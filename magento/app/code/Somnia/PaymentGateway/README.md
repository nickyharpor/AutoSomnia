# Somnia Payment Gateway for Magento 2

Accept cryptocurrency payments (SOMI tokens) in your Magento 2 store through the Somnia Payment Gateway.

## Overview

The Somnia Payment Gateway plugin integrates seamlessly with Magento 2, allowing merchants to accept cryptocurrency payments. The plugin connects to a remote payment gateway service that handles all blockchain transactions, providing a simple and secure payment experience for both merchants and customers.

## Features

- ✅ Accept SOMI cryptocurrency payments
- ✅ Automatic order status updates via payment callbacks
- ✅ Secure payment verification with double-check mechanism
- ✅ Admin configuration interface with test connection
- ✅ Debug logging for troubleshooting
- ✅ Email notifications for payment status
- ✅ HTTPS enforcement for production environments
- ✅ IP whitelist support for callback security
- ✅ Multi-store support

## Requirements

### System Requirements

- **Magento Version**: 2.3.x or 2.4.x
- **PHP Version**: 7.4, 8.0, or 8.1
- **PHP Extensions**: cURL, JSON
- **Web Server**: Apache 2.4+ or Nginx 1.18+
- **Database**: MySQL 5.7+ or MariaDB 10.2+

### Gateway Requirements

- Access to Somnia Payment Gateway (Flask service)
- Merchant account registered in gateway database
- Gateway URL (e.g., `http://localhost:5000` or production URL)
- Merchant ID assigned by gateway administrator

## Installation

### Method 1: Composer Installation (Recommended)

1. **Add the package to your Magento installation**:

```bash
composer require somnia/magento2-payment-gateway
```

2. **Enable the module**:

```bash
php bin/magento module:enable Somnia_PaymentGateway
```

3. **Run setup upgrade**:

```bash
php bin/magento setup:upgrade
```

4. **Compile dependency injection**:

```bash
php bin/magento setup:di:compile
```

5. **Deploy static content** (production mode):

```bash
php bin/magento setup:static-content:deploy
```

6. **Clear cache**:

```bash
php bin/magento cache:flush
```

### Method 2: Manual Installation

1. **Create module directory**:

```bash
mkdir -p app/code/Somnia/PaymentGateway
```

2. **Copy module files** to `app/code/Somnia/PaymentGateway/`

3. **Enable the module**:

```bash
php bin/magento module:enable Somnia_PaymentGateway
```

4. **Run setup upgrade**:

```bash
php bin/magento setup:upgrade
```

5. **Compile dependency injection**:

```bash
php bin/magento setup:di:compile
```

6. **Deploy static content** (production mode):

```bash
php bin/magento setup:static-content:deploy
```

7. **Clear cache**:

```bash
php bin/magento cache:flush
```

### Verify Installation

Check that the module is enabled:

```bash
php bin/magento module:status Somnia_PaymentGateway
```

Expected output:
```
Module is enabled
```

## Configuration

### Step 1: Access Payment Configuration

1. Log in to your Magento Admin Panel
2. Navigate to: **Stores** → **Configuration** → **Sales** → **Payment Methods**
3. Locate the **Somnia Cryptocurrency Payment** section
4. Click to expand the configuration panel

### Step 2: Basic Configuration

Configure the following required fields:

| Field | Description | Example Value |
|-------|-------------|---------------|
| **Enabled** | Enable/disable the payment method | Yes |
| **Title** | Payment method name shown to customers | "Cryptocurrency Payment (SOMI)" |
| **Gateway URL** | Base URL of the payment gateway | `http://localhost:5000` |
| **Merchant ID** | Your merchant identifier from gateway | `1` |
| **Payment Timeout** | Payment expiration time in minutes | `30` |
| **Debug Mode** | Enable detailed logging | No (Yes for testing) |
| **Sort Order** | Display order in checkout | `10` |

### Step 3: Advanced Configuration (Optional)

| Field | Description | Default |
|-------|-------------|---------|
| **Allowed IPs** | Comma-separated list of gateway IPs for callback verification | Empty (all allowed) |
| **Minimum Order Total** | Minimum order amount to show payment method | `0.00` |
| **Maximum Order Total** | Maximum order amount to show payment method | Empty (no limit) |

