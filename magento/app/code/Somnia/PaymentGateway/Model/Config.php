<?php
/**
 * Somnia Payment Gateway - Configuration Provider
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Model;

use Magento\Framework\App\Config\ScopeConfigInterface;
use Magento\Store\Model\ScopeInterface;

/**
 * Configuration provider for Somnia payment gateway
 */
class Config
{
    /**
     * Configuration path constants
     */
    const XML_PATH_ACTIVE = 'payment/somnia_gateway/active';
    const XML_PATH_TITLE = 'payment/somnia_gateway/title';
    const XML_PATH_GATEWAY_URL = 'payment/somnia_gateway/gateway_url';
    const XML_PATH_MERCHANT_ID = 'payment/somnia_gateway/merchant_id';
    const XML_PATH_PAYMENT_TIMEOUT = 'payment/somnia_gateway/payment_timeout';
    const XML_PATH_ALLOWED_IPS = 'payment/somnia_gateway/allowed_ips';
    const XML_PATH_DEBUG = 'payment/somnia_gateway/debug';
    const XML_PATH_SORT_ORDER = 'payment/somnia_gateway/sort_order';

    /**
     * Default values
     */
    const DEFAULT_GATEWAY_URL = 'http://localhost:5000';
    const DEFAULT_PAYMENT_TIMEOUT = 30;
    const MIN_PAYMENT_TIMEOUT = 5;
    const MAX_PAYMENT_TIMEOUT = 120;

    /**
     * @var ScopeConfigInterface
     */
    protected $scopeConfig;

    /**
     * @param ScopeConfigInterface $scopeConfig
     */
    public function __construct(
        ScopeConfigInterface $scopeConfig
    ) {
        $this->scopeConfig = $scopeConfig;
    }

    /**
     * Check if payment method is enabled
     *
     * @param int|null $storeId
     * @return bool
     */
    public function isEnabled($storeId = null)
    {
        return (bool)$this->getConfigValue(self::XML_PATH_ACTIVE, $storeId);
    }

    /**
     * Get payment method title
     *
     * @param int|null $storeId
     * @return string
     */
    public function getTitle($storeId = null)
    {
        return (string)$this->getConfigValue(self::XML_PATH_TITLE, $storeId);
    }

    /**
     * Get gateway URL
     *
     * @param int|null $storeId
     * @return string
     */
    public function getGatewayUrl($storeId = null)
    {
        $url = $this->getConfigValue(self::XML_PATH_GATEWAY_URL, $storeId);
        
        if (empty($url)) {
            return self::DEFAULT_GATEWAY_URL;
        }

        // Remove trailing slash
        return rtrim($url, '/');
    }

    /**
     * Get merchant ID
     *
     * @param int|null $storeId
     * @return int|null
     */
    public function getMerchantId($storeId = null)
    {
        $merchantId = $this->getConfigValue(self::XML_PATH_MERCHANT_ID, $storeId);
        
        if (empty($merchantId)) {
            return null;
        }

        return (int)$merchantId;
    }

    /**
     * Get payment timeout in minutes
     *
     * @param int|null $storeId
     * @return int
     */
    public function getPaymentTimeout($storeId = null)
    {
        $timeout = $this->getConfigValue(self::XML_PATH_PAYMENT_TIMEOUT, $storeId);
        
        if (empty($timeout)) {
            return self::DEFAULT_PAYMENT_TIMEOUT;
        }

        $timeout = (int)$timeout;

        // Validate timeout is within acceptable range
        if ($timeout < self::MIN_PAYMENT_TIMEOUT) {
            return self::MIN_PAYMENT_TIMEOUT;
        }

        if ($timeout > self::MAX_PAYMENT_TIMEOUT) {
            return self::MAX_PAYMENT_TIMEOUT;
        }

        return $timeout;
    }

    /**
     * Check if debug mode is enabled
     *
     * @param int|null $storeId
     * @return bool
     */
    public function isDebugMode($storeId = null)
    {
        return (bool)$this->getConfigValue(self::XML_PATH_DEBUG, $storeId);
    }

    /**
     * Get sort order
     *
     * @param int|null $storeId
     * @return int
     */
    public function getSortOrder($storeId = null)
    {
        return (int)$this->getConfigValue(self::XML_PATH_SORT_ORDER, $storeId);
    }

    /**
     * Validate gateway URL format
     *
     * @param string $url
     * @return bool
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
     * Validate merchant ID
     *
     * @param mixed $merchantId
     * @return bool
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
     * Validate payment timeout
     *
     * @param mixed $timeout
     * @return bool
     */
    public function validatePaymentTimeout($timeout)
    {
        if (empty($timeout)) {
            return false;
        }

        // Check if timeout is numeric
        if (!is_numeric($timeout)) {
            return false;
        }

        // Check if timeout is within acceptable range
        $timeout = (int)$timeout;
        if ($timeout < self::MIN_PAYMENT_TIMEOUT || $timeout > self::MAX_PAYMENT_TIMEOUT) {
            return false;
        }

        return true;
    }

    /**
     * Check if gateway URL uses HTTPS
     *
     * @param int|null $storeId
     * @return bool
     */
    public function isSecureConnection($storeId = null)
    {
        $url = $this->getGatewayUrl($storeId);
        $scheme = parse_url($url, PHP_URL_SCHEME);
        
        return $scheme === 'https';
    }

