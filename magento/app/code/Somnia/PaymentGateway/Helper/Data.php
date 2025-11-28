<?php
/**
 * Somnia Payment Gateway - Helper Class
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Helper;

use Magento\Framework\App\Helper\AbstractHelper;
use Magento\Framework\App\Helper\Context;
use Somnia\PaymentGateway\Model\Config;
use Psr\Log\LoggerInterface;

/**
 * Helper class for utility functions
 */
class Data extends AbstractHelper
{
    /**
     * Payment amount tolerance (0.1%)
     */
    const PAYMENT_AMOUNT_TOLERANCE = 0.001;

    /**
     * Log file name
     */
    const LOG_FILE = 'somnia_payment.log';

    /**
     * @var Config
     */
    protected $config;

    /**
     * @var LoggerInterface
     */
    protected $logger;

    /**
     * @param Context $context
     * @param Config $config
     * @param LoggerInterface $logger
     */
    public function __construct(
        Context $context,
        Config $config,
        LoggerInterface $logger
    ) {
        parent::__construct($context);
        $this->config = $config;
        $this->logger = $logger;
    }

    /**
     * Convert amount to cents
     *
     * Requirement 4.2: Convert order total to USD cents for the payment gateway
     *
     * @param float $amount Amount in dollars
     * @return int Amount in cents
     */
    public function convertToCents($amount)
    {
        return (int)round($amount * 100);
    }

    /**
     * Convert cents to amount
     *
     * @param int $cents Amount in cents
     * @return float Amount in dollars
     */
    public function convertFromCents($cents)
    {
        return (float)($cents / 100);
    }

    /**
     * Validate payment URL format
     *
     * @param string $url URL to validate
     * @return bool True if valid, false otherwise
     */
    public function validatePaymentUrl($url)
    {
        if (empty($url)) {
            return false;
        }

        // Check if URL is valid
        if (!filter_var($url, FILTER_VALIDATE_URL)) {
            return false;
        }

        // Check if URL uses http or https protocol
        $scheme = parse_url($url, PHP_URL_SCHEME);
        if (!in_array($scheme, ['http', 'https'])) {
            return false;
        }

        // Check if URL contains required path
        $path = parse_url($url, PHP_URL_PATH);
        if (empty($path) || $path === '/') {
            return false;
        }

        return true;
    }

    /**
     * Validate payment amount matches order total
     *
     * @param float $orderTotal Order total amount
     * @param float $paidAmount Paid amount from gateway
     * @return bool True if amounts match within tolerance
     */
    public function validatePaymentAmount($orderTotal, $paidAmount)
    {
        if ($orderTotal <= 0 || $paidAmount <= 0) {
            return false;
        }

        // Calculate difference percentage
        $difference = abs($orderTotal - $paidAmount);
        $tolerance = $orderTotal * self::PAYMENT_AMOUNT_TOLERANCE;

        return $difference <= $tolerance;
    }

    /**
     * Log info message
     *
     * Requirement 8.2: Log all communication with the Payment Gateway when debug mode is enabled
     *
     * @param string $message Log message
     * @param array $context Additional context data
     * @param int|null $storeId Store ID
     * @return void
     */
    public function logInfo($message, array $context = [], $storeId = null)
    {
        if ($this->config->isDebugMode($storeId)) {
            $this->logger->info($this->formatLogMessage($message), $context);
        }
    }

    /**
     * Log debug message
     *
     * Requirement 8.2: Log all communication with the Payment Gateway when debug mode is enabled
     *
     * @param string $message Log message
     * @param array $context Additional context data
     * @param int|null $storeId Store ID
     * @return void
     */
    public function logDebug($message, array $context = [], $storeId = null)
    {
        if ($this->config->isDebugMode($storeId)) {
            $this->logger->debug($this->formatLogMessage($message), $context);
        }
    }

    /**
     * Log error message
     *
     * Requirement 8.4: Log failure details with timestamp and payment_id
     *
     * @param string $message Log message
     * @param array $context Additional context data
     * @param int|null $storeId Store ID (not used for errors, always logged)
     * @return void
     */
    public function logError($message, array $context = [], $storeId = null)
    {
        $this->logger->error($this->formatLogMessage($message), $context);
    }

