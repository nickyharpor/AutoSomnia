# Somnia Payment Gateway for WooCommerce

A WordPress plugin that integrates Somnia Payment Gateway with WooCommerce, enabling cryptocurrency payments (SOMI) in your online store.

## Features

- ✅ Accept SOMI cryptocurrency payments
- ✅ Seamless WooCommerce integration
- ✅ Automatic payment verification
- ✅ Real-time payment status updates
- ✅ Configurable payment timeout
- ✅ Debug logging for troubleshooting
- ✅ Mobile-responsive payment interface
- ✅ Secure payment processing
- ✅ Automatic order status updates

## Requirements

- WordPress 5.8 or higher
- WooCommerce 5.0 or higher
- PHP 7.4 or higher
- Access to a Somnia Payment Gateway instance
- Valid Merchant ID from the gateway

## Installation

### Method 1: WordPress Admin Panel

1. Download the plugin ZIP file
2. Log in to your WordPress admin panel
3. Navigate to **Plugins > Add New**
4. Click **Upload Plugin**
5. Choose the ZIP file and click **Install Now**
6. Click **Activate Plugin**

### Method 2: Manual Installation

1. Download and extract the plugin files
2. Upload the `somnia-payment-gateway` folder to `/wp-content/plugins/`
3. Activate the plugin through the **Plugins** menu in WordPress

### Method 3: FTP Upload

1. Extract the plugin ZIP file
2. Connect to your server via FTP
3. Upload the `somnia-payment-gateway` folder to `/wp-content/plugins/`
4. Activate the plugin in WordPress admin panel

## Configuration

### Step 1: Access Gateway Settings

1. Log in to WordPress admin panel
2. Navigate to **WooCommerce > Settings**
3. Click on the **Payments** tab
4. Find **Somnia Payment Gateway** and click **Manage**

### Step 2: Configure Settings

| Setting | Description | Example |
|---------|-------------|---------|
| **Enable/Disable** | Enable or disable the payment gateway | ✓ Enabled |
| **Title** | Payment method title shown to customers | "Cryptocurrency Payment (SOMI)" |
| **Description** | Description shown during checkout | "Pay securely with SOMI cryptocurrency" |
| **Gateway URL** | URL of your Somnia Payment Gateway | `http://localhost:5000` |
| **Merchant ID** | Your unique merchant identifier | `1` |
| **Payment Timeout** | Time in minutes before payment expires | `30` |
| **Debug Mode** | Enable logging for troubleshooting | ☐ Disabled |

### Step 3: Save Settings

Click **Save changes** to apply your configuration.

## Getting a Merchant ID

Before you can accept payments, you need a Merchant ID from the Somnia Payment Gateway:

1. Contact the gateway administrator
2. Provide your store information:
   - Store name
   - Store URL
   - Redirect URL (e.g., `https://yourstore.com/checkout/order-received/`)
   - Callback URL (e.g., `https://yourstore.com/?wc-api=wc_gateway_somnia`)
3. Receive your Merchant ID
4. Enter the Merchant ID in the plugin settings

## Database Configuration

Each WooCommerce installation should have an entry in the gateway database:

```json
{
  "merchant_id": 1,
  "name": "Your Store Name",
  "redirect_url": "https://yourstore.com/checkout/order-received/",
  "callback": "https://yourstore.com/?wc-api=wc_gateway_somnia",
  "allowed_origin": "https://yourstore.com",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## Payment Flow

### Customer Experience

1. **Checkout**: Customer selects "Cryptocurrency Payment (SOMI)" at checkout
2. **Redirect**: Customer is redirected to the Somnia Payment Gateway
3. **Payment**: Customer selects SOMI and completes the payment
4. **Confirmation**: Customer is redirected back to the store
5. **Email**: Customer receives order confirmation email

### Technical Flow

```
┌─────────────┐
│  Customer   │
│   Browser   │
└──────┬──────┘
       │ 1. Checkout
       ▼
┌─────────────────┐
│  WooCommerce    │
│     Store       │
└──────┬──────────┘
       │ 2. Redirect to gateway
       ▼
┌─────────────────┐
│    Somnia       │
│Payment Gateway  │
└──────┬──────────┘
       │ 3. Payment complete
       ▼
┌─────────────────┐
│  WooCommerce    │
│   Callback      │
└──────┬──────────┘
       │ 4. Verify & update order
       ▼
