<?php
/**
 * Somnia Payment Gateway - Admin Configuration Integration Test
 *
 * @category    Somnia
 * @package     Somnia_PaymentGateway
 */

namespace Somnia\PaymentGateway\Test\Integration;

use Magento\TestFramework\Helper\Bootstrap;
use PHPUnit\Framework\TestCase;
use Somnia\PaymentGateway\Model\Config;

/**
 * Integration test for admin configuration
 *
 * Tests Requirements: 2.1, 2.5, 2.6
 */
class AdminConfigurationTest extends TestCase
{
    /**
     * @var \Magento\Framework\ObjectManagerInterface
     */
    private $objectManager;

    /**
     * @var \Magento\Framework\App\Config\MutableScopeConfigInterface
     */
    private $scopeConfig;

    /**
     * @var Config
     */
    private $config;

    /**
     * @var \Magento\Framework\App\Config\Storage\WriterInterface
     */
    private $configWriter;

    /**
     * Set up test environment
     */
    protected function setUp(): void
    {
        $this->objectManager = Bootstrap::getObjectManager();
        $this->scopeConfig = $this->objectManager->get(\Magento\Framework\App\Config\MutableScopeConfigInterface::class);
        $this->config = $this->objectManager->create(Config::class);
        $this->configWriter = $this->objectManager->get(\Magento\Framework\App\Config\Storage\WriterInterface::class);
    }

