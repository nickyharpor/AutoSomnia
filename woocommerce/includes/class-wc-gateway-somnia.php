<?php
/**
 * Somnia Payment Gateway Class
 *
 * Handles the payment gateway integration with WooCommerce
 */

if (!defined('ABSPATH')) {
    exit;
}

class WC_Gateway_Somnia extends WC_Payment_Gateway {

    /**
     * Gateway URL
     * @var string
     */
    protected $gateway_url;

    /**
     * Merchant ID
     * @var string
     */
    protected $merchant_id;

    /**
     * Payment timeout in minutes
     * @var int
     */
    protected $payment_timeout;

    /**
     * Debug mode
     * @var bool
     */
    protected $debug_mode;

    /**
     * Constructor
     */
    public function __construct() {
        $this->id = 'somnia';
        $this->icon = SOMNIA_GATEWAY_PLUGIN_URL . 'assets/images/somnia-icon.png';
        $this->has_fields = false;
        $this->method_title = __('Somnia Payment Gateway', 'somnia-payment-gateway');
        $this->method_description = __('Accept cryptocurrency payments (SOMI) through Somnia Payment Gateway', 'somnia-payment-gateway');

        // Load the settings
        $this->init_form_fields();
        $this->init_settings();

        // Define user set variables
        $this->title = $this->get_option('title');
        $this->description = $this->get_option('description');
        $this->gateway_url = $this->get_option('gateway_url');
        $this->merchant_id = $this->get_option('merchant_id');
        $this->payment_timeout = $this->get_option('payment_timeout', '30');
        $this->debug_mode = 'yes' === $this->get_option('debug_mode', 'no');

        // Actions
        add_action('woocommerce_update_options_payment_gateways_' . $this->id, array($this, 'process_admin_options'));
        add_action('woocommerce_api_wc_gateway_somnia', array($this, 'handle_callback'));
        add_action('woocommerce_thankyou_' . $this->id, array($this, 'thankyou_page'));

        // Customer emails
        add_action('woocommerce_email_before_order_table', array($this, 'email_instructions'), 10, 3);
    }

    /**
     * Initialize Gateway Settings Form Fields
     */
    public function init_form_fields() {
        $this->form_fields = array(
            'enabled' => array(
                'title' => __('Enable/Disable', 'somnia-payment-gateway'),
                'type' => 'checkbox',
                'label' => __('Enable Somnia Payment Gateway', 'somnia-payment-gateway'),
                'default' => 'no'
            ),
            'title' => array(
                'title' => __('Title', 'somnia-payment-gateway'),
                'type' => 'text',
                'description' => __('This controls the title which the user sees during checkout.', 'somnia-payment-gateway'),
                'default' => __('Cryptocurrency Payment (SOMI)', 'somnia-payment-gateway'),
                'desc_tip' => true,
            ),
            'description' => array(
                'title' => __('Description', 'somnia-payment-gateway'),
                'type' => 'textarea',
                'description' => __('This controls the description which the user sees during checkout.', 'somnia-payment-gateway'),
                'default' => __('Pay securely with SOMI cryptocurrency. You will be redirected to complete your payment.', 'somnia-payment-gateway'),
                'desc_tip' => true,
            ),
            'gateway_url' => array(
                'title' => __('Gateway URL', 'somnia-payment-gateway'),
                'type' => 'text',
                'description' => __('The URL of your Somnia Payment Gateway (e.g., http://localhost:5000)', 'somnia-payment-gateway'),
                'default' => 'http://localhost:5000',
                'desc_tip' => true,
            ),
            'merchant_id' => array(
                'title' => __('Merchant ID', 'somnia-payment-gateway'),
                'type' => 'text',
                'description' => __('Your unique merchant ID provided by the payment gateway.', 'somnia-payment-gateway'),
                'default' => '',
                'desc_tip' => true,
            ),
            'payment_timeout' => array(
                'title' => __('Payment Timeout', 'somnia-payment-gateway'),
                'type' => 'number',
                'description' => __('Time in minutes before payment expires (default: 30)', 'somnia-payment-gateway'),
                'default' => '30',
                'desc_tip' => true,
                'custom_attributes' => array(
                    'min' => '5',
                    'max' => '120',
                    'step' => '1'
                )
            ),
            'debug_mode' => array(
                'title' => __('Debug Mode', 'somnia-payment-gateway'),
                'type' => 'checkbox',
                'label' => __('Enable debug logging', 'somnia-payment-gateway'),
                'default' => 'no',
                'description' => __('Log gateway events for debugging. Logs will be saved in WooCommerce > Status > Logs.', 'somnia-payment-gateway'),
            ),
        );
    }

    /**
     * Process the payment and return the result
     */
    public function process_payment($order_id) {
        $order = wc_get_order($order_id);

        try {
            // Get order details
            $price_in_cents = intval($order->get_total() * 100);
            $order_key = $order->get_order_key();

            // Build payment URL
            $payment_url = $this->build_payment_url($price_in_cents, $order_id);

            // Log if debug mode is enabled
            if ($this->debug_mode) {
                $this->log('Processing payment for order #' . $order_id);
                $this->log('Payment URL: ' . $payment_url);
            }

            // Mark as pending payment
            $order->update_status('pending', __('Awaiting cryptocurrency payment', 'somnia-payment-gateway'));

            // Store payment URL in order meta
            $order->update_meta_data('_somnia_payment_url', $payment_url);
            $order->save();

            // Reduce stock levels
            wc_reduce_stock_levels($order_id);

            // Remove cart
            WC()->cart->empty_cart();

            // Return success and redirect to payment gateway
            return array(
                'result' => 'success',
                'redirect' => $payment_url
            );

        } catch (Exception $e) {
            if ($this->debug_mode) {
                $this->log('Payment processing error: ' . $e->getMessage());
            }

            wc_add_notice(__('Payment error: ', 'somnia-payment-gateway') . $e->getMessage(), 'error');
            return array(
                'result' => 'fail',
                'redirect' => ''
            );
        }
    }

