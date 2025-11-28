<?php
/**
 * Somnia Payment Gateway - Callback Controller
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Controller\Callback;

use Magento\Framework\App\Action\Action;
use Magento\Framework\App\Action\Context;
use Magento\Framework\App\Action\HttpGetActionInterface;
use Magento\Framework\App\Action\HttpPostActionInterface;
use Magento\Framework\Controller\Result\JsonFactory;
use Magento\Framework\Exception\LocalizedException;
use Magento\Sales\Api\OrderRepositoryInterface;
use Magento\Sales\Model\Order;
use Somnia\PaymentGateway\Model\Gateway\Client;
use Somnia\PaymentGateway\Model\Gateway\Response\StatusResponse;
use Somnia\PaymentGateway\Model\Config;
use Somnia\PaymentGateway\Helper\Data as HelperData;
use Psr\Log\LoggerInterface;
use Magento\Sales\Model\Order\Email\Sender\OrderSender;

/**
 * Callback endpoint for payment notifications from gateway
 */
class Index extends Action implements HttpGetActionInterface, HttpPostActionInterface
{
    /**
     * Payment amount tolerance (0.1%)
     */
    const AMOUNT_TOLERANCE = 0.001;

    /**
     * @var JsonFactory
     */
    protected $resultJsonFactory;

    /**
     * @var OrderRepositoryInterface
     */
    protected $orderRepository;

    /**
     * @var Client
     */
    protected $gatewayClient;

    /**
     * @var StatusResponse
     */
    protected $statusResponse;

    /**
     * @var Config
     */
    protected $config;

    /**
     * @var LoggerInterface
     */
    protected $logger;

    /**
     * @var HelperData
     */
    protected $helper;

    /**
     * @var OrderSender
     */
    protected $orderSender;

    /**
     * @param Context $context
     * @param JsonFactory $resultJsonFactory
     * @param OrderRepositoryInterface $orderRepository
     * @param Client $gatewayClient
     * @param StatusResponse $statusResponse
     * @param Config $config
     * @param LoggerInterface $logger
     * @param HelperData $helper
     * @param OrderSender $orderSender
     */
    public function __construct(
        Context $context,
        JsonFactory $resultJsonFactory,
        OrderRepositoryInterface $orderRepository,
        Client $gatewayClient,
        StatusResponse $statusResponse,
        Config $config,
        LoggerInterface $logger,
        HelperData $helper,
        OrderSender $orderSender
    ) {
        parent::__construct($context);
        $this->resultJsonFactory = $resultJsonFactory;
        $this->orderRepository = $orderRepository;
        $this->gatewayClient = $gatewayClient;
        $this->statusResponse = $statusResponse;
        $this->config = $config;
        $this->logger = $logger;
        $this->helper = $helper;
        $this->orderSender = $orderSender;
    }