### Step 4: Test Connection

1. Click the **Test Connection** button in the configuration panel
2. Wait for the connection test to complete
3. Verify you see a success message: "✓ Connection successful"
4. If the test fails, check:
   - Gateway URL is correct and accessible
   - Gateway service is running
   - Firewall allows outbound connections

### Step 5: Save Configuration

1. Click **Save Config** button
2. Clear cache: **System** → **Cache Management** → **Flush Magento Cache**

### Configuration Screenshots

#### Payment Methods Configuration
```
Stores → Configuration → Sales → Payment Methods
└── Somnia Cryptocurrency Payment
    ├── Enabled: Yes
    ├── Title: Cryptocurrency Payment (SOMI)
    ├── Gateway URL: http://localhost:5000
    ├── Merchant ID: 1
    ├── Payment Timeout: 30
    ├── Debug Mode: No
    └── [Test Connection] button
```

## Gateway Database Setup

Before using the plugin, your merchant account must be registered in the gateway's MongoDB database.

### Example Gateway Database Entry

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "gateway_id": 1,
  "redirect_url": "https://yourstore.com/somnia/callback",
  "callback": "https://yourstore.com/somnia/callback",
  "allowed_origin": "https://yourstore.com",
  "merchant_name": "Your Store Name",
  "created_at": ISODate("2024-01-15T10:30:00Z"),
  "active": true
}
```

### Database Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `gateway_id` | Integer | Your merchant ID (use this in Magento config) |
| `redirect_url` | String | URL where customers return after payment |
| `callback` | String | URL for payment status notifications |
| `allowed_origin` | String | Your store's base URL for CORS |
| `merchant_name` | String | Your business name |
| `active` | Boolean | Whether the merchant account is active |

### Callback URL Format

The callback URL must be accessible from the gateway:

```
https://yourstore.com/somnia/callback/index
```

**Important**: Ensure this URL is:
- Publicly accessible (not behind firewall)
- Using HTTPS in production
- Not blocked by security rules

## Usage

### Customer Checkout Flow

1. Customer adds products to cart
2. Customer proceeds to checkout
3. Customer selects "Cryptocurrency Payment (SOMI)" as payment method
4. Customer places order
5. Customer is redirected to payment gateway
6. Customer completes cryptocurrency payment
7. Gateway sends callback to Magento
8. Order status updates automatically to "Processing"
9. Customer receives order confirmation email

### Admin Order Management

#### View Payment Details

1. Navigate to: **Sales** → **Orders**
2. Open an order with cryptocurrency payment
3. View payment information in the **Payment & Shipping Method** section:
   - Payment Method: Cryptocurrency Payment (SOMI)
   - Payment ID: `abc-123-def-456`
   - Crypto Amount: `100.5 SOMI`
   - Gateway URL: `http://localhost:5000`

#### Order Status Flow

```
Pending Payment → Processing (payment successful)
                → Canceled (payment failed/expired)
```

## Troubleshooting

### Common Issues

#### 1. Payment Method Not Showing in Checkout

**Symptoms**: Cryptocurrency payment option doesn't appear during checkout

**Solutions**:
- ✓ Verify module is enabled: `php bin/magento module:status Somnia_PaymentGateway`
- ✓ Check configuration: **Stores** → **Configuration** → **Sales** → **Payment Methods**
- ✓ Ensure "Enabled" is set to "Yes"
- ✓ Clear cache: `php bin/magento cache:flush`
- ✓ Check minimum/maximum order total settings
- ✓ Verify store view configuration (multi-store setups)

#### 2. Connection Test Fails

**Symptoms**: "Test Connection" button shows error message

**Solutions**:
- ✓ Verify gateway URL is correct (include `http://` or `https://`)
- ✓ Check gateway service is running: `curl http://localhost:5000/health`
- ✓ Test network connectivity from Magento server
- ✓ Check firewall rules allow outbound connections
- ✓ Verify PHP cURL extension is installed: `php -m | grep curl`
- ✓ Check gateway logs for incoming requests

