# Somnia Payment Gateway Images

This directory contains image assets for the Somnia Payment Gateway module.

## Logo Files

- `somnia-logo.svg` - Vector logo (recommended for scalability)
- `somnia-logo.png` - Raster logo (32x32px, for compatibility)

## Usage

The logo is displayed in:
- Checkout payment method selection
- Order success page
- Customer order history
- Admin order view

## Customization

To use a custom logo:
1. Replace the logo files in this directory
2. Ensure the filename remains the same, or update references in:
   - `view/frontend/web/template/payment/somnia-gateway.html`
   - `view/frontend/templates/payment/info.phtml`
   - `view/frontend/web/js/view/payment/method-renderer/somnia-gateway.js`

## Recommended Specifications

- Format: PNG or SVG
- Size: 32x32px (or larger for high-DPI displays)
- Background: Transparent
- Colors: Should match your brand identity