    /**
     * Log warning message
     *
     * @param string $message Log message
     * @param array $context Additional context data
     * @param int|null $storeId Store ID (not used for warnings, always logged)
     * @return void
     */
    public function logWarning($message, array $context = [], $storeId = null)
    {
        $this->logger->warning($this->formatLogMessage($message), $context);
    }

    /**
     * Log critical message
     *
     * @param string $message Log message
     * @param array $context Additional context data
     * @param int|null $storeId Store ID (not used for critical, always logged)
     * @return void
     */
    public function logCritical($message, array $context = [], $storeId = null)
    {
        $this->logger->critical($this->formatLogMessage($message), $context);
    }

    /**
     * Format log message with prefix
     *
     * @param string $message Original message
     * @return string Formatted message
     */
    protected function formatLogMessage($message)
    {
        return 'Somnia Payment Gateway: ' . $message;
    }

    /**
     * Sanitize string for logging (mask sensitive data)
     *
     * @param string $value Value to sanitize
     * @param int $visibleChars Number of visible characters at start
     * @return string Sanitized value
     */
    public function sanitizeForLog($value, $visibleChars = 4)
    {
        if (empty($value)) {
            return '';
        }

        $length = strlen($value);
        
        if ($length <= $visibleChars) {
            return str_repeat('*', $length);
        }

        $visible = substr($value, 0, $visibleChars);
        $masked = str_repeat('*', $length - $visibleChars);

        return $visible . $masked;
    }

    /**
     * Format payment data for logging
     *
     * @param array $paymentData Payment data array
     * @return array Formatted payment data
     */
    public function formatPaymentDataForLog(array $paymentData)
    {
        $formatted = [];

        foreach ($paymentData as $key => $value) {
            // Mask sensitive fields
            if (in_array($key, ['payment_id', 'transaction_id'])) {
                $formatted[$key] = $this->sanitizeForLog($value, 8);
            } else {
                $formatted[$key] = $value;
            }
        }

        return $formatted;
    }

    /**
     * Get formatted timestamp
     *
     * @return string Formatted timestamp
     */
    public function getFormattedTimestamp()
    {
        return date('Y-m-d H:i:s');
    }

    /**
     * Check if URL uses HTTPS
     *
     * @param string $url URL to check
     * @return bool True if HTTPS, false otherwise
     */
    public function isSecureUrl($url)
    {
        if (empty($url)) {
            return false;
        }

        $scheme = parse_url($url, PHP_URL_SCHEME);
        return $scheme === 'https';
    }

    /**
     * Build callback URL
     *
     * @param string $baseUrl Store base URL
     * @return string Callback URL
     */
    public function buildCallbackUrl($baseUrl)
    {
        $baseUrl = rtrim($baseUrl, '/');
        return $baseUrl . '/somnia/callback/index';
    }

    /**
     * Parse payment ID from URL or string
     *
     * @param string $input Input string or URL
     * @return string|null Payment ID or null if not found
     */
    public function parsePaymentId($input)
    {
        if (empty($input)) {
            return null;
        }

        // If it's a URL, try to extract payment ID from path
        if (filter_var($input, FILTER_VALIDATE_URL)) {
            $path = parse_url($input, PHP_URL_PATH);
            $parts = explode('/', trim($path, '/'));
            
            // Look for UUID pattern in path segments
            foreach ($parts as $part) {
                if ($this->isValidUuid($part)) {
                    return $part;
                }
            }
        }

        // Check if input itself is a valid UUID
        if ($this->isValidUuid($input)) {
            return $input;
        }

        return null;
    }

    /**
     * Validate UUID format
     *
     * @param string $uuid UUID string to validate
     * @return bool True if valid UUID, false otherwise
     */
    public function isValidUuid($uuid)
    {
        if (empty($uuid)) {
            return false;
        }

        $pattern = '/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i';
        return preg_match($pattern, $uuid) === 1;
    }

    /**
     * Format currency amount for display
     *
     * @param float $amount Amount to format
     * @param string $currencyCode Currency code (default: USD)
     * @return string Formatted amount
     */
    public function formatCurrency($amount, $currencyCode = 'USD')
    {
        return number_format($amount, 2, '.', ',') . ' ' . $currencyCode;
    }

    /**
     * Get payment timeout in seconds
     *
     * @param int|null $storeId Store ID
     * @return int Timeout in seconds
     */
    public function getPaymentTimeoutSeconds($storeId = null)
    {
        $timeoutMinutes = $this->config->getPaymentTimeout($storeId);
        return $timeoutMinutes * 60;
    }

