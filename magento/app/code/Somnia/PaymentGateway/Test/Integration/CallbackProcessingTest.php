<?php
/**
 * Somnia Payment Gateway - Callback Processing Integration Test
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Test\Integration;

use Magento\TestFramework\Helper\Bootstrap;
use PHPUnit\Framework\TestCase;
use Magento\Sales\Model\Order;
use Somnia\PaymentGateway\Model\Payment;
use Somnia\PaymentGateway\Controller\Callback\Index as CallbackController;

/**
 * Integration test for callback processing
 *
 * Tests Requirements: 5.1, 5.3, 5.4
 */
class CallbackProcessingTest extends TestCase
{
    /**
     * @var \Magento\Framework\ObjectManagerInterface
     */
    private $objectManager;

    /**
     * @var \Magento\Sales\Api\OrderRepositoryInterface
     */
    private $orderRepository;

    /**
     * @var \Magento\Framework\App\Config\MutableScopeConfigInterface
     */
    private $scopeConfig;

    /**
     * @var \Magento\Framework\App\RequestInterface
     */
    private $request;

    /**
     * @var CallbackController
     */
    private $callbackController;

    /**
     * Set up test environment
     */
    protected function setUp(): void
    {
        $this->objectManager = Bootstrap::getObjectManager();
        $this->orderRepository = $this->objectManager->get(\Magento\Sales\Api\OrderRepositoryInterface::class);
        $this->scopeConfig = $this->objectManager->get(\Magento\Framework\App\Config\MutableScopeConfigInterface::class);
        $this->request = $this->objectManager->get(\Magento\Framework\App\RequestInterface::class);

        // Configure payment method
        $this->configurePaymentMethod();

        // Create callback controller
        $this->callbackController = $this->objectManager->create(CallbackController::class);
    }