**Debug Commands**:
```bash
# Test gateway health endpoint
curl http://localhost:5000/health

# Check PHP cURL
php -r "echo (extension_loaded('curl') ? 'cURL enabled' : 'cURL disabled');"

# Test from Magento server
php -r "echo file_get_contents('http://localhost:5000/health');"
```

#### 3. Order Status Not Updating After Payment

**Symptoms**: Customer completes payment but order remains "Pending Payment"

**Solutions**:
- ✓ Verify callback URL is accessible: `https://yourstore.com/somnia/callback/index`
- ✓ Check gateway can reach callback URL (not blocked by firewall)
- ✓ Review Magento logs: `var/log/somnia_payment.log`
- ✓ Check gateway logs for callback attempts
- ✓ Verify merchant ID matches gateway database
- ✓ Test callback manually:
  ```bash
  curl -X GET "https://yourstore.com/somnia/callback/index?payment_id=test-123&order_id=000000001"
  ```
- ✓ Check allowed IPs configuration (if set)
- ✓ Verify HTTPS certificate is valid (production)

#### 4. Payment Amount Mismatch Error

**Symptoms**: Log shows "Payment amount mismatch" error

**Solutions**:
- ✓ Check order currency matches gateway expectations
- ✓ Verify price conversion to cents is correct
- ✓ Review gateway status response for actual amount
- ✓ Check for rounding issues with decimal amounts
- ✓ Ensure tax and shipping are included in total

#### 5. Customer Redirected to Wrong URL

**Symptoms**: After placing order, customer sees 404 or wrong page

**Solutions**:
- ✓ Verify gateway URL in configuration
- ✓ Check gateway service is running
- ✓ Review payment URL construction in logs (debug mode)
- ✓ Ensure order ID is passed correctly
- ✓ Check for URL encoding issues

#### 6. Debug Logging Not Working

**Symptoms**: No logs appearing in `var/log/somnia_payment.log`

**Solutions**:
- ✓ Enable debug mode in configuration
- ✓ Check file permissions on `var/log/` directory
- ✓ Verify log directory exists: `mkdir -p var/log`
- ✓ Set correct permissions: `chmod 777 var/log`
- ✓ Check PHP error logs for write permission errors
- ✓ Trigger a test transaction to generate logs

#### 7. HTTPS Warning in Admin

**Symptoms**: Warning message about using HTTP in production

**Solutions**:
- ✓ Update gateway URL to use HTTPS
- ✓ Ensure gateway has valid SSL certificate
- ✓ For development, this warning can be ignored
- ✓ Never use HTTP in production environments

#### 8. Callback IP Verification Fails

**Symptoms**: Callbacks rejected with "Unauthorized IP" error

**Solutions**:
- ✓ Add gateway IP to "Allowed IPs" configuration
- ✓ Use comma-separated list for multiple IPs: `192.168.1.100,192.168.1.101`
- ✓ Leave empty to allow all IPs (less secure)
- ✓ Check gateway's actual IP address in logs
- ✓ Consider using IP ranges for cloud deployments

### Log Files

#### Somnia Payment Log
**Location**: `var/log/somnia_payment.log`

**Contents**:
- Payment initiation requests
- Gateway API responses
- Callback processing
- Payment verification results
- Error messages

**Example Log Entries**:
```
[2024-01-15 10:30:45] INFO: Payment initiated for order #000000123
[2024-01-15 10:30:46] DEBUG: Gateway URL: http://localhost:5000/pay?price=1000&merchant=1&order_id=000000123
[2024-01-15 10:31:15] INFO: Callback received for payment abc-123-def
[2024-01-15 10:31:16] DEBUG: Status verification response: {"status":"PAID","balance":"100.5"}
[2024-01-15 10:31:16] INFO: Order #000000123 marked as Processing
[2024-01-15 10:32:00] ERROR: Payment verification failed: Connection timeout
```

#### Magento System Log
**Location**: `var/log/system.log`

**Contents**:
- Module initialization errors
- Configuration errors
- General system errors

#### Magento Exception Log
**Location**: `var/log/exception.log`

