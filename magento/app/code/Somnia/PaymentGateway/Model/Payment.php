<?php
/**
 * Somnia Payment Gateway - Payment Method Model
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Model;

use Magento\Payment\Model\Method\AbstractMethod;
use Magento\Quote\Api\Data\CartInterface;
use Magento\Payment\Model\InfoInterface;
use Magento\Framework\Exception\LocalizedException;
use Magento\Framework\UrlInterface;

/**
 * Payment method model for Somnia cryptocurrency gateway
 */
class Payment extends AbstractMethod
{
    /**
     * Payment method code
     */
    const CODE = 'somnia_gateway';

    /**
     * @var string
     */
    protected $_code = self::CODE;

    /**
     * @var bool
     */
    protected $_isGateway = true;

    /**
     * @var bool
     */
    protected $_canAuthorize = true;

    /**
     * @var bool
     */
    protected $_canCapture = false;

    /**
     * @var bool
     */
    protected $_canCapturePartial = false;

    /**
     * @var bool
     */
    protected $_canRefund = false;

    /**
     * @var bool
     */
    protected $_canVoid = false;

    /**
     * @var bool
     */
    protected $_canUseInternal = false;

    /**
     * @var bool
     */
    protected $_canUseCheckout = true;

    /**
     * @var bool
     */
    protected $_canUseForMultishipping = false;

    /**
     * @var bool
     */
    protected $_isInitializeNeeded = false;

    /**
     * @var Config
     */
    protected $config;

    /**
     * @var UrlInterface
     */
    protected $urlBuilder;

    /**
     * @var \Magento\Checkout\Model\Session
     */
    protected $checkoutSession;

    /**
     * @var \Somnia\PaymentGateway\Model\Gateway\Client
     */
    protected $gatewayClient;

    /**
     * @var \Psr\Log\LoggerInterface
     */
    protected $customLogger;

    /**
     * @param \Magento\Framework\Model\Context $context
     * @param \Magento\Framework\Registry $registry
     * @param \Magento\Framework\Api\ExtensionAttributesFactory $extensionFactory
     * @param \Magento\Framework\Api\AttributeValueFactory $customAttributeFactory
     * @param \Magento\Payment\Helper\Data $paymentData
     * @param \Magento\Framework\App\Config\ScopeConfigInterface $scopeConfig
     * @param \Magento\Payment\Model\Method\Logger $logger
     * @param Config $config
     * @param UrlInterface $urlBuilder
     * @param \Magento\Checkout\Model\Session $checkoutSession
     * @param \Somnia\PaymentGateway\Model\Gateway\Client $gatewayClient
     * @param \Psr\Log\LoggerInterface $customLogger
     * @param \Magento\Framework\Model\ResourceModel\AbstractResource|null $resource
     * @param \Magento\Framework\Data\Collection\AbstractDb|null $resourceCollection
     * @param array $data
     */
    public function __construct(
        \Magento\Framework\Model\Context $context,
        \Magento\Framework\Registry $registry,
        \Magento\Framework\Api\ExtensionAttributesFactory $extensionFactory,
        \Magento\Framework\Api\AttributeValueFactory $customAttributeFactory,
        \Magento\Payment\Helper\Data $paymentData,
        \Magento\Framework\App\Config\ScopeConfigInterface $scopeConfig,
        \Magento\Payment\Model\Method\Logger $logger,
        Config $config,
        UrlInterface $urlBuilder,
        \Magento\Checkout\Model\Session $checkoutSession,
        \Somnia\PaymentGateway\Model\Gateway\Client $gatewayClient,
        \Psr\Log\LoggerInterface $customLogger,
        \Magento\Framework\Model\ResourceModel\AbstractResource $resource = null,
        \Magento\Framework\Data\Collection\AbstractDb $resourceCollection = null,
        array $data = []
    ) {
        parent::__construct(
            $context,
            $registry,
            $extensionFactory,
            $customAttributeFactory,
            $paymentData,
            $scopeConfig,
            $logger,
            $resource,
            $resourceCollection,
            $data
        );
        $this->config = $config;
        $this->urlBuilder = $urlBuilder;
        $this->checkoutSession = $checkoutSession;
        $this->gatewayClient = $gatewayClient;
        $this->customLogger = $customLogger;
    }

