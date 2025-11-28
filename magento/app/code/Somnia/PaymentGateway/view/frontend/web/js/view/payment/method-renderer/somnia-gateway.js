/**
 * Somnia Payment Gateway - Payment Method Renderer
 * 
 * This component renders the Somnia cryptocurrency payment method in the Magento checkout.
 * It extends the default payment renderer and handles the payment method selection and
 * redirect to the gateway on order placement.
 */
define(
    [
        'Magento_Checkout/js/view/payment/default',
        'mage/url'
    ],
    function (Component, url) {
        'use strict';

        return Component.extend({
            defaults: {
                template: 'Somnia_PaymentGateway/payment/somnia-gateway'
            },

            /**
             * Get payment method code
             * @returns {String}
             */
            getCode: function () {
                return 'somnia_gateway';
            },

            /**
             * Get payment method data
             * @returns {Object}
             */
            getData: function () {
                return {
                    'method': this.item.method,
                    'additional_data': null
                };
            },

            /**
             * Get payment method title
             * @returns {String}
             */
            getTitle: function () {
                return this.item.title;
            },

            /**
             * Check if payment method is available
             * @returns {Boolean}
             */
            isAvailable: function () {
                return true;
            },

            /**
             * After place order callback
             * Redirects customer to the payment gateway
             */
            afterPlaceOrder: function () {
                // Redirect to payment gateway will be handled by the payment method
                // The redirect URL is set in the payment method model
                window.location.replace(url.build('somnia/payment/redirect'));
            },

            /**
             * Get payment method instructions
             * @returns {String}
             */
            getInstructions: function () {
                return this.item.instructions || '';
            },

            /**
             * Get payment method logo URL
             * @returns {String}
             */
            getLogoUrl: function () {
                return require.toUrl('Somnia_PaymentGateway/images/somnia-logo.svg');
            }
        });
    }
);
