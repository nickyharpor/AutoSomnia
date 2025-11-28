<?php
/**
 * Copyright © Somnia. All rights reserved.
 * Plugin to add payment information to order emails
 */
namespace Somnia\PaymentGateway\Plugin;

use Magento\Sales\Model\Order\Email\Container\OrderIdentity;
use Magento\Sales\Model\Order\Email\Sender\OrderSender;
use Somnia\PaymentGateway\Model\Payment;
use Magento\Framework\View\LayoutInterface;

class AddPaymentInfoToOrderEmail
{
    /**
     * @var LayoutInterface
     */
    protected $layout;

    /**
     * Constructor
     *
     * @param LayoutInterface $layout
     */
    public function __construct(LayoutInterface $layout)
    {
        $this->layout = $layout;
    }

    /**
     * Add payment information to order email
     *
     * @param OrderSender $subject
     * @param \Closure $proceed
     * @param \Magento\Sales\Model\Order $order
     * @param bool $forceSyncMode
     * @return bool
     */
    public function aroundSend(
        OrderSender $subject,
        \Closure $proceed,
        \Magento\Sales\Model\Order $order,
        $forceSyncMode = false
    ) {
        // Check if this is a Somnia payment
        if ($order->getPayment()->getMethod() === Payment::CODE) {
            // Get payment info block
            $block = $this->layout->createBlock(
                \Somnia\PaymentGateway\Block\Email\PaymentInfo::class
            );
            $block->setOrder($order);

            // Add payment info to order email variables
            $payment = $order->getPayment();
            $additionalInfo = $payment->getAdditionalInformation();
            $paymentStatus = $additionalInfo['somnia_payment_status'] ?? '';

            // Store payment info in order for email template access
            $order->setData('somnia_payment_info', [
                'is_pending' => empty($paymentStatus) || $paymentStatus === 'PENDING',
                'is_confirmed' => $paymentStatus === 'PAID',
                'payment_id' => $additionalInfo['somnia_payment_id'] ?? '',
                'crypto_symbol' => $additionalInfo['somnia_crypto_symbol'] ?? 'SOMI',
                'crypto_amount' => $additionalInfo['somnia_crypto_amount'] ?? '',
                'payment_timeout' => $block->getPaymentTimeout(),
                'payment_method_title' => $block->getPaymentMethodTitle()
            ]);
        }

        return $proceed($order, $forceSyncMode);
    }
}