**Contents**:
- PHP exceptions
- Fatal errors
- Stack traces

### Enable Debug Mode

1. Navigate to: **Stores** → **Configuration** → **Sales** → **Payment Methods**
2. Expand **Somnia Cryptocurrency Payment**
3. Set **Debug Mode** to "Yes"
4. Save configuration
5. Clear cache
6. Reproduce the issue
7. Check `var/log/somnia_payment.log` for detailed information

### Getting Help

If you continue to experience issues:

1. **Check logs**: Review `var/log/somnia_payment.log` with debug mode enabled
2. **Verify gateway**: Ensure gateway service is operational
3. **Test manually**: Use cURL to test gateway endpoints
4. **Contact support**: Email support@somnia.network with:
   - Magento version
   - PHP version
   - Module version
   - Error messages from logs
   - Steps to reproduce the issue

## Security Best Practices

### Production Deployment

1. **Use HTTPS**: Always use HTTPS for gateway URL in production
2. **Disable Debug Mode**: Turn off debug logging in production
3. **Configure IP Whitelist**: Restrict callbacks to known gateway IPs
4. **Secure Callback URL**: Ensure callback endpoint uses HTTPS
5. **Regular Updates**: Keep module and Magento core updated
6. **Monitor Logs**: Regularly review logs for suspicious activity
7. **Backup Database**: Regular backups before updates

### File Permissions

Recommended permissions for production:

```bash
# Module files
find app/code/Somnia/PaymentGateway -type f -exec chmod 644 {} \;
find app/code/Somnia/PaymentGateway -type d -exec chmod 755 {} \;

# Log directory
chmod 777 var/log
```

## Uninstallation

### Remove Module

1. **Disable the module**:

```bash
php bin/magento module:disable Somnia_PaymentGateway
```

2. **Remove via Composer** (if installed via Composer):

```bash
composer remove somnia/magento2-payment-gateway
```

3. **Remove manually** (if installed manually):

```bash
rm -rf app/code/Somnia/PaymentGateway
```

4. **Run setup upgrade**:

```bash
php bin/magento setup:upgrade
```

5. **Clear cache**:

```bash
php bin/magento cache:flush
```

### Clean Database

The module does not create separate database tables. Payment data is stored in Magento's standard order tables and will remain after uninstallation.

## API Reference

### Gateway Endpoints Used

#### Payment Initiation
```
GET /pay?price={cents}&merchant={id}&order_id={order_id}
```

**Parameters**:
- `price`: Order total in cents (integer)
- `merchant`: Merchant ID (integer)
- `order_id`: Magento order increment ID (string)

**Response**: Redirects to payment page

#### Payment Status
```
GET /status/{payment_id}
```

**Parameters**:
- `payment_id`: Unique payment identifier (UUID)

**Response**:
```json
{
  "status": "PAID",
  "balance": "100.5",
  "crypto_symbol": "SOMI",
  "order_id": "000000123"
}
```

#### Health Check
```
GET /health
```

**Response**:
```json
{
  "status": "healthy"
}
```

### Callback Endpoint

```
GET /somnia/callback/index?payment_id={id}&order_id={order_id}
```

**Parameters**:
- `payment_id`: Payment identifier from gateway
- `order_id`: Magento order increment ID

**Response**:
```json
{
  "success": true,
  "message": "Payment processed successfully"
}
```

## Development

### Module Structure

```
app/code/Somnia/PaymentGateway/
├── Block/                      # Block classes
├── Controller/                 # Controllers
├── etc/                        # Configuration files
├── Helper/                     # Helper classes
├── i18n/                       # Translations
├── Model/                      # Business logic
├── Observer/                   # Event observers
├── Plugin/                     # Plugins
├── view/                       # Templates and assets
├── composer.json               # Composer configuration
├── registration.php            # Module registration
└── README.md                   # This file
```

### Testing

Run unit tests:

```bash
php bin/magento dev:tests:run unit Somnia_PaymentGateway
```

Run integration tests:

```bash
php bin/magento dev:tests:run integration Somnia_PaymentGateway
```

### Contributing

Contributions are welcome! Please follow Magento coding standards and include tests for new features.