    /**
     * Execute callback action
     *
     * @return \Magento\Framework\Controller\Result\Json
     */
    public function execute()
    {
        $result = $this->resultJsonFactory->create();

        try {
            // Extract parameters
            $paymentId = $this->getRequest()->getParam('payment_id');
            $orderId = $this->getRequest()->getParam('order_id');

            // Validate required parameters
            if (empty($paymentId)) {
                $this->logger->warning('Somnia Payment Gateway: Callback received without payment_id');
                throw new LocalizedException(__('Payment ID is required'));
            }

            if (empty($orderId)) {
                $this->logger->warning('Somnia Payment Gateway: Callback received without order_id', [
                    'payment_id' => $paymentId
                ]);
                throw new LocalizedException(__('Order ID is required'));
            }

            // Sanitize inputs to prevent injection attacks
            $paymentId = $this->helper->sanitizeInput($paymentId);
            $orderId = $this->helper->sanitizeInput($orderId);

            // Validate payment_id format (should be UUID)
            if (!$this->helper->isValidUuid($paymentId)) {
                $this->logger->warning('Somnia Payment Gateway: Invalid payment ID format', [
                    'payment_id' => $paymentId,
                    'order_id' => $orderId
                ]);
                throw new LocalizedException($this->helper->getValidationErrorMessage('payment_id', 'invalid'));
            }

            // Validate order_id format (alphanumeric with dashes)
            if (!$this->helper->validateOrderId($orderId)) {
                $this->logger->warning('Somnia Payment Gateway: Invalid order ID format', [
                    'payment_id' => $paymentId,
                    'order_id' => $orderId
                ]);
                throw new LocalizedException($this->helper->getValidationErrorMessage('order_id', 'invalid'));
            }

            // Get remote IP address
            $remoteIp = $this->getRemoteIp();

            if ($this->config->isDebugMode()) {
                $this->logger->info('Somnia Payment Gateway: Callback received', [
                    'payment_id' => $paymentId,
                    'order_id' => $orderId,
                    'remote_addr' => $remoteIp
                ]);
            }

            // Verify callback origin (IP whitelist)
            if (!$this->verifyCallbackOrigin($remoteIp)) {
                $this->logger->warning('Somnia Payment Gateway: Callback from unauthorized IP', [
                    'payment_id' => $paymentId,
                    'order_id' => $orderId,
                    'remote_ip' => $remoteIp,
                    'allowed_ips' => $this->config->getAllowedIps()
                ]);
                throw new LocalizedException(__('Unauthorized callback origin'));
            }

            // Load Magento order by increment ID
            $order = $this->loadOrder($orderId);

            if (!$order || !$order->getId()) {
                $this->logger->error('Somnia Payment Gateway: Order not found', [
                    'payment_id' => $paymentId,
                    'order_id' => $orderId
                ]);
                throw new LocalizedException(__('Order not found: %1', $orderId));
            }

            // Verify payment status with gateway
            $this->verifyAndProcessPayment($order, $paymentId);

            return $result->setData([
                'success' => true,
                'message' => 'Payment processed successfully'
            ]);

        } catch (LocalizedException $e) {
            $this->logger->error('Somnia Payment Gateway: Callback error', [
                'error' => $e->getMessage(),
                'payment_id' => $paymentId ?? null,
                'order_id' => $orderId ?? null
            ]);

            return $result->setHttpResponseCode(400)->setData([
                'success' => false,
                'message' => $e->getMessage()
            ]);

        } catch (\Exception $e) {
            $this->logger->critical('Somnia Payment Gateway: Callback exception', [
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            return $result->setHttpResponseCode(500)->setData([
                'success' => false,
                'message' => 'Internal server error'
            ]);
        }
    }

    /**
     * Get remote IP address (handles proxies)
     *
     * @return string
     */
    protected function getRemoteIp()
    {
        $request = $this->getRequest();
        
        // Check for proxy headers (in order of preference)
        $headers = [
            'HTTP_CF_CONNECTING_IP',     // Cloudflare
            'HTTP_X_REAL_IP',             // Nginx proxy
            'HTTP_X_FORWARDED_FOR',       // Standard proxy header
            'REMOTE_ADDR'                 // Direct connection
        ];
        
        foreach ($headers as $header) {
            $ip = $request->getServer($header);
            
            if (!empty($ip)) {
                // X-Forwarded-For can contain multiple IPs, take the first one
                if ($header === 'HTTP_X_FORWARDED_FOR' && strpos($ip, ',') !== false) {
                    $ips = explode(',', $ip);
                    $ip = trim($ips[0]);
                }
                
                // Validate IP format
                if (filter_var($ip, FILTER_VALIDATE_IP)) {
                    return $ip;
                }
            }
        }
        
        return '0.0.0.0';
    }

    /**
     * Verify callback origin
     *
     * @param string $remoteIp
     * @return bool
     */
    protected function verifyCallbackOrigin($remoteIp)
    {
        // If IP whitelist is not configured, allow all IPs
        if (!$this->config->isIpWhitelistEnabled()) {
            return true;
        }

        // Check if IP is in whitelist
        return $this->config->isIpAllowed($remoteIp);
    }

    /**
     * Load order by increment ID
     *
     * @param string $incrementId
     * @return Order|null
     */
    protected function loadOrder($incrementId)
    {
        try {
            $searchCriteria = $this->_objectManager->create(\Magento\Framework\Api\SearchCriteriaBuilder::class)
                ->addFilter('increment_id', $incrementId, 'eq')
                ->create();

            $orders = $this->orderRepository->getList($searchCriteria)->getItems();

            if (empty($orders)) {
                return null;
            }

            return reset($orders);

        } catch (\Exception $e) {
            $this->logger->error('Somnia Payment Gateway: Failed to load order', [
                'increment_id' => $incrementId,
                'error' => $e->getMessage()
            ]);
            return null;
        }
    }

    /**
     * Verify payment with gateway and process order
     *
     * @param Order $order
     * @param string $paymentId
     * @return void
     * @throws LocalizedException
     */
    protected function verifyAndProcessPayment($order, $paymentId)
    {
        $storeId = $order->getStoreId();

        // Call gateway status endpoint to verify payment
        $statusData = $this->gatewayClient->getPaymentStatus($paymentId, $storeId);

        // Parse status response
        $this->statusResponse->parse($statusData);

        if ($this->config->isDebugMode($storeId)) {
            $this->logger->debug('Somnia Payment Gateway: Status verification', [
                'payment_id' => $paymentId,
                'order_id' => $order->getIncrementId(),
                'status' => $this->statusResponse->getStatus(),
                'amount' => $this->statusResponse->getAmount()
            ]);
        }

        // Verify order ID matches
        $responseOrderId = $this->statusResponse->getOrderId();
        if ($responseOrderId && $responseOrderId !== $order->getIncrementId()) {
            throw new LocalizedException(
                __('Order ID mismatch: expected %1, got %2', $order->getIncrementId(), $responseOrderId)
            );
        }

        // Verify payment amount matches order total (with tolerance)
        $this->verifyPaymentAmount($order, $this->statusResponse);

        // Process payment based on status
        $this->processPaymentStatus($order, $this->statusResponse, $paymentId);
    }

    /**
     * Verify payment amount matches order total
     *
     * @param Order $order
     * @param StatusResponse $statusResponse
     * @return void
     * @throws LocalizedException
     */
    protected function verifyPaymentAmount($order, $statusResponse)
    {
        $orderTotal = $order->getGrandTotal();
        $paidAmount = $statusResponse->getAmount();

        if ($paidAmount === null) {
            // If amount is not in response, skip verification
            return;
        }

        // Calculate difference percentage
        $difference = abs($orderTotal - $paidAmount);
        $tolerance = $orderTotal * self::AMOUNT_TOLERANCE;

        if ($difference > $tolerance) {
            throw new LocalizedException(
                __('Payment amount mismatch: order total %1, paid amount %2', $orderTotal, $paidAmount)
            );
        }
    }

    /**
     * Process payment based on status
     *
     * @param Order $order
     * @param StatusResponse $statusResponse
     * @param string $paymentId
     * @return void
     */
    protected function processPaymentStatus($order, $statusResponse, $paymentId)
    {
        $status = $statusResponse->getStatus();
        $storeId = $order->getStoreId();

        if ($this->config->isDebugMode($storeId)) {
            $this->logger->info('Somnia Payment Gateway: Processing payment status', [
                'order_id' => $order->getIncrementId(),
                'payment_id' => $paymentId,
                'status' => $status
            ]);
        }

        switch ($status) {
            case StatusResponse::STATUS_PAID:
                $this->processSuccessfulPayment($order, $statusResponse, $paymentId);
                break;

            case StatusResponse::STATUS_EXPIRED:
            case StatusResponse::STATUS_FAILED:
                $this->processFailedPayment($order, $statusResponse, $paymentId);
                break;

            case StatusResponse::STATUS_PENDING:
                // Payment still pending, no action needed
                $this->logger->info('Somnia Payment Gateway: Payment still pending', [
                    'order_id' => $order->getIncrementId(),
                    'payment_id' => $paymentId
                ]);
                break;

            default:
                $this->logger->warning('Somnia Payment Gateway: Unknown payment status', [
                    'order_id' => $order->getIncrementId(),
                    'payment_id' => $paymentId,
                    'status' => $status
                ]);
                break;
        }
    }

    /**
     * Process successful payment
     *
     * @param Order $order
     * @param StatusResponse $statusResponse
     * @param string $paymentId
     * @return void
     */
    protected function processSuccessfulPayment($order, $statusResponse, $paymentId)
    {
        // Check if order is already processed
        if ($order->getState() === Order::STATE_PROCESSING) {
            $this->logger->info('Somnia Payment Gateway: Order already processed', [
                'order_id' => $order->getIncrementId(),
                'payment_id' => $paymentId
            ]);
            return;
        }

        try {
            // Store payment information in order payment
            $payment = $order->getPayment();
            $additionalInfo = [
                'somnia_payment_id' => $paymentId,
                'somnia_gateway_url' => $this->config->getGatewayUrl($order->getStoreId()),
                'somnia_payment_status' => $statusResponse->getStatus()
            ];

            // Add crypto information if available
            if ($statusResponse->getCryptoSymbol()) {
                $additionalInfo['somnia_crypto_symbol'] = $statusResponse->getCryptoSymbol();
            }

            if ($statusResponse->getCryptoAmount()) {
                $additionalInfo['somnia_crypto_amount'] = $statusResponse->getCryptoAmount();
            }

            if ($statusResponse->getWalletAddress()) {
                $additionalInfo['somnia_wallet_address'] = $statusResponse->getWalletAddress();
            }

            $payment->setAdditionalInformation($additionalInfo);

            // Update order status to Processing
            $order->setState(Order::STATE_PROCESSING);
            $order->setStatus($order->getConfig()->getStateDefaultStatus(Order::STATE_PROCESSING));

            // Add order comment
            $comment = $this->buildPaymentComment($statusResponse, $paymentId);
            $order->addCommentToStatusHistory($comment, false, true);

            // Save order
            $this->orderRepository->save($order);

            // Send order confirmation email
            try {
                if (!$order->getEmailSent()) {
                    $this->orderSender->send($order);
                    $order->addCommentToStatusHistory(
                        __('Order confirmation email sent to customer.')
                    );
                    $this->orderRepository->save($order);
                }
            } catch (\Exception $e) {
                $this->logger->error('Somnia Payment Gateway: Failed to send order confirmation email', [
                    'order_id' => $order->getIncrementId(),
                    'error' => $e->getMessage()
                ]);
            }

            $this->logger->info('Somnia Payment Gateway: Payment successful', [
                'order_id' => $order->getIncrementId(),
                'payment_id' => $paymentId,
                'crypto_symbol' => $statusResponse->getCryptoSymbol(),
                'crypto_amount' => $statusResponse->getCryptoAmount()
            ]);

        } catch (\Exception $e) {
            $this->logger->error('Somnia Payment Gateway: Failed to process successful payment', [
                'order_id' => $order->getIncrementId(),
                'payment_id' => $paymentId,
                'error' => $e->getMessage()
            ]);
            throw new LocalizedException(__('Failed to update order status'));
        }
    }

    /**
     * Process failed or expired payment
     *
     * @param Order $order
     * @param StatusResponse $statusResponse
     * @param string $paymentId
     * @return void
     */
    protected function processFailedPayment($order, $statusResponse, $paymentId)
    {
        // Check if order is already canceled
        if ($order->getState() === Order::STATE_CANCELED) {
            $this->logger->info('Somnia Payment Gateway: Order already canceled', [
                'order_id' => $order->getIncrementId(),
                'payment_id' => $paymentId
            ]);
            return;
        }

        try {
            // Store payment information
            $payment = $order->getPayment();
            $additionalInfo = [
                'somnia_payment_id' => $paymentId,
                'somnia_gateway_url' => $this->config->getGatewayUrl($order->getStoreId()),
                'somnia_payment_status' => $statusResponse->getStatus()
            ];

            $payment->setAdditionalInformation($additionalInfo);

            // Cancel order
            $order->cancel();

            // Add order comment
            $comment = sprintf(
                'Payment %s. Payment ID: %s',
                $statusResponse->getStatus() === StatusResponse::STATUS_EXPIRED ? 'expired' : 'failed',
                $paymentId
            );
            $order->addCommentToStatusHistory($comment, false, true);

            // Save order
            $this->orderRepository->save($order);

            $this->logger->info('Somnia Payment Gateway: Payment failed/expired', [
                'order_id' => $order->getIncrementId(),
                'payment_id' => $paymentId,
                'status' => $statusResponse->getStatus()
            ]);

        } catch (\Exception $e) {
            $this->logger->error('Somnia Payment Gateway: Failed to process failed payment', [
                'order_id' => $order->getIncrementId(),
                'payment_id' => $paymentId,
                'error' => $e->getMessage()
            ]);
            throw new LocalizedException(__('Failed to cancel order'));
        }
    }

    /**
     * Build payment comment for order history
     *
     * @param StatusResponse $statusResponse
     * @param string $paymentId
     * @return string
     */
    protected function buildPaymentComment($statusResponse, $paymentId)
    {
        $comment = sprintf('Cryptocurrency payment completed. Payment ID: %s', $paymentId);

        if ($statusResponse->getCryptoSymbol() && $statusResponse->getCryptoAmount()) {
            $comment .= sprintf(
                ' | Amount: %s %s',
                $statusResponse->getCryptoAmount(),
                $statusResponse->getCryptoSymbol()
            );
        }

        if ($statusResponse->getWalletAddress()) {
            $comment .= sprintf(' | Wallet: %s', $statusResponse->getWalletAddress());
        }

        return $comment;
    }
}
