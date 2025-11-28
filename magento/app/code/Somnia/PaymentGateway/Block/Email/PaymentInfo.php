<?php
/**
 * Copyright © Somnia. All rights reserved.
 * Payment Information Block for Email Templates
 */
namespace Somnia\PaymentGateway\Block\Email;

use Magento\Framework\View\Element\Template;
use Magento\Framework\View\Element\Template\Context;
use Somnia\PaymentGateway\Model\Config;
use Somnia\PaymentGateway\Model\Gateway\Client;

class PaymentInfo extends Template
{
    /**
     * @var Config
     */
    protected $config;

    /**
     * @var Client
     */
    protected $gatewayClient;

    /**
     * @var \Magento\Sales\Model\Order
     */
    protected $order;

    /**
     * Constructor
     *
     * @param Context $context
     * @param Config $config
     * @param Client $gatewayClient
     * @param array $data
     */
    public function __construct(
        Context $context,
        Config $config,
        Client $gatewayClient,
        array $data = []
    ) {
        $this->config = $config;
        $this->gatewayClient = $gatewayClient;
        parent::__construct($context, $data);
    }

    /**
     * Set order
     *
     * @param \Magento\Sales\Model\Order $order
     * @return $this
     */
    public function setOrder($order)
    {
        $this->order = $order;
        return $this;
    }

    /**
     * Get order
     *
     * @return \Magento\Sales\Model\Order
     */
    public function getOrder()
    {
        return $this->order;
    }

    /**
     * Get payment URL for the order
     *
     * @return string
     */
    public function getPaymentUrl()
    {
        if (!$this->order) {
            return '';
        }

        $payment = $this->order->getPayment();
        $additionalInfo = $payment->getAdditionalInformation();

        // Check if payment URL is already stored
        if (isset($additionalInfo['somnia_redirect_url'])) {
            return $additionalInfo['somnia_redirect_url'];
        }

        // Build payment URL
        try {
            return $this->gatewayClient->buildPaymentUrl(
                $this->order->getIncrementId(),
                $this->order->getGrandTotal()
            );
        } catch (\Exception $e) {
            return '';
        }
    }

    /**
     * Get payment timeout in minutes
     *
     * @return int
     */
    public function getPaymentTimeout()
    {
        return $this->config->getPaymentTimeout();
    }

    /**
     * Get payment ID from order
     *
     * @return string
     */
    public function getPaymentId()
    {
        if (!$this->order) {
            return '';
        }

        $payment = $this->order->getPayment();
        $additionalInfo = $payment->getAdditionalInformation();

        return $additionalInfo['somnia_payment_id'] ?? '';
    }

    /**
     * Get cryptocurrency symbol
     *
     * @return string
     */
    public function getCryptoSymbol()
    {
        if (!$this->order) {
            return 'SOMI';
        }

        $payment = $this->order->getPayment();
        $additionalInfo = $payment->getAdditionalInformation();

        return $additionalInfo['somnia_crypto_symbol'] ?? 'SOMI';
    }

    /**
     * Get cryptocurrency amount
     *
     * @return string
     */
    public function getCryptoAmount()
    {
        if (!$this->order) {
            return '';
        }

        $payment = $this->order->getPayment();
        $additionalInfo = $payment->getAdditionalInformation();

        return $additionalInfo['somnia_crypto_amount'] ?? '';
    }

    /**
     * Get payment method title
     *
     * @return string
     */
    public function getPaymentMethodTitle()
    {
        if (!$this->order) {
            return 'Cryptocurrency Payment (SOMI)';
        }

        return $this->order->getPayment()->getMethodInstance()->getTitle();
    }

    /**
     * Check if payment is pending
     *
     * @return bool
     */
    public function isPaymentPending()
    {
        if (!$this->order) {
            return false;
        }

        $payment = $this->order->getPayment();
        $additionalInfo = $payment->getAdditionalInformation();
        $status = $additionalInfo['somnia_payment_status'] ?? '';

        return empty($status) || $status === 'PENDING';
    }

    /**
     * Check if payment is confirmed
     *
     * @return bool
     */
    public function isPaymentConfirmed()
    {
        if (!$this->order) {
            return false;
        }

        $payment = $this->order->getPayment();
        $additionalInfo = $payment->getAdditionalInformation();
        $status = $additionalInfo['somnia_payment_status'] ?? '';

        return $status === 'PAID';
    }
}
