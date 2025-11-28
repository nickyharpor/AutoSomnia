<?php
/**
 * Somnia Payment Gateway - Callback Controller Unit Tests
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Test\Unit\Controller\Callback;

use PHPUnit\Framework\TestCase;
use Somnia\PaymentGateway\Controller\Callback\Index;
use Somnia\PaymentGateway\Model\Gateway\Client;
use Somnia\PaymentGateway\Model\Gateway\Response\StatusResponse;
use Somnia\PaymentGateway\Model\Config;
use Somnia\PaymentGateway\Helper\Data as HelperData;
use Magento\Framework\App\Action\Context;
use Magento\Framework\App\RequestInterface;
use Magento\Framework\Controller\Result\JsonFactory;
use Magento\Framework\Controller\Result\Json;
use Magento\Sales\Api\OrderRepositoryInterface;
use Magento\Sales\Model\Order;
use Magento\Sales\Model\Order\Payment;
use Magento\Sales\Model\Order\Email\Sender\OrderSender;
use Magento\Framework\Exception\LocalizedException;
use Psr\Log\LoggerInterface;

/**
 * Unit tests for Callback Controller
 */
class IndexTest extends TestCase
{
    /**
     * @var Index
     */
    protected $controller;

    /**
     * @var Context|\PHPUnit\Framework\MockObject\MockObject
     */
    protected $contextMock;

    /**
     * @var JsonFactory|\PHPUnit\Framework\MockObject\MockObject
     */
    protected $resultJsonFactoryMock;

    /**
     * @var OrderRepositoryInterface|\PHPUnit\Framework\MockObject\MockObject
     */
    protected $orderRepositoryMock;

    /**
     * @var Client|\PHPUnit\Framework\MockObject\MockObject
     */
    protected $gatewayClientMock;

    /**
     * @var StatusResponse|\PHPUnit\Framework\MockObject\MockObject
     */
    protected $statusResponseMock;

    /**
     * @var Config|\PHPUnit\Framework\MockObject\MockObject
     */
    protected $configMock;

    /**
     * @var LoggerInterface|\PHPUnit\Framework\MockObject\MockObject
     */
    protected $loggerMock;

    /**
     * @var HelperData|\PHPUnit\Framework\MockObject\MockObject
     */
    protected $helperMock;

    /**
     * @var OrderSender|\PHPUnit\Framework\MockObject\MockObject
     */
    protected $orderSenderMock;

    /**
     * @var RequestInterface|\PHPUnit\Framework\MockObject\MockObject
     */
    protected $requestMock;

    /**
     * Set up test dependencies
     */
    protected function setUp(): void
    {
        $this->contextMock = $this->createMock(Context::class);
        $this->resultJsonFactoryMock = $this->createMock(JsonFactory::class);
        $this->orderRepositoryMock = $this->createMock(OrderRepositoryInterface::class);
        $this->gatewayClientMock = $this->createMock(Client::class);
        $this->statusResponseMock = $this->createMock(StatusResponse::class);
        $this->configMock = $this->createMock(Config::class);
        $this->loggerMock = $this->createMock(LoggerInterface::class);
        $this->helperMock = $this->createMock(HelperData::class);
        $this->orderSenderMock = $this->createMock(OrderSender::class);
        $this->requestMock = $this->createMock(RequestInterface::class);

        $this->contextMock->expects($this->any())
            ->method('getRequest')
            ->willReturn($this->requestMock);

        $this->controller = new Index(
            $this->contextMock,
            $this->resultJsonFactoryMock,
            $this->orderRepositoryMock,
            $this->gatewayClientMock,
            $this->statusResponseMock,
            $this->configMock,
            $this->loggerMock,
            $this->helperMock,
            $this->orderSenderMock
        );
    }

    /**
     * Test execute returns error when payment_id is missing
     */
    public function testExecuteReturnsErrorWhenPaymentIdMissing()
    {
        $resultJsonMock = $this->createMock(Json::class);

        $this->resultJsonFactoryMock->expects($this->once())
            ->method('create')
            ->willReturn($resultJsonMock);

        $this->requestMock->expects($this->once())
            ->method('getParam')
            ->with('payment_id')
            ->willReturn(null);

        $resultJsonMock->expects($this->once())
            ->method('setHttpResponseCode')
            ->with(400)
            ->willReturnSelf();

        $resultJsonMock->expects($this->once())
            ->method('setData')
            ->with($this->callback(function ($data) {
                return $data['success'] === false && 
                       strpos($data['message'], 'Payment ID is required') !== false;
            }))
            ->willReturnSelf();

        $this->controller->execute();
    }

