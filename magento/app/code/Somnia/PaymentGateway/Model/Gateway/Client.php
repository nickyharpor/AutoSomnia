<?php
/**
 * Somnia Payment Gateway - HTTP Client
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Model\Gateway;

use Somnia\PaymentGateway\Model\Config;
use Magento\Framework\HTTP\Client\Curl;
use Magento\Framework\Exception\LocalizedException;
use Psr\Log\LoggerInterface;

/**
 * Gateway HTTP client for communication with payment gateway
 */
class Client
{
    /**
     * HTTP timeout in seconds
     */
    const HTTP_TIMEOUT = 30;

    /**
     * @var Config
     */
    protected $config;

    /**
     * @var Curl
     */
    protected $curl;

    /**
     * @var LoggerInterface
     */
    protected $logger;

    /**
     * @param Config $config
     * @param Curl $curl
     * @param LoggerInterface $logger
     */
    public function __construct(
        Config $config,
        Curl $curl,
        LoggerInterface $logger
    ) {
        $this->config = $config;
        $this->curl = $curl;
        $this->logger = $logger;
    }

    /**
     * Build payment initiation URL
     *
     * @param string $orderId Magento order ID
     * @param float $amount Order total amount in dollars
     * @param int|null $storeId Store ID
     * @return string Payment URL
     * @throws LocalizedException
     */
    public function buildPaymentUrl($orderId, $amount, $storeId = null)
    {
        try {
            $gatewayUrl = $this->config->getGatewayUrl($storeId);
            $merchantId = $this->config->getMerchantId($storeId);

            if (empty($gatewayUrl)) {
                $this->logger->error('Somnia Payment Gateway: Gateway URL is not configured', [
                    'order_id' => $orderId
                ]);
                throw new LocalizedException(__('Gateway URL is not configured'));
            }

            if (empty($merchantId)) {
                $this->logger->error('Somnia Payment Gateway: Merchant ID is not configured', [
                    'order_id' => $orderId
                ]);
                throw new LocalizedException(__('Merchant ID is not configured'));
            }

            // Validate HTTPS in production mode
            if ($this->config->shouldEnforceHttps($storeId) && !$this->config->isSecureConnection($storeId)) {
                $this->logger->error('Somnia Payment Gateway: HTTPS required in production mode', [
                    'order_id' => $orderId,
                    'gateway_url' => $gatewayUrl
                ]);
                throw new LocalizedException(
                    __('Gateway URL must use HTTPS in production mode. Please update your configuration.')
                );
            }

            // Convert amount to cents
            $priceInCents = (int)round($amount * 100);

            // Build query parameters
            $params = [
                'price' => $priceInCents,
                'merchant' => $merchantId,
                'order_id' => $orderId
            ];

            $paymentUrl = $gatewayUrl . '/pay?' . http_build_query($params);

            if ($this->config->isDebugMode($storeId)) {
                $this->logger->info('Somnia Payment Gateway: Payment URL built', [
                    'order_id' => $orderId,
                    'amount' => $amount,
                    'price_cents' => $priceInCents,
                    'url' => $paymentUrl,
                    'secure' => $this->config->isSecureConnection($storeId)
                ]);
            }

            return $paymentUrl;
            
        } catch (LocalizedException $e) {
            throw $e;
        } catch (\Exception $e) {
            $this->logger->critical('Somnia Payment Gateway: Unexpected error building payment URL', [
                'order_id' => $orderId,
                'error' => $e->getMessage()
            ]);
            throw new LocalizedException(
                __('Unable to build payment URL: %1', $e->getMessage())
            );
        }
    }

