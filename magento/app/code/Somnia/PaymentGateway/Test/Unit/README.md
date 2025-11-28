# Somnia Payment Gateway - Unit Tests

This directory contains unit tests for the Somnia Payment Gateway Magento 2 module.

## Test Coverage

### Payment Method Model Tests (`Model/PaymentTest.php`)
Tests for the core payment method model covering:
- `isAvailable()` method with various configurations
- `authorize()` method and payment authorization flow
- `getOrderPlaceRedirectUrl()` redirect URL generation
- `validate()` configuration validation
- Error handling for gateway unavailability

**Requirements Covered**: 1.1, 2.6, 3.1

### Gateway Client Tests (`Model/Gateway/ClientTest.php`)
Tests for the HTTP client that communicates with the payment gateway:
- `buildPaymentUrl()` with various parameters and amount conversion
- `getPaymentStatus()` response parsing and error handling
- `testConnection()` health check functionality
- Connection failure handling
- HTTPS enforcement in production mode

**Requirements Covered**: 4.2, 6.1, 8.1

### Callback Controller Tests (`Controller/Callback/IndexTest.php`)
Tests for the callback endpoint that processes payment notifications:
- Callback parameter validation (payment_id, order_id)
- Payment status verification with gateway
- Order status updates for various payment statuses (PAID, FAILED, EXPIRED)
- Payment amount verification logic
- Input sanitization and security validation

**Requirements Covered**: 5.2, 5.3, 6.4

## Running the Tests

### Prerequisites

1. Magento 2 installation with PHPUnit configured
2. PHP 7.4 or higher
3. PHPUnit 9.5 or compatible version

### Run All Unit Tests

From the Magento root directory:

```bash
# Run all Somnia Payment Gateway unit tests
vendor/bin/phpunit -c app/code/Somnia/PaymentGateway/Test/Unit/phpunit.xml.dist

# Run with coverage report
vendor/bin/phpunit -c app/code/Somnia/PaymentGateway/Test/Unit/phpunit.xml.dist --coverage-html coverage/
```

### Run Specific Test Suites

```bash
# Run only Payment model tests
vendor/bin/phpunit app/code/Somnia/PaymentGateway/Test/Unit/Model/PaymentTest.php

# Run only Gateway Client tests
vendor/bin/phpunit app/code/Somnia/PaymentGateway/Test/Unit/Model/Gateway/ClientTest.php

# Run only Callback Controller tests
vendor/bin/phpunit app/code/Somnia/PaymentGateway/Test/Unit/Controller/Callback/IndexTest.php
```

### Run with Verbose Output

```bash
vendor/bin/phpunit -c app/code/Somnia/PaymentGateway/Test/Unit/phpunit.xml.dist --verbose
```

## Test Structure

Each test class follows PHPUnit best practices:

- **setUp()**: Initializes mocks and dependencies before each test
- **Test Methods**: Named descriptively (e.g., `testIsAvailableReturnsTrue`)
- **Assertions**: Use PHPUnit assertions to verify expected behavior
- **Mocking**: Uses PHPUnit's mock objects to isolate units under test

## Mocking Strategy

The tests use PHPUnit's `createMock()` to create test doubles for:
- Magento framework components (Config, Request, Response)
- External dependencies (HTTP client, Logger)
- Domain objects (Order, Payment)

This ensures tests are:
- **Fast**: No database or network calls
- **Isolated**: Each test is independent
- **Reliable**: No external dependencies

## Code Coverage

To generate a code coverage report:

```bash
vendor/bin/phpunit -c app/code/Somnia/PaymentGateway/Test/Unit/phpunit.xml.dist \
    --coverage-html coverage/ \
    --coverage-text
```

The coverage report will be generated in the `coverage/` directory.

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Unit Tests
  run: vendor/bin/phpunit -c app/code/Somnia/PaymentGateway/Test/Unit/phpunit.xml.dist
```

## Troubleshooting

### Common Issues

**Issue**: `Class not found` errors
**Solution**: Ensure Magento's autoloader is properly configured and the module is registered

**Issue**: Mock object errors
**Solution**: Verify PHPUnit version compatibility (9.5+ recommended)

**Issue**: Bootstrap file not found
**Solution**: Adjust the bootstrap path in `phpunit.xml.dist` to match your Magento installation

## Contributing

When adding new features:
1. Write unit tests for new classes and methods
2. Ensure tests follow existing patterns
3. Maintain test coverage above 80%
4. Run tests before committing changes

## Additional Resources

- [PHPUnit Documentation](https://phpunit.de/documentation.html)
- [Magento Testing Guide](https://developer.adobe.com/commerce/testing/)
- [Test-Driven Development Best Practices](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