    /**
     * Configure payment method for testing
     */
    private function configurePaymentMethod()
    {
        $this->scopeConfig->setValue(
            'payment/somnia_gateway/active',
            1,
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->scopeConfig->setValue(
            'payment/somnia_gateway/gateway_url',
            'http://localhost:5000',
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->scopeConfig->setValue(
            'payment/somnia_gateway/merchant_id',
            1,
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->scopeConfig->setValue(
            'payment/somnia_gateway/debug',
            1,
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
    }

    /**
     * Test callback endpoint with valid payment
     *
     * Requirement 5.1: Callback endpoint should process valid payments
     */
    public function testCallbackEndpointWithValidPayment()
    {
        // Create an order
        $order = $this->createTestOrder();

        // Mock gateway client to return successful payment status
        $gatewayClient = $this->createMockGatewayClient([
            'status' => 'PAID',
            'order_id' => $order->getIncrementId(),
            'amount' => $order->getGrandTotal(),
            'crypto_symbol' => 'SOMI',
            'crypto_amount' => '100.5',
            'wallet_address' => '0x1234567890abcdef'
        ]);

        // Set request parameters
        $this->request->setParams([
            'payment_id' => 'test-payment-123',
            'order_id' => $order->getIncrementId()
        ]);

        // Execute callback
        $result = $this->callbackController->execute();

        // Verify response
        $this->assertInstanceOf(\Magento\Framework\Controller\Result\Json::class, $result);

        // Reload order
        $order = $this->orderRepository->get($order->getId());

        // Verify order status updated
        $this->assertEquals(Order::STATE_PROCESSING, $order->getState(), 'Order should be in processing state');
    }

    /**
     * Test callback endpoint with failed payment
     *
     * Requirement 5.3: Callback should handle failed payments
     */
    public function testCallbackEndpointWithFailedPayment()
    {
        // Create an order
        $order = $this->createTestOrder();

        // Mock gateway client to return failed payment status
        $gatewayClient = $this->createMockGatewayClient([
            'status' => 'FAILED',
            'order_id' => $order->getIncrementId(),
            'amount' => $order->getGrandTotal()
        ]);

        // Set request parameters
        $this->request->setParams([
            'payment_id' => 'test-payment-456',
            'order_id' => $order->getIncrementId()
        ]);

        // Execute callback
        $result = $this->callbackController->execute();

        // Reload order
        $order = $this->orderRepository->get($order->getId());

        // Verify order status updated to canceled
        $this->assertEquals(Order::STATE_CANCELED, $order->getState(), 'Order should be canceled for failed payment');
    }

    /**
     * Test callback endpoint with expired payment
     *
     * Requirement 5.3: Callback should handle expired payments
     */
    public function testCallbackEndpointWithExpiredPayment()
    {
        // Create an order
        $order = $this->createTestOrder();

        // Mock gateway client to return expired payment status
        $gatewayClient = $this->createMockGatewayClient([
            'status' => 'EXPIRED',
            'order_id' => $order->getIncrementId(),
            'amount' => $order->getGrandTotal()
        ]);

        // Set request parameters
        $this->request->setParams([
            'payment_id' => 'test-payment-789',
            'order_id' => $order->getIncrementId()
        ]);

        // Execute callback
        $result = $this->callbackController->execute();

        // Reload order
        $order = $this->orderRepository->get($order->getId());

        // Verify order status updated to canceled
        $this->assertEquals(Order::STATE_CANCELED, $order->getState(), 'Order should be canceled for expired payment');
    }

    /**
     * Test order status updates
     *
     * Requirement 5.4: Order status should be updated based on payment status
     */
    public function testOrderStatusUpdates()
    {
        // Create an order
        $order = $this->createTestOrder();
        $initialStatus = $order->getStatus();

        // Mock gateway client to return successful payment
        $gatewayClient = $this->createMockGatewayClient([
            'status' => 'PAID',
            'order_id' => $order->getIncrementId(),
            'amount' => $order->getGrandTotal(),
            'crypto_symbol' => 'SOMI',
            'crypto_amount' => '100.5'
        ]);

        // Set request parameters
        $this->request->setParams([
            'payment_id' => 'test-payment-update',
            'order_id' => $order->getIncrementId()
        ]);

        // Execute callback
        $this->callbackController->execute();

        // Reload order
        $order = $this->orderRepository->get($order->getId());

        // Verify status changed
        $this->assertNotEquals($initialStatus, $order->getStatus(), 'Order status should have changed');
        $this->assertEquals('processing', $order->getStatus(), 'Order status should be processing');
    }

    /**
     * Test payment information is stored in order
     *
     * Requirement 5.4: Payment details should be stored in order
     */
    public function testPaymentInformationStoredAfterCallback()
    {
        // Create an order
        $order = $this->createTestOrder();

        // Mock gateway client
        $gatewayClient = $this->createMockGatewayClient([
            'status' => 'PAID',
            'order_id' => $order->getIncrementId(),
            'amount' => $order->getGrandTotal(),
            'crypto_symbol' => 'SOMI',
            'crypto_amount' => '100.5',
            'wallet_address' => '0xabcdef1234567890'
        ]);

        // Set request parameters
        $this->request->setParams([
            'payment_id' => 'test-payment-info',
            'order_id' => $order->getIncrementId()
        ]);

        // Execute callback
        $this->callbackController->execute();

        // Reload order
        $order = $this->orderRepository->get($order->getId());
        $payment = $order->getPayment();
        $additionalInfo = $payment->getAdditionalInformation();

        // Verify payment information stored
        $this->assertArrayHasKey('somnia_payment_id', $additionalInfo, 'Payment ID should be stored');
        $this->assertArrayHasKey('somnia_payment_status', $additionalInfo, 'Payment status should be stored');
        $this->assertArrayHasKey('somnia_crypto_symbol', $additionalInfo, 'Crypto symbol should be stored');
        $this->assertArrayHasKey('somnia_crypto_amount', $additionalInfo, 'Crypto amount should be stored');
        $this->assertEquals('test-payment-info', $additionalInfo['somnia_payment_id']);
        $this->assertEquals('PAID', $additionalInfo['somnia_payment_status']);
    }

    /**
     * Test callback with missing payment_id parameter
     *
     * Requirement 5.1: Callback should validate required parameters
     */
    public function testCallbackWithMissingPaymentId()
    {
        // Create an order
        $order = $this->createTestOrder();

        // Set request parameters without payment_id
        $this->request->setParams([
            'order_id' => $order->getIncrementId()
        ]);

        // Execute callback
        $result = $this->callbackController->execute();

        // Verify error response
        $this->assertInstanceOf(\Magento\Framework\Controller\Result\Json::class, $result);
        
        // Order should remain unchanged
        $order = $this->orderRepository->get($order->getId());
        $this->assertEquals(Order::STATE_NEW, $order->getState());
    }

    /**
     * Test callback with missing order_id parameter
     *
     * Requirement 5.1: Callback should validate required parameters
     */
    public function testCallbackWithMissingOrderId()
    {
        // Set request parameters without order_id
        $this->request->setParams([
            'payment_id' => 'test-payment-missing-order'
        ]);

        // Execute callback
        $result = $this->callbackController->execute();

        // Verify error response
        $this->assertInstanceOf(\Magento\Framework\Controller\Result\Json::class, $result);
    }

    /**
     * Test callback with invalid order_id
     *
     * Requirement 5.1: Callback should handle invalid order IDs
     */
    public function testCallbackWithInvalidOrderId()
    {
        // Set request parameters with non-existent order
        $this->request->setParams([
            'payment_id' => 'test-payment-invalid',
            'order_id' => 'non-existent-order-999'
        ]);

        // Execute callback
        $result = $this->callbackController->execute();

        // Verify error response
        $this->assertInstanceOf(\Magento\Framework\Controller\Result\Json::class, $result);
    }

    /**
     * Test order comment is added after successful payment
     *
     * Requirement 5.4: Order comments should include payment details
     */
    public function testOrderCommentAddedAfterPayment()
    {
        // Create an order
        $order = $this->createTestOrder();
        $initialCommentCount = count($order->getStatusHistories());

        // Mock gateway client
        $gatewayClient = $this->createMockGatewayClient([
            'status' => 'PAID',
            'order_id' => $order->getIncrementId(),
            'amount' => $order->getGrandTotal(),
            'crypto_symbol' => 'SOMI',
            'crypto_amount' => '100.5'
        ]);

        // Set request parameters
        $this->request->setParams([
            'payment_id' => 'test-payment-comment',
            'order_id' => $order->getIncrementId()
        ]);

        // Execute callback
        $this->callbackController->execute();

        // Reload order
        $order = $this->orderRepository->get($order->getId());
        $comments = $order->getStatusHistories();

        // Verify comment was added
        $this->assertGreaterThan($initialCommentCount, count($comments), 'Order comment should be added');
        
        // Find the payment comment
        $paymentComment = null;
        foreach ($comments as $comment) {
            if (strpos($comment->getComment(), 'Cryptocurrency payment') !== false) {
                $paymentComment = $comment->getComment();
                break;
            }
        }
        
        $this->assertNotNull($paymentComment, 'Payment comment should exist');
        $this->assertStringContainsString('test-payment-comment', $paymentComment, 'Comment should contain payment ID');
    }

    /**
     * Create a test order
     *
     * @return Order
     */
    private function createTestOrder()
    {
        /** @var Order $order */
        $order = $this->objectManager->create(Order::class);
        
        // Set order data
        $order->setIncrementId('test_order_' . uniqid());
        $order->setState(Order::STATE_NEW);
        $order->setStatus('pending_payment');
        $order->setCustomerEmail('test@example.com');
        $order->setCustomerIsGuest(true);
        $order->setStoreId(1);
        $order->setGrandTotal(10.00);
        $order->setBaseGrandTotal(10.00);

        // Set billing address
        $billingAddress = $this->objectManager->create(\Magento\Sales\Model\Order\Address::class);
        $billingAddress->setData([
            'firstname' => 'Test',
            'lastname' => 'Customer',
            'street' => '123 Test St',
            'city' => 'Test City',
            'region' => 'CA',
            'postcode' => '12345',
            'country_id' => 'US',
            'telephone' => '555-1234',
            'email' => 'test@example.com'
        ]);
        $order->setBillingAddress($billingAddress);

        // Set payment
        $payment = $this->objectManager->create(\Magento\Sales\Model\Order\Payment::class);
        $payment->setMethod(Payment::CODE);
        $order->setPayment($payment);

        // Save order
        $this->orderRepository->save($order);

        return $order;
    }

    /**
     * Create a mock gateway client
     *
     * @param array $statusResponse
     * @return mixed
     */
    private function createMockGatewayClient(array $statusResponse)
    {
        $gatewayClient = $this->getMockBuilder(\Somnia\PaymentGateway\Model\Gateway\Client::class)
            ->disableOriginalConstructor()
            ->getMock();

        $gatewayClient->method('getPaymentStatus')
            ->willReturn($statusResponse);

        // Replace the gateway client in object manager
        $this->objectManager->addSharedInstance($gatewayClient, \Somnia\PaymentGateway\Model\Gateway\Client::class);

        return $gatewayClient;
    }

    /**
     * Clean up after tests
     */
    protected function tearDown(): void
    {
        // Reset configuration
        $this->scopeConfig->setValue(
            'payment/somnia_gateway/active',
            0,
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );

        // Clear shared instances
        $this->objectManager->removeSharedInstance(\Somnia\PaymentGateway\Model\Gateway\Client::class);
    }
}
