# Somnia Payment Gateway - Integration Tests

This directory contains integration tests for the Somnia Payment Gateway Magento 2 module. Integration tests verify that different components work together correctly within the Magento framework.

## Test Coverage

### Checkout Flow Tests (`CheckoutFlowTest.php`)

Tests the complete checkout flow with cryptocurrency payment:

- **Payment method availability**: Verifies payment method appears when enabled and is hidden when disabled
- **Order placement**: Tests order creation with cryptocurrency payment method
- **Redirect URL generation**: Verifies correct redirect URL is generated for gateway
- **Order status**: Confirms order status is set to "pending_payment" after placement
- **Payment information storage**: Validates payment details are stored in order

**Requirements Covered**: 3.1, 4.1, 4.5

### Callback Processing Tests (`CallbackProcessingTest.php`)

Tests the callback endpoint that processes payment notifications from the gateway:

- **Valid payment processing**: Tests callback with successful payment status
- **Failed payment handling**: Verifies order cancellation for failed payments
- **Expired payment handling**: Tests order cancellation for expired payments
- **Order status updates**: Confirms order status changes based on payment status
- **Payment information storage**: Validates payment details are stored after callback
- **Parameter validation**: Tests callback with missing or invalid parameters
- **Order comments**: Verifies payment details are added to order history

**Requirements Covered**: 5.1, 5.3, 5.4

### Admin Configuration Tests (`AdminConfigurationTest.php`)

Tests the admin configuration interface and settings:

- **Configuration save/retrieval**: Tests saving and retrieving configuration values
- **Default values**: Verifies default configuration values are used when not set
- **Gateway URL validation**: Tests URL format validation
- **Merchant ID validation**: Tests merchant ID format and range validation
- **Payment timeout validation**: Tests timeout range enforcement
- **HTTPS detection**: Verifies HTTPS connection detection
- **Localhost detection**: Tests localhost URL detection
- **IP whitelist**: Tests IP whitelist configuration and validation
- **Test connection**: Verifies gateway connectivity testing
- **Multi-store support**: Tests store-specific configuration
- **URL normalization**: Tests trailing slash removal

**Requirements Covered**: 2.1, 2.5, 2.6

## Running the Tests

### Prerequisites

1. **Magento 2 Installation**: Full Magento 2 installation with integration test framework
2. **PHP 7.4 or higher**: Required by Magento 2.4.x
3. **PHPUnit 9.5+**: Compatible with Magento 2.4.x
4. **Test Database**: Separate database for integration tests
5. **Gateway Service** (optional): Running gateway service for connection tests

### Setup Integration Test Environment

1. **Configure test database** in `dev/tests/integration/etc/install-config-mysql.php`:

```php
return [
    'db-host' => 'localhost',
    'db-user' => 'root',
    'db-password' => 'password',
    'db-name' => 'magento_integration_tests',
    'db-prefix' => '',
    'backend-frontname' => 'backend',
    'admin-user' => 'admin',
    'admin-password' => 'admin123',
    'admin-email' => 'admin@example.com',
    'admin-firstname' => 'Admin',
    'admin-lastname' => 'User',
];
```

2. **Install test database**:

```bash
cd dev/tests/integration
php ../../../vendor/bin/phpunit --configuration phpunit.xml.dist --testsuite "Magento Integration Tests" --filter "testStub"
```

### Run All Integration Tests

From the Magento root directory:

```bash
# Run all Somnia Payment Gateway integration tests
vendor/bin/phpunit -c app/code/Somnia/PaymentGateway/Test/Integration/phpunit.xml.dist

# Run with verbose output
vendor/bin/phpunit -c app/code/Somnia/PaymentGateway/Test/Integration/phpunit.xml.dist --verbose

# Run with detailed test information
vendor/bin/phpunit -c app/code/Somnia/PaymentGateway/Test/Integration/phpunit.xml.dist --testdox
```

### Run Specific Test Suites

```bash
# Run only checkout flow tests
vendor/bin/phpunit app/code/Somnia/PaymentGateway/Test/Integration/CheckoutFlowTest.php

# Run only callback processing tests
vendor/bin/phpunit app/code/Somnia/PaymentGateway/Test/Integration/CallbackProcessingTest.php

# Run only admin configuration tests
vendor/bin/phpunit app/code/Somnia/PaymentGateway/Test/Integration/AdminConfigurationTest.php
```

### Run Specific Test Methods

```bash
# Run a specific test method
vendor/bin/phpunit app/code/Somnia/PaymentGateway/Test/Integration/CheckoutFlowTest.php --filter testPaymentMethodIsAvailableDuringCheckout
```

## Test Structure

Integration tests follow Magento's integration testing framework:

