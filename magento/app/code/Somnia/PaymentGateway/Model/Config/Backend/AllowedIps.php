<?php
/**
 * Somnia Payment Gateway - Allowed IPs Backend Model
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Model\Config\Backend;

use Magento\Framework\App\Config\Value;
use Magento\Framework\Exception\LocalizedException;

/**
 * Backend model for allowed IPs validation
 */
class AllowedIps extends Value
{
    /**
     * Validate allowed IPs before save
     *
     * @return $this
     * @throws LocalizedException
     */
    public function beforeSave()
    {
        $value = $this->getValue();

        // Allow empty value (no IP restriction)
        if (empty($value)) {
            return parent::beforeSave();
        }

        // Sanitize and validate IPs
        $ips = $this->parseIpList($value);
        
        foreach ($ips as $ip) {
            if (!$this->validateIp($ip)) {
                throw new LocalizedException(
                    __('Invalid IP address format: %1. Please enter valid IPv4 or IPv6 addresses.', $ip)
                );
            }
        }

        // Store cleaned IP list (one per line)
        $this->setValue(implode("\n", $ips));

        return parent::beforeSave();
    }

    /**
     * Parse IP list from textarea input
     *
     * @param string $value
     * @return array
     */
    protected function parseIpList($value)
    {
        // Split by newlines and commas
        $ips = preg_split('/[\r\n,]+/', $value);
        
        // Trim and filter empty values
        $ips = array_map('trim', $ips);
        $ips = array_filter($ips, function($ip) {
            return !empty($ip);
        });
        
        return array_unique($ips);
    }

    /**
     * Validate IP address format
     *
     * @param string $ip
     * @return bool
     */
    protected function validateIp($ip)
    {
        // Check for CIDR notation (e.g., 192.168.1.0/24)
        if (strpos($ip, '/') !== false) {
            list($address, $mask) = explode('/', $ip, 2);
            
            // Validate address part
            if (!filter_var($address, FILTER_VALIDATE_IP)) {
                return false;
            }
            
            // Validate mask
            if (!is_numeric($mask) || $mask < 0 || $mask > 128) {
                return false;
            }
            
            return true;
        }
        
        // Validate regular IP address (IPv4 or IPv6)
        return filter_var($ip, FILTER_VALIDATE_IP) !== false;
    }
}