    /**
     * Check if gateway URL is localhost
     *
     * @param int|null $storeId
     * @return bool
     */
    public function isLocalhostGateway($storeId = null)
    {
        $url = $this->getGatewayUrl($storeId);
        $host = parse_url($url, PHP_URL_HOST);
        
        return in_array($host, ['localhost', '127.0.0.1', '::1']);
    }

    /**
     * Check if HTTPS should be enforced (production mode and not localhost)
     *
     * @param int|null $storeId
     * @return bool
     */
    public function shouldEnforceHttps($storeId = null)
    {
        // Don't enforce HTTPS for localhost
        if ($this->isLocalhostGateway($storeId)) {
            return false;
        }

        // Enforce HTTPS in production mode
        return $this->isProductionMode();
    }

    /**
     * Check if Magento is in production mode
     *
     * @return bool
     */
    public function isProductionMode()
    {
        try {
            $state = \Magento\Framework\App\ObjectManager::getInstance()
                ->get(\Magento\Framework\App\State::class);
            
            $mode = $state->getMode();
            // Consider production and default modes as production
            return in_array($mode, [\Magento\Framework\App\State::MODE_PRODUCTION, \Magento\Framework\App\State::MODE_DEFAULT]);
        } catch (\Exception $e) {
            // If we can't determine mode, assume production for safety
            return true;
        }
    }

    /**
     * Get allowed callback IPs
     *
     * @param int|null $storeId
     * @return array
     */
    public function getAllowedIps($storeId = null)
    {
        $value = $this->getConfigValue(self::XML_PATH_ALLOWED_IPS, $storeId);
        
        if (empty($value)) {
            return [];
        }

        // Parse IP list
        $ips = preg_split('/[\r\n,]+/', $value);
        $ips = array_map('trim', $ips);
        $ips = array_filter($ips, function($ip) {
            return !empty($ip);
        });
        
        return array_values($ips);
    }

    /**
     * Check if IP whitelist is enabled
     *
     * @param int|null $storeId
     * @return bool
     */
    public function isIpWhitelistEnabled($storeId = null)
    {
        $allowedIps = $this->getAllowedIps($storeId);
        return !empty($allowedIps);
    }

    /**
     * Check if IP is allowed to send callbacks
     *
     * @param string $ip
     * @param int|null $storeId
     * @return bool
     */
    public function isIpAllowed($ip, $storeId = null)
    {
        // If no whitelist is configured, allow all IPs
        if (!$this->isIpWhitelistEnabled($storeId)) {
            return true;
        }

        $allowedIps = $this->getAllowedIps($storeId);
        
        foreach ($allowedIps as $allowedIp) {
            if ($this->matchIp($ip, $allowedIp)) {
                return true;
            }
        }
        
        return false;
    }

    /**
     * Match IP address against pattern (supports CIDR notation)
     *
     * @param string $ip IP address to check
     * @param string $pattern IP pattern (can be single IP or CIDR)
     * @return bool
     */
    protected function matchIp($ip, $pattern)
    {
        // Exact match
        if ($ip === $pattern) {
            return true;
        }

        // Check CIDR notation
        if (strpos($pattern, '/') !== false) {
            return $this->matchCidr($ip, $pattern);
        }

        return false;
    }

    /**
     * Match IP against CIDR notation
     *
     * @param string $ip
     * @param string $cidr
     * @return bool
     */
    protected function matchCidr($ip, $cidr)
    {
        list($subnet, $mask) = explode('/', $cidr, 2);

        // Convert to binary for comparison
        if (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4)) {
            // IPv4
            $ipLong = ip2long($ip);
            $subnetLong = ip2long($subnet);
            
            if ($ipLong === false || $subnetLong === false) {
                return false;
            }
            
            $maskLong = -1 << (32 - (int)$mask);
            
            return ($ipLong & $maskLong) === ($subnetLong & $maskLong);
        } elseif (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV6)) {
            // IPv6 - simplified check
            $ipBin = inet_pton($ip);
            $subnetBin = inet_pton($subnet);
            
            if ($ipBin === false || $subnetBin === false) {
                return false;
            }
            
            $maskBytes = (int)$mask;
            $fullBytes = floor($maskBytes / 8);
            $remainingBits = $maskBytes % 8;
            
            // Compare full bytes
            if (substr($ipBin, 0, $fullBytes) !== substr($subnetBin, 0, $fullBytes)) {
                return false;
            }
            
            // Compare remaining bits if any
            if ($remainingBits > 0 && $fullBytes < strlen($ipBin)) {
                $ipByte = ord($ipBin[$fullBytes]);
                $subnetByte = ord($subnetBin[$fullBytes]);
                $mask = (0xFF << (8 - $remainingBits)) & 0xFF;
                
                if (($ipByte & $mask) !== ($subnetByte & $mask)) {
                    return false;
                }
            }
            
            return true;
        }

        return false;
    }

    /**
     * Get gateway host from URL
     *
     * @param int|null $storeId
     * @return string|null
     */
    public function getGatewayHost($storeId = null)
    {
        $url = $this->getGatewayUrl($storeId);
        return parse_url($url, PHP_URL_HOST);
    }

    /**
     * Get configuration value
     *
     * @param string $path
     * @param int|null $storeId
     * @return mixed
     */
    protected function getConfigValue($path, $storeId = null)
    {
        return $this->scopeConfig->getValue(
            $path,
            ScopeInterface::SCOPE_STORE,
            $storeId
        );
    }
}