┌─────────────────┐
│ Order Complete  │
└─────────────────┘
```

## API Endpoints

### Payment Initiation

The plugin redirects customers to:
```
{gateway_url}/pay?price={amount_in_cents}&merchant={merchant_id}&order_id={order_id}
```

Example:
```
http://localhost:5000/pay?price=1000&merchant=1&order_id=123
```

### Payment Status Check

The plugin verifies payment status at:
```
{gateway_url}/status/{payment_id}
```

Example:
```
http://localhost:5000/status/550e8400-e29b-41d4-a716-446655440000
```

### Callback URL

The gateway sends callbacks to:
```
{store_url}/?wc-api=wc_gateway_somnia&payment_id={payment_id}&order_id={order_id}&status={status}
```

Example:
```
https://yourstore.com/?wc-api=wc_gateway_somnia&payment_id=550e8400-e29b-41d4-a716-446655440000&order_id=123&status=PAID
```

## Troubleshooting

### Enable Debug Logging

1. Go to **WooCommerce > Settings > Payments > Somnia Payment Gateway**
2. Enable **Debug Mode**
3. Save changes
4. View logs at **WooCommerce > Status > Logs**
5. Look for logs with source `somnia-payment-gateway`

### Common Issues

#### Payment Gateway Not Showing at Checkout

**Solution:**
- Ensure the gateway is enabled in settings
- Check that WooCommerce is active
- Verify Merchant ID is configured

#### Redirect Not Working

**Solution:**
- Check Gateway URL is correct
- Ensure Gateway URL is accessible from your server
- Verify Merchant ID exists in gateway database

#### Payment Not Confirming

**Solution:**
- Check callback URL is accessible
- Verify allowed_origin in gateway database matches your store URL
- Enable debug logging to see callback data

#### Connection Timeout

**Solution:**
- Increase PHP max_execution_time
- Check gateway server is running
- Verify firewall settings allow outbound connections

### Debug Information

To get debug information:

1. Enable debug mode
2. Attempt a test payment
3. Check logs for:
   - Payment URL generation
   - Callback data
   - Payment verification responses
   - Error messages

## Security

### Best Practices

- ✅ Use HTTPS for production stores
- ✅ Keep WordPress and WooCommerce updated
- ✅ Use strong passwords for admin accounts
- ✅ Regularly backup your database
- ✅ Monitor payment logs for suspicious activity
- ✅ Disable debug mode in production

### Data Handling

- Order information is sent to the gateway (order ID, amount)
- No customer personal information is stored by the plugin
- Payment verification is done server-to-server
- All communication should use HTTPS in production

## Development

### File Structure

```
somnia-payment-gateway/
├── somnia-payment-gateway.php    # Main plugin file
├── includes/
│   └── class-wc-gateway-somnia.php  # Gateway class
├── assets/
│   ├── css/
│   │   └── admin.css             # Admin styles
│   ├── js/
│   │   └── admin.js              # Admin scripts
│   └── images/
│       └── somnia-icon.png       # Payment method icon
├── languages/                     # Translation files
├── README.md                      # This file
└── readme.txt                     # WordPress.org readme
```

### Hooks and Filters

#### Actions

- `woocommerce_update_options_payment_gateways_somnia` - Save gateway settings
- `woocommerce_api_wc_gateway_somnia` - Handle payment callbacks
- `woocommerce_thankyou_somnia` - Display thank you page content

#### Filters

- `woocommerce_payment_gateways` - Register the gateway
- `plugin_action_links_somnia-payment-gateway` - Add settings link

### Testing

#### Local Testing

1. Set up local WordPress with WooCommerce
2. Install the plugin
3. Configure gateway URL as `http://localhost:5000`
4. Set Merchant ID to `1` (or your test merchant ID)
5. Create a test product
6. Complete a test checkout

#### Production Testing

1. Use a staging environment first
2. Configure production gateway URL
3. Use a real Merchant ID
4. Test with small amounts
5. Verify order status updates
6. Check email notifications

## Changelog

### Version 1.0.0

- Initial release
- Support for SOMI cryptocurrency payments
- Integration with Somnia Payment Gateway
- Automatic payment verification
- Debug logging
- Configurable payment timeout
- Mobile-responsive interface

## Support

For support and questions:

- **Documentation**: See this README
- **Issues**: Report bugs on GitHub

## License

This plugin is licensed under the GPL v2 or later.

```
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
```

## Credits

- Developed by: Nicky Harpor
- Gateway Integration: Somnia Payment Gateway
- Built for: WooCommerce

## Roadmap

### Version 1.1.0 (Planned)

- [ ] Support for multiple cryptocurrencies
- [ ] Partial payment support
- [ ] Refund functionality
- [ ] Enhanced admin dashboard
- [ ] Payment analytics

### Version 1.2.0 (Planned)

- [ ] Multi-language support
- [ ] Custom payment page styling
- [ ] Webhook support
- [ ] Advanced fraud detection
- [ ] Payment scheduling

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