    /**
     * Build payment URL for the gateway
     */
    protected function build_payment_url($price_in_cents, $order_id) {
        $gateway_url = rtrim($this->gateway_url, '/');
        
        $params = array(
            'price' => $price_in_cents,
            'merchant' => $this->merchant_id,
            'order_id' => $order_id
        );

        return $gateway_url . '/pay?' . http_build_query($params);
    }

    /**
     * Handle callback from payment gateway
     */
    public function handle_callback() {
        if ($this->debug_mode) {
            $this->log('Callback received: ' . print_r($_REQUEST, true));
        }

        // Get callback data
        $payment_id = isset($_GET['payment_id']) ? sanitize_text_field($_GET['payment_id']) : '';
        $order_id = isset($_GET['order_id']) ? intval($_GET['order_id']) : 0;
        $status = isset($_GET['status']) ? sanitize_text_field($_GET['status']) : '';

        if (!$order_id || !$payment_id) {
            if ($this->debug_mode) {
                $this->log('Invalid callback data');
            }
            wp_die(__('Invalid callback data', 'somnia-payment-gateway'), 400);
            return;
        }

        $order = wc_get_order($order_id);

        if (!$order) {
            if ($this->debug_mode) {
                $this->log('Order not found: ' . $order_id);
            }
            wp_die(__('Order not found', 'somnia-payment-gateway'), 404);
            return;
        }

        // Verify payment status with gateway
        $payment_status = $this->verify_payment_status($payment_id);

        if ($payment_status === 'PAID') {
            // Payment successful
            $order->payment_complete($payment_id);
            $order->add_order_note(
                sprintf(__('Cryptocurrency payment completed. Payment ID: %s', 'somnia-payment-gateway'), $payment_id)
            );

            if ($this->debug_mode) {
                $this->log('Payment completed for order #' . $order_id);
            }

            // Send success response
            wp_send_json_success(array(
                'message' => 'Payment processed successfully'
            ));

        } else {
            // Payment failed or pending
            $order->update_status('failed', sprintf(__('Payment failed. Status: %s', 'somnia-payment-gateway'), $payment_status));

            if ($this->debug_mode) {
                $this->log('Payment failed for order #' . $order_id . '. Status: ' . $payment_status);
            }

            wp_send_json_error(array(
                'message' => 'Payment not completed'
            ));
        }
    }

    /**
     * Verify payment status with gateway
     */
    protected function verify_payment_status($payment_id) {
        $gateway_url = rtrim($this->gateway_url, '/');
        $status_url = $gateway_url . '/status/' . $payment_id;

        $response = wp_remote_get($status_url, array(
            'timeout' => 15,
            'headers' => array(
                'Accept' => 'application/json'
            )
        ));

        if (is_wp_error($response)) {
            if ($this->debug_mode) {
                $this->log('Error verifying payment: ' . $response->get_error_message());
            }
            return 'ERROR';
        }

        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);

        if (isset($data['status'])) {
            return $data['status'];
        }

        return 'UNKNOWN';
    }

    /**
     * Output for the order received page
     */
    public function thankyou_page($order_id) {
        $order = wc_get_order($order_id);
        
        if ($order->get_status() === 'pending') {
            echo '<div class="woocommerce-info">';
            echo '<p>' . __('Your order is pending cryptocurrency payment confirmation.', 'somnia-payment-gateway') . '</p>';
            echo '<p>' . __('You will receive an email confirmation once the payment is confirmed on the blockchain.', 'somnia-payment-gateway') . '</p>';
            echo '</div>';
        }
    }

    /**
     * Add content to the WC emails
     */
    public function email_instructions($order, $sent_to_admin, $plain_text = false) {
        if ($this->instructions && !$sent_to_admin && $this->id === $order->get_payment_method() && $order->has_status('pending')) {
            echo wp_kses_post(wpautop(wptexturize($this->instructions)) . PHP_EOL);
        }
    }

    /**
     * Log messages if debug mode is enabled
     */
    protected function log($message) {
        if ($this->debug_mode) {
            if (!isset($this->logger)) {
                $this->logger = wc_get_logger();
            }
            $this->logger->info($message, array('source' => 'somnia-payment-gateway'));
        }
    }

    /**
     * Validate merchant ID field
     */
    public function validate_merchant_id_field($key, $value) {
        if (empty($value)) {
            WC_Admin_Settings::add_error(__('Merchant ID is required.', 'somnia-payment-gateway'));
        }
        return $value;
    }

    /**
     * Validate gateway URL field
     */
    public function validate_gateway_url_field($key, $value) {
        if (empty($value)) {
            WC_Admin_Settings::add_error(__('Gateway URL is required.', 'somnia-payment-gateway'));
        } elseif (!filter_var($value, FILTER_VALIDATE_URL)) {
            WC_Admin_Settings::add_error(__('Gateway URL must be a valid URL.', 'somnia-payment-gateway'));
        }
        return $value;
    }
}
