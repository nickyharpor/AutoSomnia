<?php
/**
 * Somnia Payment Gateway Module Registration
 *
 * @category  Somnia
 * @package   Somnia_PaymentGateway
 * @author    Somnia Team
 * @copyright Copyright (c) 2024 Somnia
 * @license   MIT License
 */

use Magento\Framework\Component\ComponentRegistrar;

ComponentRegistrar::register(
    ComponentRegistrar::MODULE,
    'Somnia_PaymentGateway',
    __DIR__
);