    /**
     * Check if payment is expired
     *
     * @param string $createdAt Payment creation timestamp
     * @param int|null $storeId Store ID
     * @return bool True if expired, false otherwise
     */
    public function isPaymentExpired($createdAt, $storeId = null)
    {
        if (empty($createdAt)) {
            return false;
        }

        $createdTimestamp = strtotime($createdAt);
        $currentTimestamp = time();
        $timeoutSeconds = $this->getPaymentTimeoutSeconds($storeId);

        return ($currentTimestamp - $createdTimestamp) > $timeoutSeconds;
    }

    /**
     * Sanitize input to prevent injection attacks
     *
     * Requirement 10.1: Validate all callback parameters to prevent injection attacks
     *
     * @param string $input Input string to sanitize
     * @return string Sanitized input
     */
    public function sanitizeInput($input)
    {
        if (empty($input)) {
            return '';
        }

        // Remove any HTML tags
        $input = strip_tags($input);
        
        // Remove any null bytes
        $input = str_replace(chr(0), '', $input);
        
        // Remove any control characters except newline and tab
        $input = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/', '', $input);
        
        // Trim whitespace
        $input = trim($input);
        
        return $input;
    }

    /**
     * Validate order ID format
     *
     * Requirement 10.4: Sanitize all user inputs in admin configuration forms
     *
     * @param string $orderId Order ID to validate
     * @return bool True if valid, false otherwise
     */
    public function validateOrderId($orderId)
    {
        if (empty($orderId)) {
            return false;
        }

        // Order ID should be alphanumeric with optional dashes
        $pattern = '/^[a-zA-Z0-9\-]+$/';
        
        if (preg_match($pattern, $orderId) !== 1) {
            return false;
        }
        
        // Check length (reasonable limit)
        if (strlen($orderId) > 50) {
            return false;
        }
        
        return true;
    }

    /**
     * Validate merchant ID format
     *
     * @param mixed $merchantId Merchant ID to validate
     * @return bool True if valid, false otherwise
     */
    public function validateMerchantId($merchantId)
    {
        if (empty($merchantId)) {
            return false;
        }

        // Check if merchant ID is numeric
        if (!is_numeric($merchantId)) {
            return false;
        }

        // Check if merchant ID is positive integer
        $merchantId = (int)$merchantId;
        if ($merchantId <= 0) {
            return false;
        }

        return true;
    }

    /**
     * Validate gateway URL format
     *
     * @param string $url Gateway URL to validate
     * @return bool True if valid, false otherwise
     */
    public function validateGatewayUrl($url)
    {
        if (empty($url)) {
            return false;
        }

        // Check if URL is valid
        if (!filter_var($url, FILTER_VALIDATE_URL)) {
            return false;
        }

        // Check if URL uses http or https protocol
        $scheme = parse_url($url, PHP_URL_SCHEME);
        if (!in_array($scheme, ['http', 'https'])) {
            return false;
        }

        return true;
    }

    /**
     * Get validation error message for invalid input
     *
     * @param string $fieldName Field name that failed validation
     * @param string $errorType Type of validation error
     * @return string Error message
     */
    public function getValidationErrorMessage($fieldName, $errorType = 'invalid')
    {
        $messages = [
            'payment_id' => [
                'required' => __('Payment ID is required.'),
                'invalid' => __('Invalid payment ID format. Must be a valid UUID.'),
            ],
            'order_id' => [
                'required' => __('Order ID is required.'),
                'invalid' => __('Invalid order ID format. Must be alphanumeric.'),
            ],
            'gateway_url' => [
                'required' => __('Gateway URL is required.'),
                'invalid' => __('Invalid gateway URL format. Must be a valid HTTP or HTTPS URL.'),
            ],
            'merchant_id' => [
                'required' => __('Merchant ID is required.'),
                'invalid' => __('Invalid merchant ID. Must be a positive integer.'),
            ],
            'payment_timeout' => [
                'required' => __('Payment timeout is required.'),
                'invalid' => __('Invalid payment timeout. Must be between 5 and 120 minutes.'),
            ],
        ];

        if (isset($messages[$fieldName][$errorType])) {
            return $messages[$fieldName][$errorType];
        }

        return __('Invalid %1.', $fieldName);
    }
}
