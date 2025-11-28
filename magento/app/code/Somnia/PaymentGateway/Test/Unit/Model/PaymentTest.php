<?php
/**
 * Somnia Payment Gateway - Payment Method Model Unit Tests
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Test\Unit\Model;

use PHPUnit\Framework\TestCase;
use Somnia\PaymentGateway\Model\Payment;
use Somnia\PaymentGateway\Model\Config;
use Somnia\PaymentGateway\Model\Gateway\Client;
use Magento\Framework\UrlInterface;
use Magento\Checkout\Model\Session as CheckoutSession;
use Magento\Payment\Model\InfoInterface;
use Magento\Sales\Model\Order;
use Magento\Framework\Exception\LocalizedException;
use Psr\Log\LoggerInterface;

/**
 * Unit tests for Payment method model
 */
class PaymentTest extends TestCase
{
    /**
     * @var Payment
     */
    protected $payment;

    /**
     * @var Config|\PHPUnit\Framework\MockObject\MockObject
     */
    protected $configMock;

    /**
     * @var Client|\PHPUnit\Framework\MockObject\MockObject
     */
    protected $gatewayClientMock;

    /**
     * @var UrlInterface|\PHPUnit\Framework\MockObject\MockObject
     */
    protected $urlBuilderMock;

    /**
     * @var CheckoutSession|\PHPUnit\Framework\MockObject\MockObject
     */
    protected $checkoutSessionMock;

    /**
     * @var LoggerInterface|\PHPUnit\Framework\MockObject\MockObject
     */
    protected $loggerMock;

    /**
     * Set up test dependencies
     */
    protected function setUp(): void
    {
        $this->configMock = $this->createMock(Config::class);
        $this->gatewayClientMock = $this->createMock(Client::class);
        $this->urlBuilderMock = $this->createMock(UrlInterface::class);
        $this->checkoutSessionMock = $this->createMock(CheckoutSession::class);
        $this->loggerMock = $this->createMock(LoggerInterface::class);

        // Create minimal mocks for parent constructor
        $contextMock = $this->createMock(\Magento\Framework\Model\Context::class);
        $registryMock = $this->createMock(\Magento\Framework\Registry::class);
        $extensionFactoryMock = $this->createMock(\Magento\Framework\Api\ExtensionAttributesFactory::class);
        $customAttributeFactoryMock = $this->createMock(\Magento\Framework\Api\AttributeValueFactory::class);
        $paymentDataMock = $this->createMock(\Magento\Payment\Helper\Data::class);
        $scopeConfigMock = $this->createMock(\Magento\Framework\App\Config\ScopeConfigInterface::class);
        $paymentLoggerMock = $this->createMock(\Magento\Payment\Model\Method\Logger::class);

        $this->payment = new Payment(
            $contextMock,
            $registryMock,
            $extensionFactoryMock,
            $customAttributeFactoryMock,
            $paymentDataMock,
            $scopeConfigMock,
            $paymentLoggerMock,
            $this->configMock,
            $this->urlBuilderMock,
            $this->checkoutSessionMock,
            $this->gatewayClientMock,
            $this->loggerMock
        );
    }

    /**
     * Test isAvailable returns true when all conditions are met
     */
    public function testIsAvailableReturnsTrue()
    {
        $this->configMock->expects($this->once())
            ->method('isEnabled')
            ->willReturn(true);

        $this->configMock->expects($this->once())
            ->method('getGatewayUrl')
            ->willReturn('http://localhost:5000');

        $this->configMock->expects($this->once())
            ->method('getMerchantId')
            ->willReturn(1);

        $result = $this->payment->isAvailable();

        $this->assertTrue($result);
    }

    /**
     * Test isAvailable returns false when payment method is disabled
     */
    public function testIsAvailableReturnsFalseWhenDisabled()
    {
        $this->configMock->expects($this->once())
            ->method('isEnabled')
            ->willReturn(false);

        $result = $this->payment->isAvailable();

        $this->assertFalse($result);
    }

    /**
     * Test isAvailable returns false when gateway URL is empty
     */
    public function testIsAvailableReturnsFalseWhenGatewayUrlEmpty()
    {
        $this->configMock->expects($this->once())
            ->method('isEnabled')
            ->willReturn(true);

        $this->configMock->expects($this->once())
            ->method('getGatewayUrl')
            ->willReturn('');

        $result = $this->payment->isAvailable();

        $this->assertFalse($result);
    }

    /**
     * Test isAvailable returns false when merchant ID is empty
     */
    public function testIsAvailableReturnsFalseWhenMerchantIdEmpty()
    {
        $this->configMock->expects($this->once())
            ->method('isEnabled')
            ->willReturn(true);

        $this->configMock->expects($this->once())
            ->method('getGatewayUrl')
            ->willReturn('http://localhost:5000');

        $this->configMock->expects($this->once())
            ->method('getMerchantId')
            ->willReturn(null);

        $result = $this->payment->isAvailable();

        $this->assertFalse($result);
    }

