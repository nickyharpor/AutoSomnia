<?php
/**
 * Somnia Payment Gateway - Payment Request Builder
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Model\Gateway\Request;

use Magento\Framework\Exception\LocalizedException;

/**
 * Payment request parameter builder
 */
class PaymentRequest
{
    /**
     * @var string
     */
    protected $orderId;

    /**
     * @var float
     */
    protected $amount;

    /**
     * @var int
     */
    protected $merchantId;

    /**
     * Build payment request parameters
     *
     * @param string $orderId Magento order ID
     * @param float $amount Order total amount in dollars
     * @param int $merchantId Merchant ID
     * @return $this
     * @throws LocalizedException
     */
    public function build($orderId, $amount, $merchantId)
    {
        $this->validateOrderId($orderId);
        $this->validateAmount($amount);
        $this->validateMerchantId($merchantId);

        $this->orderId = $orderId;
        $this->amount = $amount;
        $this->merchantId = $merchantId;

        return $this;
    }

    /**
     * Get request parameters as array
     *
     * @return array
     * @throws LocalizedException
     */
    public function getParameters()
    {
        if (empty($this->orderId) || empty($this->amount) || empty($this->merchantId)) {
            throw new LocalizedException(__('Payment request not built. Call build() first.'));
        }

        return [
            'price' => $this->getPriceInCents(),
            'merchant' => $this->merchantId,
            'order_id' => $this->orderId
        ];
    }

    /**
     * Get price in cents
     *
     * @return int
     */
    public function getPriceInCents()
    {
        return (int)round($this->amount * 100);
    }

    /**
     * Get order ID
     *
     * @return string
     */
    public function getOrderId()
    {
        return $this->orderId;
    }

    /**
     * Get amount
     *
     * @return float
     */
    public function getAmount()
    {
        return $this->amount;
    }

    /**
     * Get merchant ID
     *
     * @return int
     */
    public function getMerchantId()
    {
        return $this->merchantId;
    }

    /**
     * Validate order ID
     *
     * @param string $orderId
     * @return void
     * @throws LocalizedException
     */
    protected function validateOrderId($orderId)
    {
        if (empty($orderId)) {
            throw new LocalizedException(__('Order ID is required'));
        }

        if (!is_string($orderId) && !is_numeric($orderId)) {
            throw new LocalizedException(__('Order ID must be a string or number'));
        }
    }

    /**
     * Validate amount
     *
     * @param float $amount
     * @return void
     * @throws LocalizedException
     */
    protected function validateAmount($amount)
    {
        if (!is_numeric($amount)) {
            throw new LocalizedException(__('Amount must be numeric'));
        }

        if ($amount <= 0) {
            throw new LocalizedException(__('Amount must be greater than zero'));
        }
    }

    /**
     * Validate merchant ID
     *
     * @param int $merchantId
     * @return void
     * @throws LocalizedException
     */
    protected function validateMerchantId($merchantId)
    {
        if (empty($merchantId)) {
            throw new LocalizedException(__('Merchant ID is required'));
        }

        if (!is_numeric($merchantId)) {
            throw new LocalizedException(__('Merchant ID must be numeric'));
        }

        if ((int)$merchantId <= 0) {
            throw new LocalizedException(__('Merchant ID must be a positive integer'));
        }
    }
}
