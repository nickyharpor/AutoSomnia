<?php
/**
 * Somnia Payment Gateway - Gateway Client Unit Tests
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Test\Unit\Model\Gateway;

use PHPUnit\Framework\TestCase;
use Somnia\PaymentGateway\Model\Gateway\Client;
use Somnia\PaymentGateway\Model\Config;
use Magento\Framework\HTTP\Client\Curl;
use Magento\Framework\Exception\LocalizedException;
use Psr\Log\LoggerInterface;

/**
 * Unit tests for Gateway Client
 */
class ClientTest extends TestCase
{
    /**
     * @var Client
     */
    protected $client;

    /**
     * @var Config|\PHPUnit\Framework\MockObject\MockObject
     */
    protected $configMock;

    /**
     * @var Curl|\PHPUnit\Framework\MockObject\MockObject
     */
    protected $curlMock;

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
        $this->curlMock = $this->createMock(Curl::class);
        $this->loggerMock = $this->createMock(LoggerInterface::class);

        $this->client = new Client(
            $this->configMock,
            $this->curlMock,
            $this->loggerMock
        );
    }

    /**
     * Test buildPaymentUrl with valid parameters
     */
    public function testBuildPaymentUrlSuccess()
    {
        $orderId = '000000123';
        $amount = 10.50;
        $storeId = 1;
        $gatewayUrl = 'http://localhost:5000';
        $merchantId = 1;

        $this->configMock->expects($this->once())
            ->method('getGatewayUrl')
            ->with($storeId)
            ->willReturn($gatewayUrl);

        $this->configMock->expects($this->once())
            ->method('getMerchantId')
            ->with($storeId)
            ->willReturn($merchantId);

        $this->configMock->expects($this->once())
            ->method('shouldEnforceHttps')
            ->with($storeId)
            ->willReturn(false);

        $this->configMock->expects($this->once())
            ->method('isDebugMode')
            ->with($storeId)
            ->willReturn(false);

        $result = $this->client->buildPaymentUrl($orderId, $amount, $storeId);

        $this->assertStringContainsString('/pay?', $result);
        $this->assertStringContainsString('price=1050', $result);
        $this->assertStringContainsString('merchant=1', $result);
        $this->assertStringContainsString('order_id=000000123', $result);
    }

    /**
     * Test buildPaymentUrl converts amount to cents correctly
     */
    public function testBuildPaymentUrlConvertsToCents()
    {
        $orderId = '000000123';
        $amount = 99.99;
        $storeId = 1;

        $this->configMock->expects($this->once())
            ->method('getGatewayUrl')
            ->with($storeId)
            ->willReturn('http://localhost:5000');

        $this->configMock->expects($this->once())
            ->method('getMerchantId')
            ->with($storeId)
            ->willReturn(1);

        $this->configMock->expects($this->once())
            ->method('shouldEnforceHttps')
            ->with($storeId)
            ->willReturn(false);

        $this->configMock->expects($this->once())
            ->method('isDebugMode')
            ->with($storeId)
            ->willReturn(false);

        $result = $this->client->buildPaymentUrl($orderId, $amount, $storeId);

        $this->assertStringContainsString('price=9999', $result);
    }

    /**
     * Test buildPaymentUrl throws exception when gateway URL is empty
     */
    public function testBuildPaymentUrlThrowsExceptionWhenGatewayUrlEmpty()
    {
        $this->expectException(LocalizedException::class);
        $this->expectExceptionMessage('Gateway URL is not configured');

        $this->configMock->expects($this->once())
            ->method('getGatewayUrl')
            ->willReturn('');

        $this->client->buildPaymentUrl('000000123', 10.00);
    }

    /**
     * Test buildPaymentUrl throws exception when merchant ID is empty
     */
    public function testBuildPaymentUrlThrowsExceptionWhenMerchantIdEmpty()
    {
        $this->expectException(LocalizedException::class);
        $this->expectExceptionMessage('Merchant ID is not configured');

        $this->configMock->expects($this->once())
            ->method('getGatewayUrl')
            ->willReturn('http://localhost:5000');

        $this->configMock->expects($this->once())
            ->method('getMerchantId')
            ->willReturn(null);

        $this->client->buildPaymentUrl('000000123', 10.00);
    }

    /**
     * Test buildPaymentUrl throws exception when HTTPS is required but not used
     */
    public function testBuildPaymentUrlThrowsExceptionWhenHttpsRequired()
    {
        $this->expectException(LocalizedException::class);
        $this->expectExceptionMessage('Gateway URL must use HTTPS in production mode');

        $this->configMock->expects($this->once())
            ->method('getGatewayUrl')
            ->willReturn('http://example.com');

        $this->configMock->expects($this->once())
            ->method('getMerchantId')
            ->willReturn(1);

        $this->configMock->expects($this->once())
            ->method('shouldEnforceHttps')
            ->willReturn(true);

        $this->configMock->expects($this->once())
            ->method('isSecureConnection')
            ->willReturn(false);

        $this->client->buildPaymentUrl('000000123', 10.00);
    }

    /**
     * Test getPaymentStatus with successful response
     */
    public function testGetPaymentStatusSuccess()
    {
        $paymentId = '12345678-1234-1234-1234-123456789abc';
        $storeId = 1;
        $gatewayUrl = 'http://localhost:5000';
        $responseData = [
            'status' => 'PAID',
            'payment_id' => $paymentId,
            'balance' => '100.5',
            'crypto_symbol' => 'SOMI'
        ];

        $this->configMock->expects($this->once())
            ->method('getGatewayUrl')
            ->with($storeId)
            ->willReturn($gatewayUrl);

        $this->configMock->expects($this->exactly(2))
            ->method('isDebugMode')
            ->with($storeId)
            ->willReturn(false);

        $this->curlMock->expects($this->once())
            ->method('setTimeout')
            ->with(30);

        $this->curlMock->expects($this->exactly(2))
            ->method('setOption');

        $this->curlMock->expects($this->once())
            ->method('get')
            ->with($gatewayUrl . '/status/' . $paymentId);

        $this->curlMock->expects($this->once())
            ->method('getStatus')
            ->willReturn(200);

        $this->curlMock->expects($this->once())
            ->method('getBody')
            ->willReturn(json_encode($responseData));

        $result = $this->client->getPaymentStatus($paymentId, $storeId);

        $this->assertEquals($responseData, $result);
    }

    /**
     * Test getPaymentStatus throws exception when payment ID is empty
     */
    public function testGetPaymentStatusThrowsExceptionWhenPaymentIdEmpty()
    {
        $this->expectException(LocalizedException::class);
        $this->expectExceptionMessage('Payment ID is required');

        $this->client->getPaymentStatus('');
    }

    /**
     * Test getPaymentStatus throws exception on non-200 status code
     */
    public function testGetPaymentStatusThrowsExceptionOnErrorStatus()
    {
        $this->expectException(LocalizedException::class);
        $this->expectExceptionMessage('Gateway returned error status: 404');

        $paymentId = '12345678-1234-1234-1234-123456789abc';
        $storeId = 1;

        $this->configMock->expects($this->once())
            ->method('getGatewayUrl')
            ->with($storeId)
            ->willReturn('http://localhost:5000');

        $this->configMock->expects($this->once())
            ->method('isDebugMode')
            ->with($storeId)
            ->willReturn(false);

        $this->curlMock->expects($this->once())
            ->method('getStatus')
            ->willReturn(404);

        $this->curlMock->expects($this->once())
            ->method('getBody')
            ->willReturn('Not found');

        $this->client->getPaymentStatus($paymentId, $storeId);
    }

    /**
     * Test getPaymentStatus throws exception on invalid JSON
     */
    public function testGetPaymentStatusThrowsExceptionOnInvalidJson()
    {
        $this->expectException(LocalizedException::class);
        $this->expectExceptionMessage('Invalid JSON response from gateway');

        $paymentId = '12345678-1234-1234-1234-123456789abc';
        $storeId = 1;

        $this->configMock->expects($this->once())
            ->method('getGatewayUrl')
            ->with($storeId)
            ->willReturn('http://localhost:5000');

        $this->configMock->expects($this->once())
            ->method('isDebugMode')
            ->with($storeId)
            ->willReturn(false);

        $this->curlMock->expects($this->once())
            ->method('getStatus')
            ->willReturn(200);

        $this->curlMock->expects($this->once())
            ->method('getBody')
            ->willReturn('invalid json');

        $this->client->getPaymentStatus($paymentId, $storeId);
    }

    /**
     * Test testConnection with successful health check
     */
    public function testTestConnectionSuccess()
    {
        $storeId = 1;
        $gatewayUrl = 'http://localhost:5000';
        $healthResponse = ['status' => 'healthy'];

        $this->configMock->expects($this->once())
            ->method('getGatewayUrl')
            ->with($storeId)
            ->willReturn($gatewayUrl);

        $this->configMock->expects($this->once())
            ->method('isDebugMode')
            ->with($storeId)
            ->willReturn(false);

        $this->curlMock->expects($this->once())
            ->method('setTimeout')
            ->with(30);

        $this->curlMock->expects($this->exactly(2))
            ->method('setOption');

        $this->curlMock->expects($this->once())
            ->method('get')
            ->with($gatewayUrl . '/health');

        $this->curlMock->expects($this->once())
            ->method('getStatus')
            ->willReturn(200);

        $this->curlMock->expects($this->once())
            ->method('getBody')
            ->willReturn(json_encode($healthResponse));

        $result = $this->client->testConnection(null, $storeId);

        $this->assertTrue($result['success']);
        $this->assertEquals('healthy', $result['status']);
    }

    /**
     * Test testConnection with custom gateway URL
     */
    public function testTestConnectionWithCustomUrl()
    {
        $customUrl = 'http://custom-gateway.com';
        $healthResponse = ['status' => 'healthy'];

        $this->curlMock->expects($this->once())
            ->method('setTimeout')
            ->with(30);

        $this->curlMock->expects($this->exactly(2))
            ->method('setOption');

        $this->curlMock->expects($this->once())
            ->method('get')
            ->with($customUrl . '/health');

        $this->curlMock->expects($this->once())
            ->method('getStatus')
            ->willReturn(200);

        $this->curlMock->expects($this->once())
            ->method('getBody')
            ->willReturn(json_encode($healthResponse));

        $result = $this->client->testConnection($customUrl);

        $this->assertTrue($result['success']);
    }

    /**
     * Test testConnection returns error on non-200 status
     */
    public function testTestConnectionReturnsErrorOnNon200Status()
    {
        $storeId = 1;

        $this->configMock->expects($this->once())
            ->method('getGatewayUrl')
            ->with($storeId)
            ->willReturn('http://localhost:5000');

        $this->configMock->expects($this->once())
            ->method('isDebugMode')
            ->with($storeId)
            ->willReturn(false);

        $this->curlMock->expects($this->once())
            ->method('getStatus')
            ->willReturn(500);

        $result = $this->client->testConnection(null, $storeId);

        $this->assertFalse($result['success']);
        $this->assertStringContainsString('status: 500', $result['error']);
    }

    /**
     * Test testConnection returns error on invalid JSON
     */
    public function testTestConnectionReturnsErrorOnInvalidJson()
    {
        $storeId = 1;

        $this->configMock->expects($this->once())
            ->method('getGatewayUrl')
            ->with($storeId)
            ->willReturn('http://localhost:5000');

        $this->configMock->expects($this->once())
            ->method('isDebugMode')
            ->with($storeId)
            ->willReturn(false);

        $this->curlMock->expects($this->once())
            ->method('getStatus')
            ->willReturn(200);

        $this->curlMock->expects($this->once())
            ->method('getBody')
            ->willReturn('invalid json');

        $result = $this->client->testConnection(null, $storeId);

        $this->assertFalse($result['success']);
        $this->assertStringContainsString('Invalid JSON', $result['error']);
    }

    /**
     * Test testConnection returns error when gateway is not healthy
     */
    public function testTestConnectionReturnsErrorWhenNotHealthy()
    {
        $storeId = 1;
        $healthResponse = ['status' => 'unhealthy'];

        $this->configMock->expects($this->once())
            ->method('getGatewayUrl')
            ->with($storeId)
            ->willReturn('http://localhost:5000');

        $this->configMock->expects($this->once())
            ->method('isDebugMode')
            ->with($storeId)
            ->willReturn(false);

        $this->curlMock->expects($this->once())
            ->method('getStatus')
            ->willReturn(200);

        $this->curlMock->expects($this->once())
            ->method('getBody')
            ->willReturn(json_encode($healthResponse));

        $result = $this->client->testConnection(null, $storeId);

        $this->assertFalse($result['success']);
        $this->assertEquals('Gateway is not healthy', $result['error']);
    }

    /**
     * Test testConnection handles connection exceptions
     */
    public function testTestConnectionHandlesExceptions()
    {
        $storeId = 1;

        $this->configMock->expects($this->once())
            ->method('getGatewayUrl')
            ->with($storeId)
            ->willReturn('http://localhost:5000');

        $this->configMock->expects($this->once())
            ->method('isDebugMode')
            ->with($storeId)
            ->willReturn(false);

        $this->curlMock->expects($this->once())
            ->method('get')
            ->willThrowException(new \Exception('Connection timeout'));

        $result = $this->client->testConnection(null, $storeId);

        $this->assertFalse($result['success']);
        $this->assertEquals('Connection timeout', $result['error']);
    }
}