    /**
     * Test authorize method with successful connection
     */
    public function testAuthorizeSuccess()
    {
        $amount = 100.00;
        $orderId = '000000123';
        $storeId = 1;

        $paymentMock = $this->createMock(InfoInterface::class);
        $orderMock = $this->createMock(Order::class);

        $orderMock->expects($this->once())
            ->method('getIncrementId')
            ->willReturn($orderId);

        $orderMock->expects($this->once())
            ->method('getStoreId')
            ->willReturn($storeId);

        $paymentMock->expects($this->once())
            ->method('getOrder')
            ->willReturn($orderMock);

        $this->gatewayClientMock->expects($this->once())
            ->method('testConnection')
            ->with(null, $storeId)
            ->willReturn(['success' => true]);

        $this->configMock->expects($this->once())
            ->method('getGatewayUrl')
            ->with($storeId)
            ->willReturn('http://localhost:5000');

        $this->configMock->expects($this->once())
            ->method('getMerchantId')
            ->with($storeId)
            ->willReturn(1);

        $this->configMock->expects($this->once())
            ->method('isDebugMode')
            ->with($storeId)
            ->willReturn(false);

        $paymentMock->expects($this->once())
            ->method('setIsTransactionPending')
            ->with(true);

        $paymentMock->expects($this->once())
            ->method('setIsTransactionClosed')
            ->with(false);

        $paymentMock->expects($this->exactly(2))
            ->method('setAdditionalInformation');

        $result = $this->payment->authorize($paymentMock, $amount);

        $this->assertSame($this->payment, $result);
    }

    /**
     * Test authorize throws exception when gateway is unavailable
     */
    public function testAuthorizeThrowsExceptionWhenGatewayUnavailable()
    {
        $this->expectException(LocalizedException::class);
        $this->expectExceptionMessage('Payment gateway is currently unavailable');

        $amount = 100.00;
        $orderId = '000000123';
        $storeId = 1;

        $paymentMock = $this->createMock(InfoInterface::class);
        $orderMock = $this->createMock(Order::class);

        $orderMock->expects($this->once())
            ->method('getIncrementId')
            ->willReturn($orderId);

        $orderMock->expects($this->once())
            ->method('getStoreId')
            ->willReturn($storeId);

        $paymentMock->expects($this->once())
            ->method('getOrder')
            ->willReturn($orderMock);

        $this->gatewayClientMock->expects($this->once())
            ->method('testConnection')
            ->with(null, $storeId)
            ->willReturn(['success' => false, 'error' => 'Connection failed']);

        $this->payment->authorize($paymentMock, $amount);
    }

    /**
     * Test getOrderPlaceRedirectUrl returns correct URL
     */
    public function testGetOrderPlaceRedirectUrl()
    {
        $expectedUrl = 'https://example.com/somnia/redirect/index';

        $this->urlBuilderMock->expects($this->once())
            ->method('getUrl')
            ->with('somnia/redirect/index', ['_secure' => true])
            ->willReturn($expectedUrl);

        $result = $this->payment->getOrderPlaceRedirectUrl();

        $this->assertEquals($expectedUrl, $result);
    }

    /**
     * Test validate throws exception when gateway URL is empty
     */
    public function testValidateThrowsExceptionWhenGatewayUrlEmpty()
    {
        $this->expectException(LocalizedException::class);
        $this->expectExceptionMessage('Gateway URL is not configured');

        $this->configMock->expects($this->once())
            ->method('getGatewayUrl')
            ->willReturn('');

        $this->payment->validate();
    }

    /**
     * Test validate throws exception when gateway URL is invalid
     */
    public function testValidateThrowsExceptionWhenGatewayUrlInvalid()
    {
        $this->expectException(LocalizedException::class);
        $this->expectExceptionMessage('Gateway URL is not valid');

        $this->configMock->expects($this->once())
            ->method('getGatewayUrl')
            ->willReturn('invalid-url');

        $this->payment->validate();
    }

    /**
     * Test validate throws exception when merchant ID is empty
     */
    public function testValidateThrowsExceptionWhenMerchantIdEmpty()
    {
        $this->expectException(LocalizedException::class);
        $this->expectExceptionMessage('Merchant ID is not configured');

        $this->configMock->expects($this->once())
            ->method('getGatewayUrl')
            ->willReturn('http://localhost:5000');

        $this->configMock->expects($this->once())
            ->method('getMerchantId')
            ->willReturn(null);

        $this->payment->validate();
    }

    /**
     * Test validate throws exception when merchant ID is not positive
     */
    public function testValidateThrowsExceptionWhenMerchantIdNotPositive()
    {
        $this->expectException(LocalizedException::class);
        $this->expectExceptionMessage('Merchant ID must be a positive integer');

        $this->configMock->expects($this->once())
            ->method('getGatewayUrl')
            ->willReturn('http://localhost:5000');

        $this->configMock->expects($this->once())
            ->method('getMerchantId')
            ->willReturn(-1);

        $this->payment->validate();
    }

    /**
     * Test validate succeeds with valid configuration
     */
    public function testValidateSucceedsWithValidConfiguration()
    {
        $this->configMock->expects($this->once())
            ->method('getGatewayUrl')
            ->willReturn('http://localhost:5000');

        $this->configMock->expects($this->once())
            ->method('getMerchantId')
            ->willReturn(1);

        $result = $this->payment->validate();

        $this->assertSame($this->payment, $result);
    }
}
