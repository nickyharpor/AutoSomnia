/**
 * Somnia Payment Gateway - Payment Method Loader
 * 
 * This component registers the Somnia payment method renderer with Magento's checkout.
 */
define(
    [
        'uiComponent',
        'Magento_Checkout/js/model/payment/renderer-list'
    ],
    function (
        Component,
        rendererList
    ) {
        'use strict';

        // Register the payment method renderer
        rendererList.push(
            {
                type: 'somnia_gateway',
                component: 'Somnia_PaymentGateway/js/view/payment/method-renderer/somnia-gateway'
            }
        );

        /** Add view logic here if needed */
        return Component.extend({});
    }
);