- **setUp()**: Initializes Magento object manager and dependencies
- **Test Methods**: Named descriptively (e.g., `testOrderPlacementWithCryptocurrencyPayment`)
- **Assertions**: Use PHPUnit assertions to verify expected behavior
- **tearDown()**: Cleans up test data and resets configuration

## Key Differences from Unit Tests

| Aspect | Unit Tests | Integration Tests |
|--------|-----------|-------------------|
| **Scope** | Single class/method | Multiple components |
| **Dependencies** | Mocked | Real Magento objects |
| **Database** | No database access | Uses test database |
| **Speed** | Very fast (milliseconds) | Slower (seconds) |
| **Isolation** | Completely isolated | Tests interactions |
| **Purpose** | Verify logic | Verify integration |

## Mocking Strategy

Integration tests use minimal mocking:

- **Gateway Client**: Mocked to avoid external HTTP calls
- **Magento Framework**: Real objects from object manager
- **Database**: Real test database with transactions
- **Configuration**: Real configuration system

This ensures tests verify actual integration between components while avoiding external dependencies.

## Test Data Management

Integration tests create and clean up test data:

1. **Orders**: Created with unique increment IDs
2. **Quotes**: Created with test products and addresses
3. **Configuration**: Set during test, reset in tearDown()
4. **Database**: Magento handles transaction rollback

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

### GitHub Actions Example

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: magento_integration_tests
        ports:
          - 3306:3306
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup PHP
        uses: shivammathur/setup-php@v2
        with:
          php-version: '7.4'
          extensions: bcmath, ctype, curl, dom, gd, hash, iconv, intl, mbstring, openssl, pdo_mysql, simplexml, soap, xsl, zip
      
      - name: Install Magento
        run: |
          composer install
          bin/magento setup:install --db-host=127.0.0.1 --db-name=magento_integration_tests --db-user=root --db-password=root
      
      - name: Run Integration Tests
        run: vendor/bin/phpunit -c app/code/Somnia/PaymentGateway/Test/Integration/phpunit.xml.dist
```

## Troubleshooting

### Common Issues

**Issue**: `Class not found` errors  
**Solution**: Ensure Magento is properly installed and the module is registered

**Issue**: Database connection errors  
**Solution**: Verify test database configuration in `dev/tests/integration/etc/install-config-mysql.php`

**Issue**: Tests fail with "Area code not set"  
**Solution**: Integration test framework should handle this automatically. Check bootstrap configuration.

**Issue**: Gateway connection tests fail  
**Solution**: These tests expect a running gateway service. Either start the gateway or mock the client.

**Issue**: Tests are very slow  
**Solution**: Integration tests are slower than unit tests. Consider running only specific test suites during development.

### Debug Mode

Enable debug output:

```bash
# Run with debug output
vendor/bin/phpunit -c app/code/Somnia/PaymentGateway/Test/Integration/phpunit.xml.dist --debug

# Run with verbose assertions
vendor/bin/phpunit -c app/code/Somnia/PaymentGateway/Test/Integration/phpunit.xml.dist --verbose --debug
```

## Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Cleanup**: Always clean up test data in tearDown()
3. **Realistic Data**: Use realistic test data that mimics production scenarios
4. **Clear Assertions**: Use descriptive assertion messages
5. **Fast Tests**: Keep tests as fast as possible while maintaining coverage
6. **Avoid External Dependencies**: Mock external services (gateway API)

## Contributing

When adding new features:

1. Write integration tests for new workflows
2. Ensure tests follow existing patterns
3. Test both success and failure scenarios
4. Run all tests before committing changes
5. Update this README if adding new test suites

## Performance Considerations

Integration tests are slower than unit tests:

- **Checkout Flow Tests**: ~2-5 seconds per test
- **Callback Processing Tests**: ~1-3 seconds per test
- **Admin Configuration Tests**: ~1-2 seconds per test

Total suite execution time: ~30-60 seconds

For faster feedback during development:
1. Run unit tests first (faster)
2. Run integration tests for affected areas
3. Run full integration suite before committing

## Additional Resources

- [Magento Integration Testing Guide](https://developer.adobe.com/commerce/testing/guide/integration/)
- [PHPUnit Documentation](https://phpunit.de/documentation.html)
- [Magento Testing Best Practices](https://developer.adobe.com/commerce/testing/guide/integration/best-practices/)
- [Integration Test Framework](https://developer.adobe.com/commerce/testing/guide/integration/framework/)

## Test Results

After running tests, you should see output like:

```
PHPUnit 9.5.x by Sebastian Bergmann and contributors.

Testing Somnia Payment Gateway Integration Tests
...............                                                   15 / 15 (100%)

Time: 00:45.123, Memory: 128.00 MB

OK (15 tests, 45 assertions)
```

## Coverage

Integration tests complement unit tests to provide comprehensive coverage:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions and workflows
- **Combined Coverage**: Ensures both logic and integration are verified

For complete test coverage, run both unit and integration test suites.
