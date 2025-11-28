<?php
/**
 * Somnia Payment Gateway - Checkout Flow Integration Test
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Test\Integration;

use Magento\TestFramework\Helper\Bootstrap;
use PHPUnit\Framework\TestCase;
use Magento\Quote\Model\Quote;
use Magento\Sales\Model\Order;
use Somnia\PaymentGateway\Model\Payment;

/**
 * Integration test for complete checkout flow
 *
 * Tests Requirements: 3.1, 4.1, 4.5
 */
class CheckoutFlowTest extends TestCase
{
    /**
     * @var \Magento\Framework\ObjectManagerInterface
     */
    private $objectManager;

    /**
     * @var \Magento\Quote\Api\CartRepositoryInterface
     */
    private $quoteRepository;

    /**
     * @var \Magento\Quote\Api\CartManagementInterface
     */
    private $quoteManagement;

    /**
     * @var \Magento\Sales\Api\OrderRepositoryInterface
     */
    private $orderRepository;

    /**
     * @var \Magento\Catalog\Api\ProductRepositoryInterface
     */
    private $productRepository;

    /**
     * @var \Magento\Customer\Api\CustomerRepositoryInterface
     */
    private $customerRepository;

    /**
     * @var \Magento\Framework\App\Config\MutableScopeConfigInterface
     */
    private $scopeConfig;

    /**
     * Set up test environment
     */
    protected function setUp(): void
    {
        $this->objectManager = Bootstrap::getObjectManager();
        $this->quoteRepository = $this->objectManager->get(\Magento\Quote\Api\CartRepositoryInterface::class);
        $this->quoteManagement = $this->objectManager->get(\Magento\Quote\Api\CartManagementInterface::class);
        $this->orderRepository = $this->objectManager->get(\Magento\Sales\Api\OrderRepositoryInterface::class);
        $this->productRepository = $this->objectManager->get(\Magento\Catalog\Api\ProductRepositoryInterface::class);
        $this->customerRepository = $this->objectManager->get(\Magento\Customer\Api\CustomerRepositoryInterface::class);
        $this->scopeConfig = $this->objectManager->get(\Magento\Framework\App\Config\MutableScopeConfigInterface::class);

        // Configure payment method
        $this->configurePaymentMethod();
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
    }

    /**
     * Test that payment method is available during checkout
     *
     * Requirement 3.1: Payment method should be displayed when enabled
     */
    public function testPaymentMethodIsAvailableDuringCheckout()
    {
        // Create a quote
        $quote = $this->createQuote();

        // Get payment method
        $payment = $this->objectManager->create(Payment::class);

        // Test availability
        $this->assertTrue(
            $payment->isAvailable($quote),
            'Payment method should be available when properly configured'
        );
    }

