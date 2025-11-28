<?php
/**
 * Somnia Payment Gateway - Custom Log Handler
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Logger;

use Magento\Framework\Logger\Handler\Base;
use Monolog\Logger;

/**
 * Custom log handler for Somnia payment gateway
 */
class Handler extends Base
{
    /**
     * Logging level
     *
     * @var int
     */
    protected $loggerType = Logger::INFO;

    /**
     * Log file name
     *
     * @var string
     */
    protected $fileName = '/var/log/somnia_payment.log';
}
