<?php
/**
 * Copyright © Somnia. All rights reserved.
 * Observer to send payment instructions email after order placement
 */
namespace Somnia\PaymentGateway\Observer;

use Magento\Framework\Event\Observer;
use Magento\Framework\Event\ObserverInterface;
use Magento\Sales\Model\Order;
use Somnia\PaymentGateway\Model\Payment;
use Somnia\PaymentGateway\Model\Config;
use Magento\Framework\Mail\Template\TransportBuilder;
use Magento\Framework\Translate\Inline\StateInterface;
use Magento\Store\Model\StoreManagerInterface;
use Psr\Log\LoggerInterface;

class SendPaymentInstructionsEmail implements ObserverInterface
{
    /**
     * @var Config
     */
    protected $config;

    /**
     * @var TransportBuilder
     */
    protected $transportBuilder;

    /**
     * @var StateInterface
     */
    protected $inlineTranslation;

    /**
     * @var StoreManagerInterface
     */
    protected $storeManager;

    /**
     * @var LoggerInterface
     */
    protected $logger;

    /**
     * Constructor
     *
     * @param Config $config
     * @param TransportBuilder $transportBuilder
     * @param StateInterface $inlineTranslation
     * @param StoreManagerInterface $storeManager
     * @param LoggerInterface $logger
     */
    public function __construct(
        Config $config,
        TransportBuilder $transportBuilder,
        StateInterface $inlineTranslation,
        StoreManagerInterface $storeManager,
        LoggerInterface $logger
    ) {
        $this->config = $config;
        $this->transportBuilder = $transportBuilder;
        $this->inlineTranslation = $inlineTranslation;
        $this->storeManager = $storeManager;
        $this->logger = $logger;
    }

    /**
     * Send payment instructions email after order is placed
     *
     * @param Observer $observer
     * @return void
     */
    public function execute(Observer $observer)
    {
        /** @var Order $order */
        $order = $observer->getEvent()->getOrder();

        // Only send email for Somnia payment method
        if ($order->getPayment()->getMethod() !== Payment::CODE) {
            return;
        }

        // Only send if order is in pending payment status
        if ($order->getState() !== Order::STATE_PENDING_PAYMENT) {
            return;
        }

        try {
            $this->inlineTranslation->suspend();

            $payment = $order->getPayment();
            $additionalInfo = $payment->getAdditionalInformation();
            $paymentUrl = $additionalInfo['somnia_redirect_url'] ?? '';

            $templateVars = [
                'order' => $order,
                'payment' => $payment,
                'payment_url' => $paymentUrl,
                'payment_timeout' => $this->config->getPaymentTimeout($order->getStoreId()),
                'store' => $this->storeManager->getStore($order->getStoreId())
            ];

            $transport = $this->transportBuilder
                ->setTemplateIdentifier('somnia_payment_instructions')
                ->setTemplateOptions([
                    'area' => \Magento\Framework\App\Area::AREA_FRONTEND,
                    'store' => $order->getStoreId()
                ])
                ->setTemplateVars($templateVars)
                ->setFromByScope('sales')
                ->addTo($order->getCustomerEmail(), $order->getCustomerName())
                ->getTransport();

            $transport->sendMessage();

            $this->inlineTranslation->resume();

            // Add order comment
            $order->addCommentToStatusHistory(
                __('Payment instructions email sent to customer.')
            );
            $order->save();

            if ($this->config->isDebugMode($order->getStoreId())) {
                $this->logger->info(
                    'Payment instructions email sent for order #' . $order->getIncrementId()
                );
            }
        } catch (\Exception $e) {
            $this->inlineTranslation->resume();
            $this->logger->error(
                'Failed to send payment instructions email for order #' . $order->getIncrementId() . ': ' . $e->getMessage()
            );
        }
    }
}