    /**
     * Get payment status from gateway
     *
     * @param string $paymentId Payment ID from gateway
     * @param int|null $storeId Store ID
     * @return array Payment status data
     * @throws LocalizedException
     */
    public function getPaymentStatus($paymentId, $storeId = null)
    {
        if (empty($paymentId)) {
            $this->logger->error('Somnia Payment Gateway: Payment ID is required for status check');
            throw new LocalizedException(__('Payment ID is required'));
        }

        $gatewayUrl = $this->config->getGatewayUrl($storeId);
        $statusUrl = $gatewayUrl . '/status/' . urlencode($paymentId);

        if ($this->config->isDebugMode($storeId)) {
            $this->logger->info('Somnia Payment Gateway: Checking payment status', [
                'payment_id' => $paymentId,
                'url' => $statusUrl
            ]);
        }

        try {
            // Configure curl
            $this->curl->setTimeout(self::HTTP_TIMEOUT);
            $this->curl->setOption(CURLOPT_RETURNTRANSFER, true);
            $this->curl->setOption(CURLOPT_FOLLOWLOCATION, true);

            // Make GET request
            $this->curl->get($statusUrl);

            $statusCode = $this->curl->getStatus();
            $response = $this->curl->getBody();

            if ($this->config->isDebugMode($storeId)) {
                $this->logger->debug('Somnia Payment Gateway: Status response received', [
                    'payment_id' => $paymentId,
                    'status_code' => $statusCode,
                    'response' => $response
                ]);
            }

            if ($statusCode !== 200) {
                $this->logger->error('Somnia Payment Gateway: Gateway returned error status', [
                    'payment_id' => $paymentId,
                    'status_code' => $statusCode,
                    'response' => $response
                ]);
                throw new LocalizedException(
                    __('Gateway returned error status: %1', $statusCode)
                );
            }

            // Parse JSON response
            $data = json_decode($response, true);

            if (json_last_error() !== JSON_ERROR_NONE) {
                $this->logger->error('Somnia Payment Gateway: Invalid JSON response', [
                    'payment_id' => $paymentId,
                    'json_error' => json_last_error_msg(),
                    'response' => $response
                ]);
                throw new LocalizedException(
                    __('Invalid JSON response from gateway: %1', json_last_error_msg())
                );
            }

            if (!is_array($data)) {
                $this->logger->error('Somnia Payment Gateway: Invalid response format', [
                    'payment_id' => $paymentId,
                    'response_type' => gettype($data)
                ]);
                throw new LocalizedException(__('Invalid response format from gateway'));
            }

            if ($this->config->isDebugMode($storeId)) {
                $this->logger->info('Somnia Payment Gateway: Status check successful', [
                    'payment_id' => $paymentId,
                    'status' => $data['status'] ?? 'unknown'
                ]);
            }

            return $data;

        } catch (LocalizedException $e) {
            throw $e;
        } catch (\Exception $e) {
            $this->logger->error('Somnia Payment Gateway: Status check failed', [
                'payment_id' => $paymentId,
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            throw new LocalizedException(
                __('Unable to verify payment status: %1', $e->getMessage())
            );
        }
    }

    /**
     * Test connection to gateway
     *
     * @param string|null $customGatewayUrl Custom gateway URL (for admin test)
     * @param int|null $storeId Store ID
     * @return array Result array with success, status, and error keys
     */
    public function testConnection($customGatewayUrl = null, $storeId = null)
    {
        // Use custom URL if provided, otherwise get from config
        $gatewayUrl = $customGatewayUrl ?: $this->config->getGatewayUrl($storeId);
        
        // Remove trailing slash
        $gatewayUrl = rtrim($gatewayUrl, '/');
        $healthUrl = $gatewayUrl . '/health';

        $debugMode = $customGatewayUrl ? false : $this->config->isDebugMode($storeId);

        if ($debugMode) {
            $this->logger->info('Somnia Payment Gateway: Testing connection', [
                'url' => $healthUrl
            ]);
        }

        try {
            // Configure curl
            $this->curl->setTimeout(self::HTTP_TIMEOUT);
            $this->curl->setOption(CURLOPT_RETURNTRANSFER, true);
            $this->curl->setOption(CURLOPT_FOLLOWLOCATION, true);

            // Make GET request
            $this->curl->get($healthUrl);

            $statusCode = $this->curl->getStatus();
            $response = $this->curl->getBody();

            if ($debugMode) {
                $this->logger->debug('Somnia Payment Gateway: Health check response', [
                    'status_code' => $statusCode,
                    'response' => $response
                ]);
            }

            if ($statusCode !== 200) {
                return [
                    'success' => false,
                    'error' => 'Gateway health check failed with status: ' . $statusCode
                ];
            }

            // Parse JSON response
            $data = json_decode($response, true);

            if (json_last_error() !== JSON_ERROR_NONE) {
                return [
                    'success' => false,
                    'error' => 'Invalid JSON response from gateway health check'
                ];
            }

            // Check if status is healthy
            if (isset($data['status']) && $data['status'] === 'healthy') {
                if ($debugMode) {
                    $this->logger->info('Somnia Payment Gateway: Connection test successful');
                }
                return [
                    'success' => true,
                    'status' => $data['status']
                ];
            }

            return [
                'success' => false,
                'error' => 'Gateway is not healthy'
            ];

        } catch (\Exception $e) {
            $this->logger->error('Somnia Payment Gateway: Connection test failed', [
                'url' => $healthUrl,
                'error' => $e->getMessage()
            ]);

            return [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
    }
}
