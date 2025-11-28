<?php
/**
 * Somnia Payment Gateway - Merchant ID Backend Model
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Model\Config\Backend;

use Magento\Framework\App\Config\Value;
use Magento\Framework\Exception\LocalizedException;

/**
 * Backend model for merchant ID validation
 */
class MerchantId extends Value
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
     * Validate merchant ID before save
     *
     * @return $this
     * @throws LocalizedException
     */
    public function beforeSave()
    {
        $value = $this->getValue();

        // Allow empty value
        if (empty($value)) {
            return parent::beforeSave();
        }

        // Sanitize input
        $value = $this->sanitizeMerchantId($value);
        $this->setValue($value);

        // Validate merchant ID
        if (!$this->config->validateMerchantId($value)) {
            throw new LocalizedException(
                __('Merchant ID must be a positive integer.')
            );
        }

        return parent::beforeSave();
    }

    /**
     * Sanitize merchant ID input
     *
     * @param string $merchantId
     * @return string
     */
    protected function sanitizeMerchantId($merchantId)
    {
        // Remove any HTML tags
        $merchantId = strip_tags($merchantId);
        
        // Trim whitespace
        $merchantId = trim($merchantId);
        
        // Remove any non-numeric characters
        $merchantId = preg_replace('/[^0-9]/', '', $merchantId);
        
        return $merchantId;
    }
}
