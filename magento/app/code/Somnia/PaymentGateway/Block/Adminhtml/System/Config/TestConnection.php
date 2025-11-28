<?php
/**
 * Somnia Payment Gateway - Test Connection Block
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Block\Adminhtml\System\Config;

use Magento\Config\Block\System\Config\Form\Field;
use Magento\Framework\Data\Form\Element\AbstractElement;

/**
 * Test connection button in admin configuration
 */
class TestConnection extends Field
{
    /**
     * Template path
     *
     * @var string
     */
    protected $_template = 'Somnia_PaymentGateway::system/config/test-connection.phtml';

    /**
     * Remove scope label
     *
     * @param AbstractElement $element
     * @return string
     */
    public function render(AbstractElement $element)
    {
        $element->unsScope()->unsCanUseWebsiteValue()->unsCanUseDefaultValue();
        return parent::render($element);
    }

    /**
     * Return element html
     *
     * @param AbstractElement $element
     * @return string
     */
    protected function _getElementHtml(AbstractElement $element)
    {
        return $this->_toHtml();
    }

    /**
     * Get AJAX URL for test connection
     *
     * @return string
     */
    public function getAjaxUrl()
    {
        return $this->getUrl('somnia_gateway/system_config/testconnection');
    }

    /**
     * Generate button HTML
     *
     * @return string
     */
    public function getButtonHtml()
    {
        $button = $this->getLayout()->createBlock(
            \Magento\Backend\Block\Widget\Button::class
        )->setData(
            [
                'id' => 'somnia_test_connection_button',
                'label' => __('Test Connection'),
                'onclick' => 'javascript:testSomniaConnection(); return false;'
            ]
        );

        return $button->toHtml();
    }
}
