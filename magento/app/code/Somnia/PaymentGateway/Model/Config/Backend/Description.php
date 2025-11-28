<?php
/**
 * Somnia Payment Gateway - Description Backend Model
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Model\Config\Backend;

use Magento\Framework\App\Config\Value;

/**
 * Backend model for description sanitization
 */
class Description extends Value
{
    /**
     * Sanitize description before save
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
     * Sanitize text input (allows basic HTML for description)
     *
     * @param string $text
     * @return string
     */
    protected function sanitizeText($text)
    {
        // Remove any null bytes
        $text = str_replace(chr(0), '', $text);
        
        // Trim whitespace
        $text = trim($text);
        
        // Allow only safe HTML tags (for formatting)
        $allowedTags = '<p><br><strong><em><ul><ol><li><a>';
        $text = strip_tags($text, $allowedTags);
        
        // Sanitize attributes in allowed tags
        $text = $this->sanitizeAttributes($text);
        
        return $text;
    }

    /**
     * Sanitize HTML attributes
     *
     * @param string $html
     * @return string
     */
    protected function sanitizeAttributes($html)
    {
        // Remove dangerous attributes like onclick, onerror, etc.
        $html = preg_replace('/\s*on\w+\s*=\s*["\'].*?["\']/i', '', $html);
        
        // Remove javascript: protocol from href
        $html = preg_replace('/href\s*=\s*["\']javascript:.*?["\']/i', '', $html);
        
        // Remove data: protocol from href
        $html = preg_replace('/href\s*=\s*["\']data:.*?["\']/i', '', $html);
        
        return $html;
    }
}
