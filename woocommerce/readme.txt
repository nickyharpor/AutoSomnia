=== Somnia Payment Gateway for WooCommerce ===
Contributors: Nicky Harpor
Tags: woocommerce, payment gateway, cryptocurrency, somnia, blockchain
Requires at least: 5.8
Tested up to: 6.4
Requires PHP: 7.4
Stable tag: 1.0.0
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

Accept cryptocurrency payments (SOMI) through Somnia Payment Gateway in your WooCommerce store.

== Description ==

Somnia Payment Gateway for WooCommerce allows you to accept cryptocurrency payments (SOMI tokens) in your online store. This plugin integrates seamlessly with WooCommerce and connects to a remote Somnia Payment Gateway to process transactions.

= Features =

* Accept SOMI cryptocurrency payments
* Automatic payment verification
* Real-time payment status updates
* Configurable payment timeout
* Debug logging for troubleshooting
* Secure payment processing
* Mobile-responsive payment interface
* Automatic order status updates

= How It Works =

1. Customer selects Somnia Payment Gateway at checkout
2. Customer is redirected to the payment gateway
3. Customer selects cryptocurrency and completes payment
4. Payment is verified on the blockchain
5. Order status is automatically updated
6. Customer receives confirmation email

= Requirements =

* WordPress 5.8 or higher
* WooCommerce 5.0 or higher
* PHP 7.4 or higher
* Access to a Somnia Payment Gateway instance
* Valid Merchant ID from the gateway

== Installation ==

= Automatic Installation =

1. Log in to your WordPress dashboard
2. Navigate to Plugins > Add New
3. Search for "Somnia Payment Gateway"
4. Click "Install Now" and then "Activate"

= Manual Installation =

1. Download the plugin ZIP file
2. Log in to your WordPress dashboard
3. Navigate to Plugins > Add New > Upload Plugin
4. Choose the ZIP file and click "Install Now"
5. Activate the plugin

= Configuration =

1. Go to WooCommerce > Settings > Payments
2. Click on "Somnia Payment Gateway"
3. Enable the payment method
4. Enter your Gateway URL (e.g., http://localhost:5000)
5. Enter your Merchant ID
6. Configure other settings as needed
7. Save changes

== Frequently Asked Questions ==

= What is a Merchant ID? =

A Merchant ID is a unique identifier assigned to your store by the Somnia Payment Gateway. You need to register with the gateway to obtain this ID.

= What cryptocurrencies are supported? =

Currently, the gateway supports SOMI tokens on the Somnia testnet. Additional cryptocurrencies may be added in future updates.

= How long does payment confirmation take? =

Payment confirmation typically takes a few seconds up to a minute, depending on blockchain network conditions.

= Can I test the gateway before going live? =

Yes, you can use the default localhost URL (http://localhost:5000) for testing. Make sure you have a local instance of the Somnia Payment Gateway running.

= Where can I find debug logs? =

Enable debug mode in the gateway settings, then navigate to WooCommerce > Status > Logs and look for logs with the source "somnia-payment-gateway".

= What happens if a payment fails? =

If a payment fails, the order status will be updated to "Failed" and the customer will be notified. The customer can attempt payment again from their order page.

= Is this plugin secure? =

Yes, the plugin follows WordPress and WooCommerce security best practices. All payment processing is handled by the remote gateway, and no sensitive payment information is stored on your server.

== Screenshots ==

== Changelog ==

= 1.0.0 =
* Initial release
* Support for SOMI cryptocurrency payments
* Integration with Somnia Payment Gateway
* Automatic payment verification
* Debug logging
* Configurable payment timeout

== Upgrade Notice ==

= 1.0.0 =
Initial release of Somnia Payment Gateway for WooCommerce.

== Support ==

For support, please visit the plugin support forum or contact the plugin author.

== Privacy Policy ==

This plugin connects to a remote Somnia Payment Gateway to process payments. When a customer makes a payment:

* Order information (order ID, amount) is sent to the gateway
* Payment status is retrieved from the gateway
* No customer personal information is stored by the plugin
* Payment data is handled according to the gateway's privacy policy

Please review the Somnia Payment Gateway privacy policy for more information about how payment data is handled.
