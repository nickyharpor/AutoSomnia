<?php
/**
 * Somnia Payment Gateway - HTTPS Warning Block
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Block\Adminhtml\System\Config;

use Magento\Config\Block\System\Config\Form\Field;
use Magento\Framework\Data\Form\Element\AbstractElement;
use Somnia\PaymentGateway\Model\Config;

/**
 * Display HTTPS warning in admin configuration
 */
class HttpsWarning extends Field
{
    /**
     * @var Config
     */
    protected $config;

    /**
     * @param \Magento\Backend\Block\Template\Context $context
     * @param Config $config
     * @param array $data
     */
    public function __construct(
        \Magento\Backend\Block\Template\Context $context,
        Config $config,
        array $data = []
    ) {
        parent::__construct($context, $data);
        $this->config = $config;
    }

    /**
     * Render element
     *
     * @param AbstractElement $element
     * @return string
     */
    protected function _getElementHtml(AbstractElement $element)
    {
        // Check if gateway URL uses HTTP and is not localhost
        if (!$this->config->isSecureConnection() && !$this->config->isLocalhostGateway()) {
            $warningMessage = __(
                'Warning: Your gateway URL is using HTTP instead of HTTPS. ' .
                'This is insecure and should only be used for development. ' .
                'Please use HTTPS for production environments to protect sensitive payment data.'
            );

            return sprintf(
                '<div class="message message-warning warning" style="margin-top: 10px;">
                    <strong>%s</strong> %s
                </div>',
                __('Security Warning:'),
                $warningMessage
            );
        }

        return '';
    }
}