    /**
     * Check if payment method is available
     *
     * @param CartInterface|null $quote
     * @return bool
     */
    public function isAvailable(CartInterface $quote = null)
    {
        // Check if parent availability check passes
        if (!parent::isAvailable($quote)) {
            return false;
        }

        // Check if payment method is enabled in configuration
        if (!$this->config->isEnabled()) {
            return false;
        }

        // Check if gateway URL is configured
        $gatewayUrl = $this->config->getGatewayUrl();
        if (empty($gatewayUrl)) {
            return false;
        }

        // Check if merchant ID is configured
        $merchantId = $this->config->getMerchantId();
        if (empty($merchantId)) {
            return false;
        }

        return true;
    }

    /**
     * Authorize payment
     *
     * @param InfoInterface $payment
     * @param float $amount
     * @return $this
     * @throws LocalizedException
     */
    public function authorize(InfoInterface $payment, $amount)
    {
        if (!$this->canAuthorize()) {
            throw new LocalizedException(__('Authorize action is not available.'));
        }

        try {
            // Get order information
            $order = $payment->getOrder();
            $storeId = $order->getStoreId();
            
            // Test gateway connectivity before proceeding
            $connectionTest = $this->gatewayClient->testConnection(null, $storeId);
            
            if (!$connectionTest['success']) {
                // Log the error
                $this->customLogger->error('Somnia Payment Gateway: Connection test failed during authorization', [
                    'order_id' => $order->getIncrementId(),
                    'error' => $connectionTest['error'] ?? 'Unknown error'
                ]);
                
                // Restore customer cart
                $this->restoreQuote();
                
                throw new LocalizedException(
                    __('Payment gateway is currently unavailable. Please try again later or choose a different payment method.')
                );
            }
            
            // Store payment information
            $payment->setIsTransactionPending(true);
            $payment->setIsTransactionClosed(false);
            
            // Store additional information for later use
            $payment->setAdditionalInformation('somnia_gateway_url', $this->config->getGatewayUrl($storeId));
            $payment->setAdditionalInformation('somnia_merchant_id', $this->config->getMerchantId($storeId));
            
            if ($this->config->isDebugMode($storeId)) {
                $this->customLogger->info('Somnia Payment Gateway: Payment authorized', [
                    'order_id' => $order->getIncrementId(),
                    'amount' => $amount
                ]);
            }
            
            return $this;
            
        } catch (LocalizedException $e) {
            // Re-throw Magento exceptions
            throw $e;
            
        } catch (\Exception $e) {
            // Log unexpected errors
            $this->customLogger->critical('Somnia Payment Gateway: Unexpected error during authorization', [
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);
            
            // Restore customer cart
            $this->restoreQuote();
            
            throw new LocalizedException(
                __('An error occurred while processing your payment. Please try again.')
            );
        }
    }

    /**
     * Restore customer quote/cart
     *
     * @return void
     */
    protected function restoreQuote()
    {
        try {
            if ($this->checkoutSession->getLastRealOrder()->getId()) {
                $this->checkoutSession->restoreQuote();
                
                if ($this->config->isDebugMode()) {
                    $this->customLogger->info('Somnia Payment Gateway: Customer cart restored after payment failure');
                }
            }
        } catch (\Exception $e) {
            // Log but don't throw - cart restoration is a courtesy feature
            $this->customLogger->warning('Somnia Payment Gateway: Failed to restore customer cart', [
                'error' => $e->getMessage()
            ]);
        }
    }

    /**
     * Get redirect URL for payment gateway
     *
     * @return string
     */
    public function getOrderPlaceRedirectUrl()
    {
        return $this->urlBuilder->getUrl('somnia/redirect/index', ['_secure' => true]);
    }

    /**
     * Validate payment method configuration
     *
     * @return $this
     * @throws LocalizedException
     */
    public function validate()
    {
        parent::validate();

        // Validate gateway URL
        $gatewayUrl = $this->config->getGatewayUrl();
        if (empty($gatewayUrl)) {
            throw new LocalizedException(__('Gateway URL is not configured.'));
        }

        if (!filter_var($gatewayUrl, FILTER_VALIDATE_URL)) {
            throw new LocalizedException(__('Gateway URL is not valid.'));
        }

        // Validate merchant ID
        $merchantId = $this->config->getMerchantId();
        if (empty($merchantId)) {
            throw new LocalizedException(__('Merchant ID is not configured.'));
        }

        if (!is_numeric($merchantId) || $merchantId <= 0) {
            throw new LocalizedException(__('Merchant ID must be a positive integer.'));
        }

        return $this;
    }
}