    /**
     * Test execute returns error when order_id is missing
     */
    public function testExecuteReturnsErrorWhenOrderIdMissing()
    {
        $resultJsonMock = $this->createMock(Json::class);
        $paymentId = '12345678-1234-1234-1234-123456789abc';

        $this->resultJsonFactoryMock->expects($this->once())
            ->method('create')
            ->willReturn($resultJsonMock);

        $this->requestMock->expects($this->exactly(2))
            ->method('getParam')
            ->willReturnMap([
                ['payment_id', null, $paymentId],
                ['order_id', null, null]
            ]);

        $resultJsonMock->expects($this->once())
            ->method('setHttpResponseCode')
            ->with(400)
            ->willReturnSelf();

        $resultJsonMock->expects($this->once())
            ->method('setData')
            ->with($this->callback(function ($data) {
                return $data['success'] === false && 
                       strpos($data['message'], 'Order ID is required') !== false;
            }))
            ->willReturnSelf();

        $this->controller->execute();
    }

    /**
     * Test execute validates payment_id format
     */
    public function testExecuteValidatesPaymentIdFormat()
    {
        $resultJsonMock = $this->createMock(Json::class);
        $paymentId = 'invalid-payment-id';
        $orderId = '000000123';

        $this->resultJsonFactoryMock->expects($this->once())
            ->method('create')
            ->willReturn($resultJsonMock);

        $this->requestMock->expects($this->exactly(2))
            ->method('getParam')
            ->willReturnMap([
                ['payment_id', null, $paymentId],
                ['order_id', null, $orderId]
            ]);

        $this->helperMock->expects($this->exactly(2))
            ->method('sanitizeInput')
            ->willReturnArgument(0);

        $this->helperMock->expects($this->once())
            ->method('isValidUuid')
            ->with($paymentId)
            ->willReturn(false);

        $this->helperMock->expects($this->once())
            ->method('getValidationErrorMessage')
            ->with('payment_id', 'invalid')
            ->willReturn('Invalid payment ID format');

        $resultJsonMock->expects($this->once())
            ->method('setHttpResponseCode')
            ->with(400)
            ->willReturnSelf();

        $this->controller->execute();
    }

    /**
     * Test execute validates order_id format
     */
    public function testExecuteValidatesOrderIdFormat()
    {
        $resultJsonMock = $this->createMock(Json::class);
        $paymentId = '12345678-1234-1234-1234-123456789abc';
        $orderId = 'invalid<script>alert(1)</script>';

        $this->resultJsonFactoryMock->expects($this->once())
            ->method('create')
            ->willReturn($resultJsonMock);

        $this->requestMock->expects($this->exactly(2))
            ->method('getParam')
            ->willReturnMap([
                ['payment_id', null, $paymentId],
                ['order_id', null, $orderId]
            ]);

        $this->helperMock->expects($this->exactly(2))
            ->method('sanitizeInput')
            ->willReturnArgument(0);

        $this->helperMock->expects($this->once())
            ->method('isValidUuid')
            ->with($paymentId)
            ->willReturn(true);

        $this->helperMock->expects($this->once())
            ->method('validateOrderId')
            ->with($orderId)
            ->willReturn(false);

        $this->helperMock->expects($this->once())
            ->method('getValidationErrorMessage')
            ->with('order_id', 'invalid')
            ->willReturn('Invalid order ID format');

        $resultJsonMock->expects($this->once())
            ->method('setHttpResponseCode')
            ->with(400)
            ->willReturnSelf();

        $this->controller->execute();
    }

