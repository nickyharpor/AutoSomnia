<?php
/**
 * Somnia Payment Gateway - Test Connection Controller
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Controller\Adminhtml\System\Config;

use Magento\Backend\App\Action;
use Magento\Backend\App\Action\Context;
use Magento\Framework\Controller\Result\JsonFactory;
use Somnia\PaymentGateway\Model\Gateway\Client;
use Psr\Log\LoggerInterface;

/**
 * Test connection to payment gateway
 */
class TestConnection extends Action
{
    /**
     * Authorization level
     */
    const ADMIN_RESOURCE = 'Magento_Payment::payment';

    /**
     * @var JsonFactory
     */
    protected $resultJsonFactory;

    /**
     * @var Client
     */
    protected $gatewayClient;

    /**
     * @var LoggerInterface
     */
    protected $logger;

    /**
     * @param Context $context
     * @param JsonFactory $resultJsonFactory
     * @param Client $gatewayClient
     * @param LoggerInterface $logger
     */
    public function __construct(
        Context $context,
        JsonFactory $resultJsonFactory,
        Client $gatewayClient,
        LoggerInterface $logger
    ) {
        parent::__construct($context);
        $this->resultJsonFactory = $resultJsonFactory;
        $this->gatewayClient = $gatewayClient;
        $this->logger = $logger;
    }

    /**
     * Test connection to gateway
     *
     * @return \Magento\Framework\Controller\Result\Json
     */
    public function execute()
    {
        $result = $this->resultJsonFactory->create();
        
        try {
            // Get parameters from request
            $gatewayUrl = $this->getRequest()->getParam('gateway_url');
            $merchantId = $this->getRequest()->getParam('merchant_id');
            
            // Validate inputs
            if (empty($gatewayUrl)) {
                return $result->setData([
                    'success' => false,
                    'message' => __('Gateway URL is required.')
                ]);
            }
            
            if (empty($merchantId)) {
                return $result->setData([
                    'success' => false,
                    'message' => __('Merchant ID is required.')
                ]);
            }
            
            // Validate URL format
            if (!filter_var($gatewayUrl, FILTER_VALIDATE_URL)) {
                return $result->setData([
                    'success' => false,
                    'message' => __('Gateway URL is not a valid URL.')
                ]);
            }
            
            // Validate merchant ID is numeric
            if (!is_numeric($merchantId) || (int)$merchantId <= 0) {
                return $result->setData([
                    'success' => false,
                    'message' => __('Merchant ID must be a positive integer.')
                ]);
            }
            
            // Test connection using gateway client
            $testResult = $this->gatewayClient->testConnection($gatewayUrl);
            
            if ($testResult['success']) {
                return $result->setData([
                    'success' => true,
                    'message' => __('Successfully connected to gateway. Status: %1', $testResult['status'])
                ]);
            } else {
                return $result->setData([
                    'success' => false,
                    'message' => __('Failed to connect to gateway: %1', $testResult['error'])
                ]);
            }
            
        } catch (\Exception $e) {
            $this->logger->error('Somnia Gateway test connection error: ' . $e->getMessage());
            
            return $result->setData([
                'success' => false,
                'message' => __('Connection test failed: %1', $e->getMessage())
            ]);
        }
    }
}
