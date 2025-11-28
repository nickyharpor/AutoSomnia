<?php
/**
 * Somnia Payment Gateway - Title Backend Model
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Model\Config\Backend;

use Magento\Framework\App\Config\Value;

/**
 * Backend model for title sanitization
 */
class Title extends Value
{
    /**
     * Sanitize title before save
     *
     * @return $this
     */
    public function beforeSave()
    {
        $value = $this->getValue();

        if (!empty($value)) {
            // Sanitize input to prevent XSS
            $value = $this->sanitizeText($value);
            $this->setValue($value);
        }

        return parent::beforeSave();
    }

    /**
     * Sanitize text input
     *
     * @param string $text
     * @return string
     */
    protected function sanitizeText($text)
    {
        // Remove any HTML tags
        $text = strip_tags($text);
        
        // Remove any null bytes
        $text = str_replace(chr(0), '', $text);
        
        // Trim whitespace
        $text = trim($text);
        
        // Encode special characters to prevent XSS
        $text = htmlspecialchars($text, ENT_QUOTES | ENT_HTML5, 'UTF-8');
        
        return $text;
    }
}
