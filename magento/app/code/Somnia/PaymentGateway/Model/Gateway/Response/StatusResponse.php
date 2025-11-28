<?php
/**
 * Somnia Payment Gateway - Status Response Parser
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Model\Gateway\Response;

use Magento\Framework\Exception\LocalizedException;

/**
 * Payment status response parser
 */
class StatusResponse
{
    /**
     * Payment status constants
     */
    const STATUS_PAID = 'PAID';
    const STATUS_PENDING = 'PENDING';
    const STATUS_EXPIRED = 'EXPIRED';
    const STATUS_FAILED = 'FAILED';

    /**
     * @var array
     */
    protected $data;

    /**
     * Parse status response
     *
     * @param array|string $response Response data (array or JSON string)
     * @return $this
     * @throws LocalizedException
     */
    public function parse($response)
    {
        // If response is a JSON string, decode it
        if (is_string($response)) {
            $data = json_decode($response, true);
            
            if (json_last_error() !== JSON_ERROR_NONE) {
                throw new LocalizedException(
                    __('Invalid JSON response: %1', json_last_error_msg())
                );
            }
        } elseif (is_array($response)) {
            $data = $response;
        } else {
            throw new LocalizedException(__('Response must be an array or JSON string'));
        }

        $this->validateResponse($data);
        $this->data = $data;

        return $this;
    }

    /**
     * Get payment status
     *
     * @return string
     * @throws LocalizedException
     */
    public function getStatus()
    {
        $this->ensureParsed();
        return isset($this->data['status']) ? (string)$this->data['status'] : '';
    }

    /**
     * Get payment ID
     *
     * @return string|null
     */
    public function getPaymentId()
    {
        $this->ensureParsed();
        return isset($this->data['payment_id']) ? (string)$this->data['payment_id'] : null;
    }

    /**
     * Get order ID
     *
     * @return string|null
     */
    public function getOrderId()
    {
        $this->ensureParsed();
        return isset($this->data['order_id']) ? (string)$this->data['order_id'] : null;
    }

    /**
     * Get cryptocurrency symbol
     *
     * @return string|null
     */
    public function getCryptoSymbol()
    {
        $this->ensureParsed();
        return isset($this->data['crypto_symbol']) ? (string)$this->data['crypto_symbol'] : null;
    }

    /**
     * Get cryptocurrency amount
     *
     * @return float|null
     */
    public function getCryptoAmount()
    {
        $this->ensureParsed();
        
        if (!isset($this->data['balance'])) {
            return null;
        }

        return (float)$this->data['balance'];
    }

    /**
     * Get payment amount in USD
     *
     * @return float|null
     */
    public function getAmount()
    {
        $this->ensureParsed();
        
        if (!isset($this->data['price'])) {
            return null;
        }

        // Convert cents to dollars
        return (float)$this->data['price'] / 100;
    }

    /**
     * Get merchant ID
     *
     * @return int|null
     */
    public function getMerchantId()
    {
        $this->ensureParsed();
        return isset($this->data['merchant']) ? (int)$this->data['merchant'] : null;
    }

    /**
     * Get wallet address
     *
     * @return string|null
     */
    public function getWalletAddress()
    {
        $this->ensureParsed();
        return isset($this->data['wallet_address']) ? (string)$this->data['wallet_address'] : null;
    }

    /**
     * Get created timestamp
     *
     * @return string|null
     */
    public function getCreatedAt()
    {
        $this->ensureParsed();
        return isset($this->data['created_at']) ? (string)$this->data['created_at'] : null;
    }

    /**
     * Get updated timestamp
     *
     * @return string|null
     */
    public function getUpdatedAt()
    {
        $this->ensureParsed();
        return isset($this->data['updated_at']) ? (string)$this->data['updated_at'] : null;
    }

    /**
     * Check if payment is paid
     *
     * @return bool
     */
    public function isPaid()
    {
        try {
            return $this->getStatus() === self::STATUS_PAID;
        } catch (LocalizedException $e) {
            return false;
        }
    }

    /**
     * Check if payment is pending
     *
     * @return bool
     */
    public function isPending()
    {
        try {
            return $this->getStatus() === self::STATUS_PENDING;
        } catch (LocalizedException $e) {
            return false;
        }
    }

    /**
     * Check if payment is expired
     *
     * @return bool
     */
    public function isExpired()
    {
        try {
            return $this->getStatus() === self::STATUS_EXPIRED;
        } catch (LocalizedException $e) {
            return false;
        }
    }

    /**
     * Check if payment is failed
     *
     * @return bool
     */
    public function isFailed()
    {
        try {
            return $this->getStatus() === self::STATUS_FAILED;
        } catch (LocalizedException $e) {
            return false;
        }
    }

    /**
     * Get all response data
     *
     * @return array
     */
    public function getData()
    {
        $this->ensureParsed();
        return $this->data;
    }

    /**
     * Validate response data
     *
     * @param array $data
     * @return void
     * @throws LocalizedException
     */
    protected function validateResponse($data)
    {
        if (!is_array($data)) {
            throw new LocalizedException(__('Response data must be an array'));
        }

        // Status is required
        if (!isset($data['status'])) {
            throw new LocalizedException(__('Response missing required field: status'));
        }

        // Validate status value
        $validStatuses = [
            self::STATUS_PAID,
            self::STATUS_PENDING,
            self::STATUS_EXPIRED,
            self::STATUS_FAILED
        ];

        if (!in_array($data['status'], $validStatuses)) {
            throw new LocalizedException(
                __('Invalid payment status: %1', $data['status'])
            );
        }
    }

    /**
     * Ensure response has been parsed
     *
     * @return void
     * @throws LocalizedException
     */
    protected function ensureParsed()
    {
        if ($this->data === null) {
            throw new LocalizedException(__('Response not parsed. Call parse() first.'));
        }
    }
}
