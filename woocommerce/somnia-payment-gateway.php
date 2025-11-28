<?php
/**
 * Plugin Name: Somnia Payment Gateway for WooCommerce
 * Plugin URI: https://github.com/nickyharpor/AutoSomnia
 * Description: Accept cryptocurrency payments (SOMI) through Somnia Payment Gateway
 * Version: 1.0.0
 * Author: Nicky Harpor
 * Author URI: https://github.com/nickyharpor
 * License: GPL v2 or later
 * License URI: https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain: somnia-payment-gateway
 * Domain Path: /languages
 * Requires at least: 5.8
 * Requires PHP: 7.4
 * WC requires at least: 5.0
 * WC tested up to: 8.0
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('SOMNIA_GATEWAY_VERSION', '1.0.0');
define('SOMNIA_GATEWAY_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('SOMNIA_GATEWAY_PLUGIN_URL', plugin_dir_url(__FILE__));
define('SOMNIA_GATEWAY_PLUGIN_FILE', __FILE__);

/**
 * Check if WooCommerce is active
 */
function somnia_gateway_check_woocommerce() {
    if (!class_exists('WooCommerce')) {
        add_action('admin_notices', 'somnia_gateway_woocommerce_missing_notice');
        return false;
    }
    return true;
}

/**
 * Display admin notice if WooCommerce is not active
 */
function somnia_gateway_woocommerce_missing_notice() {
    ?>
    <div class="error">
        <p><?php _e('Somnia Payment Gateway requires WooCommerce to be installed and active.', 'somnia-payment-gateway'); ?></p>
    </div>
    <?php
}

/**
 * Initialize the gateway
 */
function somnia_gateway_init() {
    if (!somnia_gateway_check_woocommerce()) {
        return;
    }

    // Include the gateway class
    require_once SOMNIA_GATEWAY_PLUGIN_DIR . 'includes/class-wc-gateway-somnia.php';

    // Add the gateway to WooCommerce
    add_filter('woocommerce_payment_gateways', 'somnia_gateway_add_gateway');
}
add_action('plugins_loaded', 'somnia_gateway_init');

/**
 * Add Somnia Gateway to WooCommerce
 */
function somnia_gateway_add_gateway($gateways) {
    $gateways[] = 'WC_Gateway_Somnia';
    return $gateways;
}

/**
 * Add settings link on plugin page
 */
function somnia_gateway_settings_link($links) {
    $settings_link = '<a href="admin.php?page=wc-settings&tab=checkout&section=somnia">' . __('Settings', 'somnia-payment-gateway') . '</a>';
    array_unshift($links, $settings_link);
    return $links;
}
add_filter('plugin_action_links_' . plugin_basename(__FILE__), 'somnia_gateway_settings_link');

/**
 * Load plugin textdomain for translations
 */
function somnia_gateway_load_textdomain() {
    load_plugin_textdomain('somnia-payment-gateway', false, dirname(plugin_basename(__FILE__)) . '/languages');
}
add_action('init', 'somnia_gateway_load_textdomain');

/**
 * Register activation hook
 */
function somnia_gateway_activate() {
    // Check for WooCommerce
    if (!class_exists('WooCommerce')) {
        deactivate_plugins(plugin_basename(__FILE__));
        wp_die(__('This plugin requires WooCommerce to be installed and active.', 'somnia-payment-gateway'));
    }

    // Set default options
    if (!get_option('woocommerce_somnia_settings')) {
        $default_settings = array(
            'enabled' => 'no',
            'title' => 'Cryptocurrency Payment (SOMI)',
            'description' => 'Pay with SOMI cryptocurrency',
            'gateway_url' => 'http://localhost:5000',
            'merchant_id' => '',
            'payment_timeout' => '30',
            'debug_mode' => 'no'
        );
        update_option('woocommerce_somnia_settings', $default_settings);
    }
}
register_activation_hook(__FILE__, 'somnia_gateway_activate');

/**
 * Register deactivation hook
 */
function somnia_gateway_deactivate() {
    // Cleanup if needed
}
register_deactivation_hook(__FILE__, 'somnia_gateway_deactivate');
