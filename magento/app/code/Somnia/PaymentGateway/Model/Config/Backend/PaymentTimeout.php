<?php
/**
 * Somnia Payment Gateway - Payment Timeout Backend Model
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Model\Config\Backend;

use Magento\Framework\App\Config\Value;
use Magento\Framework\Exception\LocalizedException;

/**
 * Backend model for payment timeout validation
 */
class PaymentTimeout extends Value
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
     * Validate payment timeout before save
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
        $value = $this->sanitizeTimeout($value);
        $this->setValue($value);

        // Validate timeout
        if (!$this->config->validatePaymentTimeout($value)) {
            throw new LocalizedException(
                __('Payment timeout must be between %1 and %2 minutes.', 
                    \Somnia\PaymentGateway\Model\Config::MIN_PAYMENT_TIMEOUT,
                    \Somnia\PaymentGateway\Model\Config::MAX_PAYMENT_TIMEOUT
                )
            );
        }

        return parent::beforeSave();
    }

    /**
     * Sanitize timeout input
     *
     * @param string $timeout
     * @return string
     */
    protected function sanitizeTimeout($timeout)
    {
        // Remove any HTML tags
        $timeout = strip_tags($timeout);
        
        // Trim whitespace
        $timeout = trim($timeout);
        
        // Remove any non-numeric characters
        $timeout = preg_replace('/[^0-9]/', '', $timeout);
        
        return $timeout;
    }
}