    /**
     * Test execute verifies payment status with gateway
     */
    public function testExecuteVerifiesPaymentStatusWithGateway()
    {
        $resultJsonMock = $this->createMock(Json::class);
        $paymentId = '12345678-1234-1234-1234-123456789abc';
        $orderId = '000000123';
        $storeId = 1;

        $orderMock = $this->createMock(Order::class);
        $paymentMock = $this->createMock(Payment::class);

        $this->resultJsonFactoryMock->expects($this->once())
            ->method('create')
            ->willReturn($resultJsonMock);

        $this->requestMock->expects($this->exactly(2))
            ->method('getParam')
            ->willReturnMap([
                ['payment_id', null, $paymentId],
                ['order_id', null, $orderId]
            ]);

        $this->helperMock->expects($this->exactly(2))
            ->method('sanitizeInput')
            ->willReturnArgument(0);

        $this->helperMock->expects($this->once())
            ->method('isValidUuid')
            ->willReturn(true);

        $this->helperMock->expects($this->once())
            ->method('validateOrderId')
            ->willReturn(true);

        $this->configMock->expects($this->once())
            ->method('isDebugMode')
            ->willReturn(false);

        $this->configMock->expects($this->once())
            ->method('isIpWhitelistEnabled')
            ->willReturn(false);

        // Mock order loading
        $searchCriteriaMock = $this->createMock(\Magento\Framework\Api\SearchCriteria::class);
        $searchResultsMock = $this->createMock(\Magento\Sales\Api\Data\OrderSearchResultInterface::class);

        $searchResultsMock->expects($this->once())
            ->method('getItems')
            ->willReturn([$orderMock]);

        $orderMock->expects($this->any())
            ->method('getId')
            ->willReturn(1);

        $orderMock->expects($this->any())
            ->method('getIncrementId')
            ->willReturn($orderId);

        $orderMock->expects($this->any())
            ->method('getStoreId')
            ->willReturn($storeId);

        $orderMock->expects($this->any())
            ->method('getGrandTotal')
            ->willReturn(100.00);

        $orderMock->expects($this->any())
            ->method('getState')
            ->willReturn(Order::STATE_PENDING_PAYMENT);

        $orderMock->expects($this->any())
            ->method('getPayment')
            ->willReturn($paymentMock);

        // Mock gateway status check
        $statusData = [
            'status' => 'PAID',
            'payment_id' => $paymentId,
            'order_id' => $orderId,
            'price' => 10000,
            'balance' => '100.5',
            'crypto_symbol' => 'SOMI'
        ];

        $this->gatewayClientMock->expects($this->once())
            ->method('getPaymentStatus')
            ->with($paymentId, $storeId)
            ->willReturn($statusData);

        $this->statusResponseMock->expects($this->once())
            ->method('parse')
            ->with($statusData);

        $this->statusResponseMock->expects($this->once())
            ->method('getStatus')
            ->willReturn('PAID');

        $this->statusResponseMock->expects($this->once())
            ->method('getOrderId')
            ->willReturn($orderId);

        $this->statusResponseMock->expects($this->once())
            ->method('getAmount')
            ->willReturn(100.00);

        $resultJsonMock->expects($this->once())
            ->method('setData')
            ->with($this->callback(function ($data) {
                return $data['success'] === true;
            }))
            ->willReturnSelf();

        $this->controller->execute();
    }

    /**
     * Test execute updates order status to Processing when payment is PAID
     */
    public function testExecuteUpdatesOrderStatusToProcessingWhenPaid()
    {
        $resultJsonMock = $this->createMock(Json::class);
        $paymentId = '12345678-1234-1234-1234-123456789abc';
        $orderId = '000000123';
        $storeId = 1;

        $orderMock = $this->createMock(Order::class);
        $paymentMock = $this->createMock(Payment::class);
        $orderConfigMock = $this->createMock(\Magento\Sales\Model\Order\Config::class);

        $this->resultJsonFactoryMock->expects($this->once())
            ->method('create')
            ->willReturn($resultJsonMock);

        $this->requestMock->expects($this->exactly(2))
            ->method('getParam')
            ->willReturnMap([
                ['payment_id', null, $paymentId],
                ['order_id', null, $orderId]
            ]);

        $this->helperMock->expects($this->exactly(2))
            ->method('sanitizeInput')
            ->willReturnArgument(0);

        $this->helperMock->expects($this->once())
            ->method('isValidUuid')
            ->willReturn(true);

        $this->helperMock->expects($this->once())
            ->method('validateOrderId')
            ->willReturn(true);

        $this->configMock->expects($this->any())
            ->method('isDebugMode')
            ->willReturn(false);

        $this->configMock->expects($this->once())
            ->method('isIpWhitelistEnabled')
            ->willReturn(false);

        // Mock order
        $searchResultsMock = $this->createMock(\Magento\Sales\Api\Data\OrderSearchResultInterface::class);
        $searchResultsMock->expects($this->once())
            ->method('getItems')
            ->willReturn([$orderMock]);

        $orderMock->expects($this->any())
            ->method('getId')
            ->willReturn(1);

        $orderMock->expects($this->any())
            ->method('getIncrementId')
            ->willReturn($orderId);

        $orderMock->expects($this->any())
            ->method('getStoreId')
            ->willReturn($storeId);

        $orderMock->expects($this->any())
            ->method('getGrandTotal')
            ->willReturn(100.00);

        $orderMock->expects($this->any())
            ->method('getState')
            ->willReturn(Order::STATE_PENDING_PAYMENT);

        $orderMock->expects($this->any())
            ->method('getPayment')
            ->willReturn($paymentMock);

        $orderMock->expects($this->once())
            ->method('setState')
            ->with(Order::STATE_PROCESSING);

        $orderMock->expects($this->once())
            ->method('getConfig')
            ->willReturn($orderConfigMock);

        $orderConfigMock->expects($this->once())
            ->method('getStateDefaultStatus')
            ->with(Order::STATE_PROCESSING)
            ->willReturn('processing');

        $orderMock->expects($this->once())
            ->method('setStatus')
            ->with('processing');

        $orderMock->expects($this->once())
            ->method('addCommentToStatusHistory');

        // Mock gateway status
        $statusData = [
            'status' => 'PAID',
            'payment_id' => $paymentId,
            'order_id' => $orderId,
            'price' => 10000,
            'balance' => '100.5',
            'crypto_symbol' => 'SOMI'
        ];

        $this->gatewayClientMock->expects($this->once())
            ->method('getPaymentStatus')
            ->willReturn($statusData);

        $this->statusResponseMock->expects($this->once())
            ->method('parse')
            ->with($statusData);

        $this->statusResponseMock->expects($this->once())
            ->method('getStatus')
            ->willReturn('PAID');

        $this->statusResponseMock->expects($this->once())
            ->method('getOrderId')
            ->willReturn($orderId);

        $this->statusResponseMock->expects($this->once())
            ->method('getAmount')
            ->willReturn(100.00);

        $this->statusResponseMock->expects($this->any())
            ->method('getCryptoSymbol')
            ->willReturn('SOMI');

        $this->statusResponseMock->expects($this->any())
            ->method('getCryptoAmount')
            ->willReturn('100.5');

        $this->statusResponseMock->expects($this->any())
            ->method('getWalletAddress')
            ->willReturn(null);

        $this->orderRepositoryMock->expects($this->once())
            ->method('save')
            ->with($orderMock);

        $resultJsonMock->expects($this->once())
            ->method('setData')
            ->with($this->callback(function ($data) {
                return $data['success'] === true;
            }))
            ->willReturnSelf();

        $this->controller->execute();
    }

