<?php
/**
 * Somnia Payment Gateway - Gateway URL Backend Model
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Model\Config\Backend;

use Magento\Framework\App\Config\Value;
use Magento\Framework\Exception\LocalizedException;

/**
 * Backend model for gateway URL validation
 */
class GatewayUrl extends Value
{
    /**
     * @var \Somnia\PaymentGateway\Model\Config
     */
    protected $config;

    /**
     * @param \Magento\Framework\Model\Context $context
     * @param \Magento\Framework\Registry $registry
     * @param \Magento\Framework\App\Config\ScopeConfigInterface $scopeConfig
     * @param \Magento\Framework\App\Cache\TypeListInterface $cacheTypeList
     * @param \Somnia\PaymentGateway\Model\Config $config
     * @param \Magento\Framework\Model\ResourceModel\AbstractResource|null $resource
     * @param \Magento\Framework\Data\Collection\AbstractDb|null $resourceCollection
     * @param array $data
     */
    public function __construct(
        \Magento\Framework\Model\Context $context,
        \Magento\Framework\Registry $registry,
        \Magento\Framework\App\Config\ScopeConfigInterface $scopeConfig,
        \Magento\Framework\App\Cache\TypeListInterface $cacheTypeList,
        \Somnia\PaymentGateway\Model\Config $config,
        \Magento\Framework\Model\ResourceModel\AbstractResource $resource = null,
        \Magento\Framework\Data\Collection\AbstractDb $resourceCollection = null,
        array $data = []
    ) {
        parent::__construct($context, $registry, $scopeConfig, $cacheTypeList, $resource, $resourceCollection, $data);
        $this->config = $config;
    }

    /**
     * Validate gateway URL before save
     *
     * @return $this
     * @throws LocalizedException
     */
    public function beforeSave()
    {
        $value = $this->getValue();

        // Allow empty value (will use default)
        if (empty($value)) {
            return parent::beforeSave();
        }

        // Sanitize input
        $value = $this->sanitizeUrl($value);
        $this->setValue($value);

        // Validate URL format
        if (!$this->config->validateGatewayUrl($value)) {
            throw new LocalizedException(
                __('Gateway URL must be a valid HTTP or HTTPS URL.')
            );
        }

        // Check if URL uses HTTPS in production mode
        $scheme = parse_url($value, PHP_URL_SCHEME);
        if ($scheme === 'http' && !$this->isLocalhost($value)) {
            // Check if we're in production mode (not developer mode)
            if ($this->isProductionMode()) {
                // In production, require HTTPS for non-localhost URLs
                throw new LocalizedException(
                    __('Gateway URL must use HTTPS in production mode. HTTP is only allowed for localhost/development.')
                );
            } else {
                // In development mode, log warning but allow HTTP
                $this->_logger->warning(
                    'Somnia Payment Gateway: HTTP URL configured for non-localhost gateway. HTTPS is strongly recommended for production.'
                );
            }
        }

        return parent::beforeSave();
    }

    /**
     * Sanitize URL input
     *
     * @param string $url
     * @return string
     */
    protected function sanitizeUrl($url)
    {
        // Remove any HTML tags
        $url = strip_tags($url);
        
        // Trim whitespace
        $url = trim($url);
        
        // Remove trailing slash
        $url = rtrim($url, '/');
        
        return $url;
    }

    /**
     * Check if URL is localhost
     *
     * @param string $url
     * @return bool
     */
    protected function isLocalhost($url)
    {
        $host = parse_url($url, PHP_URL_HOST);
        
        return in_array($host, ['localhost', '127.0.0.1', '::1']);
    }

    /**
     * Check if Magento is in production mode
     *
     * @return bool
     */
    protected function isProductionMode()
    {
        $state = \Magento\Framework\App\ObjectManager::getInstance()
            ->get(\Magento\Framework\App\State::class);
        
        try {
            $mode = $state->getMode();
            // Consider production and default modes as production
            return in_array($mode, [\Magento\Framework\App\State::MODE_PRODUCTION, \Magento\Framework\App\State::MODE_DEFAULT]);
        } catch (\Exception $e) {
            // If we can't determine mode, assume production for safety
            return true;
        }
    }
}