    /**
     * Test that payment method is not available when disabled
     *
     * Requirement 3.1: Payment method should not appear when disabled
     */
    public function testPaymentMethodNotAvailableWhenDisabled()
    {
        // Disable payment method
        $this->scopeConfig->setValue(
            'payment/somnia_gateway/active',
            0,
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );

        // Create a quote
        $quote = $this->createQuote();

        // Get payment method
        $payment = $this->objectManager->create(Payment::class);

        // Test availability
        $this->assertFalse(
            $payment->isAvailable($quote),
            'Payment method should not be available when disabled'
        );

        // Re-enable for other tests
        $this->scopeConfig->setValue(
            'payment/somnia_gateway/active',
            1,
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
    }

    /**
     * Test order placement with cryptocurrency payment
     *
     * Requirement 4.1: Order should be created with pending payment status
     */
    public function testOrderPlacementWithCryptocurrencyPayment()
    {
        // Create a quote with items
        $quote = $this->createQuoteWithProduct();

        // Set payment method
        $quote->getPayment()->setMethod(Payment::CODE);
        $quote->setIsActive(true);
        $this->quoteRepository->save($quote);

        // Place order
        $orderId = $this->quoteManagement->placeOrder($quote->getId());

        // Load order
        $order = $this->orderRepository->get($orderId);

        // Verify order was created
        $this->assertNotNull($order->getId(), 'Order should be created');
        $this->assertEquals(Payment::CODE, $order->getPayment()->getMethod(), 'Payment method should be somnia_gateway');
        $this->assertEquals(Order::STATE_NEW, $order->getState(), 'Order state should be new');
        $this->assertEquals('pending_payment', $order->getStatus(), 'Order status should be pending_payment');
    }

    /**
     * Test redirect URL generation
     *
     * Requirement 4.5: Should generate redirect URL to gateway
     */
    public function testRedirectUrlGeneration()
    {
        // Get payment method
        $payment = $this->objectManager->create(Payment::class);

        // Get redirect URL
        $redirectUrl = $payment->getOrderPlaceRedirectUrl();

        // Verify redirect URL
        $this->assertNotEmpty($redirectUrl, 'Redirect URL should not be empty');
        $this->assertStringContainsString('somnia/redirect/index', $redirectUrl, 'Redirect URL should contain correct route');
    }

    /**
     * Test order status after placement
     *
     * Requirement 4.1: Order status should be pending payment after placement
     */
    public function testOrderStatusAfterPlacement()
    {
        // Create a quote with items
        $quote = $this->createQuoteWithProduct();

        // Set payment method
        $quote->getPayment()->setMethod(Payment::CODE);
        $quote->setIsActive(true);
        $this->quoteRepository->save($quote);

        // Place order
        $orderId = $this->quoteManagement->placeOrder($quote->getId());

        // Load order
        $order = $this->orderRepository->get($orderId);

        // Verify order status
        $this->assertEquals('pending_payment', $order->getStatus(), 'Order status should be pending_payment');
        $this->assertFalse($order->canInvoice(), 'Order should not be invoiceable yet');
        $this->assertFalse($order->canShip(), 'Order should not be shippable yet');
    }

    /**
     * Test payment information is stored in order
     *
     * Requirement 4.1: Payment information should be stored
     */
    public function testPaymentInformationStoredInOrder()
    {
        // Create a quote with items
        $quote = $this->createQuoteWithProduct();

        // Set payment method
        $quote->getPayment()->setMethod(Payment::CODE);
        $quote->setIsActive(true);
        $this->quoteRepository->save($quote);

        // Place order
        $orderId = $this->quoteManagement->placeOrder($quote->getId());

        // Load order
        $order = $this->orderRepository->get($orderId);
        $payment = $order->getPayment();

        // Verify payment information
        $additionalInfo = $payment->getAdditionalInformation();
        $this->assertArrayHasKey('somnia_gateway_url', $additionalInfo, 'Gateway URL should be stored');
        $this->assertArrayHasKey('somnia_merchant_id', $additionalInfo, 'Merchant ID should be stored');
        $this->assertEquals('http://localhost:5000', $additionalInfo['somnia_gateway_url']);
        $this->assertEquals(1, $additionalInfo['somnia_merchant_id']);
    }

    /**
     * Create a basic quote
     *
     * @return Quote
     */
    private function createQuote()
    {
        /** @var Quote $quote */
        $quote = $this->objectManager->create(Quote::class);
        $quote->setStoreId(1);
        $quote->setIsActive(true);
        $quote->setIsMultiShipping(false);
        $quote->setReservedOrderId('test_order_' . uniqid());

        // Set customer email
        $quote->setCustomerEmail('test@example.com');
        $quote->setCustomerIsGuest(true);

        // Set billing address
        $billingAddress = $this->objectManager->create(\Magento\Quote\Model\Quote\Address::class);
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
        $quote->setBillingAddress($billingAddress);

        // Set shipping address
        $shippingAddress = $this->objectManager->create(\Magento\Quote\Model\Quote\Address::class);
        $shippingAddress->setData([
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
        $quote->setShippingAddress($shippingAddress);

        return $quote;
    }

    /**
     * Create a quote with a product
     *
     * @return Quote
     */
    private function createQuoteWithProduct()
    {
        $quote = $this->createQuote();

        // Create a simple product
        $product = $this->objectManager->create(\Magento\Catalog\Model\Product::class);
        $product->setTypeId(\Magento\Catalog\Model\Product\Type::TYPE_SIMPLE)
            ->setAttributeSetId(4)
            ->setWebsiteIds([1])
            ->setName('Test Product')
            ->setSku('test-product-' . uniqid())
            ->setPrice(10.00)
            ->setVisibility(\Magento\Catalog\Model\Product\Visibility::VISIBILITY_BOTH)
            ->setStatus(\Magento\Catalog\Model\Product\Attribute\Source\Status::STATUS_ENABLED)
            ->setStockData([
                'use_config_manage_stock' => 1,
                'qty' => 100,
                'is_in_stock' => 1
            ]);

        $this->productRepository->save($product);

        // Add product to quote
        $quote->addProduct($product, 1);

        // Set shipping method
        $shippingAddress = $quote->getShippingAddress();
        $shippingAddress->setCollectShippingRates(true)
            ->collectShippingRates()
            ->setShippingMethod('flatrate_flatrate');

        $quote->collectTotals();
        $this->quoteRepository->save($quote);

        return $quote;
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
    }
}