    /**
     * Test execute throws exception when payment amount doesn't match
     */
    public function testExecuteThrowsExceptionWhenAmountMismatch()
    {
        $resultJsonMock = $this->createMock(Json::class);
        $paymentId = '12345678-1234-1234-1234-123456789abc';
        $orderId = '000000123';
        $storeId = 1;

        $orderMock = $this->createMock(Order::class);

        $this->resultJsonFactoryMock->expects($this->once())
            ->method('create')
            ->willReturn($resultJsonMock);

        $this->requestMock->expects($this->exactly(2))
            ->method('getParam')
            ->willReturnMap([
                ['payment_id', null, $paymentId],
                ['order_id', null, $orderId]
            ]);

        $this->helperMock->expects($this->exactly(2))
            ->method('sanitizeInput')
            ->willReturnArgument(0);

        $this->helperMock->expects($this->once())
            ->method('isValidUuid')
            ->willReturn(true);

        $this->helperMock->expects($this->once())
            ->method('validateOrderId')
            ->willReturn(true);

        $this->configMock->expects($this->once())
            ->method('isDebugMode')
            ->willReturn(false);

        $this->configMock->expects($this->once())
            ->method('isIpWhitelistEnabled')
            ->willReturn(false);

        // Mock order
        $searchResultsMock = $this->createMock(\Magento\Sales\Api\Data\OrderSearchResultInterface::class);
        $searchResultsMock->expects($this->once())
            ->method('getItems')
            ->willReturn([$orderMock]);

        $orderMock->expects($this->any())
            ->method('getId')
            ->willReturn(1);

        $orderMock->expects($this->any())
            ->method('getIncrementId')
            ->willReturn($orderId);

        $orderMock->expects($this->any())
            ->method('getStoreId')
            ->willReturn($storeId);

        $orderMock->expects($this->any())
            ->method('getGrandTotal')
            ->willReturn(100.00);

        // Mock gateway status with mismatched amount
        $statusData = [
            'status' => 'PAID',
            'payment_id' => $paymentId,
            'order_id' => $orderId,
            'price' => 5000, // $50 instead of $100
            'balance' => '50.0',
            'crypto_symbol' => 'SOMI'
        ];

        $this->gatewayClientMock->expects($this->once())
            ->method('getPaymentStatus')
            ->willReturn($statusData);

        $this->statusResponseMock->expects($this->once())
            ->method('parse')
            ->with($statusData);

        $this->statusResponseMock->expects($this->once())
            ->method('getOrderId')
            ->willReturn($orderId);

        $this->statusResponseMock->expects($this->once())
            ->method('getAmount')
            ->willReturn(50.00); // Mismatched amount

        $resultJsonMock->expects($this->once())
            ->method('setHttpResponseCode')
            ->with(400)
            ->willReturnSelf();

        $resultJsonMock->expects($this->once())
            ->method('setData')
            ->with($this->callback(function ($data) {
                return $data['success'] === false &&
                       strpos($data['message'], 'amount mismatch') !== false;
            }))
            ->willReturnSelf();

        $this->controller->execute();
    }
}