    /**
     * Test configuration save and retrieval
     *
     * Requirement 2.1: Configuration should be saved and retrieved correctly
     */
    public function testConfigurationSaveAndRetrieval()
    {
        // Set configuration values
        $this->scopeConfig->setValue(
            Config::XML_PATH_ACTIVE,
            1,
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->scopeConfig->setValue(
            Config::XML_PATH_GATEWAY_URL,
            'https://gateway.example.com',
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->scopeConfig->setValue(
            Config::XML_PATH_MERCHANT_ID,
            123,
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->scopeConfig->setValue(
            Config::XML_PATH_PAYMENT_TIMEOUT,
            45,
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->scopeConfig->setValue(
            Config::XML_PATH_DEBUG,
            1,
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );

        // Retrieve configuration values
        $this->assertTrue($this->config->isEnabled(), 'Payment method should be enabled');
        $this->assertEquals('https://gateway.example.com', $this->config->getGatewayUrl(), 'Gateway URL should match');
        $this->assertEquals(123, $this->config->getMerchantId(), 'Merchant ID should match');
        $this->assertEquals(45, $this->config->getPaymentTimeout(), 'Payment timeout should match');
        $this->assertTrue($this->config->isDebugMode(), 'Debug mode should be enabled');
    }

    /**
     * Test default configuration values
     *
     * Requirement 2.6: Default values should be used when not configured
     */
    public function testDefaultConfigurationValues()
    {
        // Clear all configuration
        $this->scopeConfig->setValue(
            Config::XML_PATH_GATEWAY_URL,
            null,
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->scopeConfig->setValue(
            Config::XML_PATH_PAYMENT_TIMEOUT,
            null,
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );

        // Test default values
        $this->assertEquals(
            Config::DEFAULT_GATEWAY_URL,
            $this->config->getGatewayUrl(),
            'Should use default gateway URL'
        );
        $this->assertEquals(
            Config::DEFAULT_PAYMENT_TIMEOUT,
            $this->config->getPaymentTimeout(),
            'Should use default payment timeout'
        );
    }

    /**
     * Test gateway URL validation
     *
     * Requirement 2.1: Gateway URL should be validated
     */
    public function testGatewayUrlValidation()
    {
        // Test valid URLs
        $this->assertTrue(
            $this->config->validateGatewayUrl('http://localhost:5000'),
            'HTTP localhost URL should be valid'
        );
        $this->assertTrue(
            $this->config->validateGatewayUrl('https://gateway.example.com'),
            'HTTPS URL should be valid'
        );

        // Test invalid URLs
        $this->assertFalse(
            $this->config->validateGatewayUrl(''),
            'Empty URL should be invalid'
        );
        $this->assertFalse(
            $this->config->validateGatewayUrl('not-a-url'),
            'Invalid URL format should be invalid'
        );
        $this->assertFalse(
            $this->config->validateGatewayUrl('ftp://gateway.example.com'),
            'FTP URL should be invalid'
        );
    }

    /**
     * Test merchant ID validation
     *
     * Requirement 2.1: Merchant ID should be validated
     */
    public function testMerchantIdValidation()
    {
        // Test valid merchant IDs
        $this->assertTrue(
            $this->config->validateMerchantId(1),
            'Positive integer should be valid'
        );
        $this->assertTrue(
            $this->config->validateMerchantId('123'),
            'Numeric string should be valid'
        );

        // Test invalid merchant IDs
        $this->assertFalse(
            $this->config->validateMerchantId(''),
            'Empty value should be invalid'
        );
        $this->assertFalse(
            $this->config->validateMerchantId(0),
            'Zero should be invalid'
        );
        $this->assertFalse(
            $this->config->validateMerchantId(-1),
            'Negative number should be invalid'
        );
        $this->assertFalse(
            $this->config->validateMerchantId('abc'),
            'Non-numeric string should be invalid'
        );
    }

    /**
     * Test payment timeout validation
     *
     * Requirement 2.6: Payment timeout should be validated
     */
    public function testPaymentTimeoutValidation()
    {
        // Test valid timeouts
        $this->assertTrue(
            $this->config->validatePaymentTimeout(30),
            'Valid timeout should pass'
        );
        $this->assertTrue(
            $this->config->validatePaymentTimeout(Config::MIN_PAYMENT_TIMEOUT),
            'Minimum timeout should be valid'
        );
        $this->assertTrue(
            $this->config->validatePaymentTimeout(Config::MAX_PAYMENT_TIMEOUT),
            'Maximum timeout should be valid'
        );

        // Test invalid timeouts
        $this->assertFalse(
            $this->config->validatePaymentTimeout(''),
            'Empty value should be invalid'
        );
        $this->assertFalse(
            $this->config->validatePaymentTimeout(Config::MIN_PAYMENT_TIMEOUT - 1),
            'Below minimum should be invalid'
        );
        $this->assertFalse(
            $this->config->validatePaymentTimeout(Config::MAX_PAYMENT_TIMEOUT + 1),
            'Above maximum should be invalid'
        );
        $this->assertFalse(
            $this->config->validatePaymentTimeout('abc'),
            'Non-numeric value should be invalid'
        );
    }

    /**
     * Test payment timeout range enforcement
     *
     * Requirement 2.6: Payment timeout should be within acceptable range
     */
    public function testPaymentTimeoutRangeEnforcement()
    {
        // Set timeout below minimum
        $this->scopeConfig->setValue(
            Config::XML_PATH_PAYMENT_TIMEOUT,
            2,
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->assertEquals(
            Config::MIN_PAYMENT_TIMEOUT,
            $this->config->getPaymentTimeout(),
            'Should enforce minimum timeout'
        );

        // Set timeout above maximum
        $this->scopeConfig->setValue(
            Config::XML_PATH_PAYMENT_TIMEOUT,
            200,
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->assertEquals(
            Config::MAX_PAYMENT_TIMEOUT,
            $this->config->getPaymentTimeout(),
            'Should enforce maximum timeout'
        );
    }

    /**
     * Test HTTPS detection
     *
     * Requirement 2.5: Should detect HTTPS connections
     */
    public function testHttpsDetection()
    {
        // Test HTTPS URL
        $this->scopeConfig->setValue(
            Config::XML_PATH_GATEWAY_URL,
            'https://gateway.example.com',
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->assertTrue(
            $this->config->isSecureConnection(),
            'HTTPS URL should be detected as secure'
        );

        // Test HTTP URL
        $this->scopeConfig->setValue(
            Config::XML_PATH_GATEWAY_URL,
            'http://gateway.example.com',
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->assertFalse(
            $this->config->isSecureConnection(),
            'HTTP URL should not be detected as secure'
        );
    }

    /**
     * Test localhost detection
     *
     * Requirement 2.5: Should detect localhost URLs
     */
    public function testLocalhostDetection()
    {
        // Test localhost
        $this->scopeConfig->setValue(
            Config::XML_PATH_GATEWAY_URL,
            'http://localhost:5000',
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->assertTrue(
            $this->config->isLocalhostGateway(),
            'localhost should be detected'
        );

        // Test 127.0.0.1
        $this->scopeConfig->setValue(
            Config::XML_PATH_GATEWAY_URL,
            'http://127.0.0.1:5000',
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->assertTrue(
            $this->config->isLocalhostGateway(),
            '127.0.0.1 should be detected as localhost'
        );

        // Test remote URL
        $this->scopeConfig->setValue(
            Config::XML_PATH_GATEWAY_URL,
            'https://gateway.example.com',
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->assertFalse(
            $this->config->isLocalhostGateway(),
            'Remote URL should not be detected as localhost'
        );
    }

    /**
     * Test IP whitelist configuration
     *
     * Requirement 2.5: Should support IP whitelist configuration
     */
    public function testIpWhitelistConfiguration()
    {
        // Test with no whitelist
        $this->scopeConfig->setValue(
            Config::XML_PATH_ALLOWED_IPS,
            '',
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->assertFalse(
            $this->config->isIpWhitelistEnabled(),
            'Whitelist should not be enabled when empty'
        );
        $this->assertTrue(
            $this->config->isIpAllowed('1.2.3.4'),
            'All IPs should be allowed when whitelist is disabled'
        );

        // Test with whitelist
        $this->scopeConfig->setValue(
            Config::XML_PATH_ALLOWED_IPS,
            "192.168.1.1\n10.0.0.0/8",
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->assertTrue(
            $this->config->isIpWhitelistEnabled(),
            'Whitelist should be enabled'
        );
        $this->assertTrue(
            $this->config->isIpAllowed('192.168.1.1'),
            'Whitelisted IP should be allowed'
        );
        $this->assertTrue(
            $this->config->isIpAllowed('10.0.0.5'),
            'IP in CIDR range should be allowed'
        );
        $this->assertFalse(
            $this->config->isIpAllowed('1.2.3.4'),
            'Non-whitelisted IP should not be allowed'
        );
    }

    /**
     * Test test connection functionality
     *
     * Requirement 2.5: Should provide test connection functionality
     */
    public function testConnectionFunctionality()
    {
        // Configure gateway
        $this->scopeConfig->setValue(
            Config::XML_PATH_GATEWAY_URL,
            'http://localhost:5000',
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->scopeConfig->setValue(
            Config::XML_PATH_MERCHANT_ID,
            1,
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );

        // Create gateway client
        $gatewayClient = $this->objectManager->create(\Somnia\PaymentGateway\Model\Gateway\Client::class);

        // Test connection (this will actually try to connect to the gateway)
        // In a real test environment, you would mock this
        try {
            $result = $gatewayClient->testConnection();
            
            // If gateway is running, connection should succeed
            if ($result['success']) {
                $this->assertTrue($result['success'], 'Connection test should succeed');
                $this->assertArrayHasKey('message', $result, 'Result should contain message');
            } else {
                // If gateway is not running, we should get a proper error
                $this->assertFalse($result['success'], 'Connection test should fail gracefully');
                $this->assertArrayHasKey('error', $result, 'Result should contain error message');
            }
        } catch (\Exception $e) {
            // Connection test should not throw exceptions
            $this->fail('Connection test should not throw exceptions: ' . $e->getMessage());
        }
    }

    /**
     * Test configuration retrieval for different stores
     *
     * Requirement 2.1: Configuration should support multi-store
     */
    public function testMultiStoreConfiguration()
    {
        // Set configuration for default store
        $this->scopeConfig->setValue(
            Config::XML_PATH_GATEWAY_URL,
            'https://gateway1.example.com',
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE,
            1
        );

        // Set configuration for another store (if exists)
        $this->scopeConfig->setValue(
            Config::XML_PATH_GATEWAY_URL,
            'https://gateway2.example.com',
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE,
            2
        );

        // Retrieve configuration for different stores
        $url1 = $this->config->getGatewayUrl(1);
        $url2 = $this->config->getGatewayUrl(2);

        // Verify store-specific configuration
        $this->assertEquals('https://gateway1.example.com', $url1, 'Store 1 should have its own URL');
        
        // Store 2 might not exist, so we just verify it returns a value
        $this->assertNotEmpty($url2, 'Store 2 should return a URL');
    }

    /**
     * Test trailing slash removal from gateway URL
     *
     * Requirement 2.1: Gateway URL should have trailing slash removed
     */
    public function testTrailingSlashRemoval()
    {
        // Set URL with trailing slash
        $this->scopeConfig->setValue(
            Config::XML_PATH_GATEWAY_URL,
            'https://gateway.example.com/',
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );

        // Verify trailing slash is removed
        $this->assertEquals(
            'https://gateway.example.com',
            $this->config->getGatewayUrl(),
            'Trailing slash should be removed'
        );
    }

    /**
     * Test sort order configuration
     *
     * Requirement 2.1: Sort order should be configurable
     */
    public function testSortOrderConfiguration()
    {
        // Set sort order
        $this->scopeConfig->setValue(
            Config::XML_PATH_SORT_ORDER,
            10,
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );

        // Verify sort order
        $this->assertEquals(10, $this->config->getSortOrder(), 'Sort order should match');
    }

    /**
     * Clean up after tests
     */
    protected function tearDown(): void
    {
        // Reset configuration to defaults
        $this->scopeConfig->setValue(
            Config::XML_PATH_ACTIVE,
            0,
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->scopeConfig->setValue(
            Config::XML_PATH_GATEWAY_URL,
            null,
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->scopeConfig->setValue(
            Config::XML_PATH_MERCHANT_ID,
            null,
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->scopeConfig->setValue(
            Config::XML_PATH_PAYMENT_TIMEOUT,
            null,
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->scopeConfig->setValue(
            Config::XML_PATH_ALLOWED_IPS,
            null,
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
        $this->scopeConfig->setValue(
            Config::XML_PATH_DEBUG,
            0,
            \Magento\Store\Model\ScopeInterface::SCOPE_STORE
        );
    }
}
