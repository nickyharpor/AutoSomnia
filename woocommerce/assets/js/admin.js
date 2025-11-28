/**
 * Somnia Payment Gateway - Admin JavaScript
 */

(function($) {
    'use strict';

    /**
     * Gateway Settings Handler
     */
    const SomniaGatewayAdmin = {
        
        /**
         * Initialize
         */
        init: function() {
            this.bindEvents();
            this.checkConnection();
        },

        /**
         * Bind event handlers
         */
        bindEvents: function() {
            // Test connection button
            $(document).on('click', '.somnia-test-connection-btn', this.testConnection.bind(this));

            // Gateway URL change
            $('#woocommerce_somnia_gateway_url').on('change', this.onGatewayUrlChange.bind(this));

            // Merchant ID change
            $('#woocommerce_somnia_merchant_id').on('change', this.onMerchantIdChange.bind(this));

            // Save settings
            $('button[name="save"]').on('click', this.onSaveSettings.bind(this));
        },

        /**
         * Check gateway connection status
         */
        checkConnection: function() {
            const gatewayUrl = $('#woocommerce_somnia_gateway_url').val();
            const merchantId = $('#woocommerce_somnia_merchant_id').val();

            if (!gatewayUrl || !merchantId) {
                return;
            }

            // Show loading state
            this.showConnectionStatus('checking', 'Checking connection...');

            // Check health endpoint
            $.ajax({
                url: gatewayUrl + '/health',
                method: 'GET',
                timeout: 5000,
                success: function(response) {
                    if (response.status === 'healthy') {
                        this.showConnectionStatus('connected', 'Connected to gateway');
                    } else {
                        this.showConnectionStatus('disconnected', 'Gateway unhealthy');
                    }
                }.bind(this),
                error: function() {
                    this.showConnectionStatus('disconnected', 'Cannot connect to gateway');
                }.bind(this)
            });
        },

        /**
         * Test connection button handler
         */
        testConnection: function(e) {
            e.preventDefault();

            const gatewayUrl = $('#woocommerce_somnia_gateway_url').val();
            const merchantId = $('#woocommerce_somnia_merchant_id').val();

            if (!gatewayUrl) {
                alert('Please enter a Gateway URL');
                return;
            }

            if (!merchantId) {
                alert('Please enter a Merchant ID');
                return;
            }

            // Show loading
            const $button = $(e.currentTarget);
            const originalText = $button.text();
            $button.text('Testing...').prop('disabled', true);

            // Test health endpoint
            $.ajax({
                url: gatewayUrl + '/health',
                method: 'GET',
                timeout: 10000,
                success: function(response) {
                    if (response.status === 'healthy') {
                        alert('✓ Connection successful!\n\nGateway is healthy and responding.');
                        this.showConnectionStatus('connected', 'Connected to gateway');
                    } else {
                        alert('⚠ Gateway responded but is unhealthy.\n\nStatus: ' + response.status);
                        this.showConnectionStatus('disconnected', 'Gateway unhealthy');
                    }
                }.bind(this),
                error: function(xhr, status, error) {
                    let message = '✗ Connection failed!\n\n';
                    
                    if (status === 'timeout') {
                        message += 'Request timed out. Check if the gateway is running.';
                    } else if (xhr.status === 0) {
                        message += 'Cannot reach gateway. Check the URL and network connection.';
                    } else {
                        message += 'Error: ' + error;
                    }
                    
                    alert(message);
                    this.showConnectionStatus('disconnected', 'Cannot connect to gateway');
                }.bind(this),
                complete: function() {
                    $button.text(originalText).prop('disabled', false);
                }
            });
        },

        /**
         * Show connection status
         */
        showConnectionStatus: function(status, message) {
            let $statusEl = $('.somnia-connection-status');
            
            if ($statusEl.length === 0) {
                // Create status element if it doesn't exist
                const $container = $('#woocommerce_somnia_gateway_url').closest('tr');
                $statusEl = $('<div class="somnia-connection-status"></div>');
                $container.find('td').append($statusEl);
            }

            // Update status
            $statusEl
                .removeClass('connected disconnected checking')
                .addClass(status)
                .text(message);
        },

        /**
         * Gateway URL change handler
         */
        onGatewayUrlChange: function() {
            // Clear connection status
            $('.somnia-connection-status').remove();
        },

        /**
         * Merchant ID change handler
         */
        onMerchantIdChange: function() {
            // Clear connection status
            $('.somnia-connection-status').remove();
        },

        /**
         * Save settings handler
         */
        onSaveSettings: function() {
            // Validate before saving
            const gatewayUrl = $('#woocommerce_somnia_gateway_url').val();
            const merchantId = $('#woocommerce_somnia_merchant_id').val();
            const enabled = $('#woocommerce_somnia_enabled').is(':checked');

            if (enabled) {
                if (!gatewayUrl) {
                    alert('Gateway URL is required when the payment method is enabled.');
                    return false;
                }

                if (!merchantId) {
                    alert('Merchant ID is required when the payment method is enabled.');
                    return false;
                }

                // Validate URL format
                try {
                    new URL(gatewayUrl);
                } catch (e) {
                    alert('Gateway URL must be a valid URL (e.g., http://localhost:5000)');
                    return false;
                }
            }
        }
    };

    /**
     * Order Details Handler
     */
    const SomniaOrderDetails = {
        
        /**
         * Initialize
         */
        init: function() {
            this.bindEvents();
        },

        /**
         * Bind event handlers
         */
        bindEvents: function() {
            // Check payment status button
            $(document).on('click', '.somnia-check-status-btn', this.checkPaymentStatus.bind(this));

            // Copy payment ID
            $(document).on('click', '.somnia-copy-payment-id', this.copyPaymentId.bind(this));
        },

        /**
         * Check payment status
         */
        checkPaymentStatus: function(e) {
            e.preventDefault();

            const $button = $(e.currentTarget);
            const paymentId = $button.data('payment-id');
            const gatewayUrl = $button.data('gateway-url');

            if (!paymentId || !gatewayUrl) {
                return;
            }

            // Show loading
            const originalText = $button.text();
            $button.text('Checking...').prop('disabled', true);

            // Check status
            $.ajax({
                url: gatewayUrl + '/status/' + paymentId,
                method: 'GET',
                timeout: 10000,
                success: function(response) {
                    alert('Payment Status: ' + response.status + '\n\n' +
                          'Balance: ' + response.balance + ' SOMI\n' +
                          'Required: ' + response.required_amount + ' SOMI\n' +
                          'Complete: ' + (response.is_complete ? 'Yes' : 'No'));
                },
                error: function() {
                    alert('Failed to check payment status. Please try again.');
                },
                complete: function() {
                    $button.text(originalText).prop('disabled', false);
                }
            });
        },

        /**
         * Copy payment ID to clipboard
         */
        copyPaymentId: function(e) {
            e.preventDefault();

            const $button = $(e.currentTarget);
            const paymentId = $button.data('payment-id');

            // Create temporary input
            const $temp = $('<input>');
            $('body').append($temp);
            $temp.val(paymentId).select();
            document.execCommand('copy');
            $temp.remove();

            // Show feedback
            const originalText = $button.text();
            $button.text('Copied!');
            setTimeout(function() {
                $button.text(originalText);
            }, 2000);
        }
    };

    /**
     * Initialize on document ready
     */
    $(document).ready(function() {
        // Check if we're on the gateway settings page
        if ($('#woocommerce_somnia_enabled').length) {
            SomniaGatewayAdmin.init();
        }

        // Check if we're on an order details page
        if ($('.somnia-payment-info').length) {
            SomniaOrderDetails.init();
        }
    });

})(jQuery);
