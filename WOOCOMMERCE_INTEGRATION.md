# WordPress & WooCommerce Integration Guide

## Overview

The LUX Marketing Platform now integrates seamlessly with WordPress and WooCommerce, allowing you to:
- Sync products from your WooCommerce store
- Create email campaigns featuring your products
- Track customer orders and behavior
- Automate product marketing workflows
- Send targeted campaigns based on purchase history

---

## Prerequisites

### WordPress/WooCommerce Requirements
- WordPress 4.4 or higher
- WooCommerce 3.5 or higher
- Pretty permalinks enabled (not "Plain")
- SSL/HTTPS recommended

### LUX Platform Requirements
- Active LUX Marketing installation
- Environment variables configured
- Access to server configuration files

---

## Setup Instructions

### Step 1: Generate WooCommerce API Credentials

1. **Log in to your WordPress Admin Dashboard**

2. **Navigate to WooCommerce Settings**
   - Go to: `WooCommerce → Settings → Advanced → REST API`

3. **Create New API Key**
   - Click "Add Key"
   - Fill in the following:
     - **Description**: `LUX Marketing Platform`
     - **User**: Select your admin user
     - **Permissions**: Select `Read/Write`
   - Click "Generate API Key"

4. **Save Your Credentials**
   - **Consumer Key**: Starts with `ck_...`
   - **Consumer Secret**: Starts with `cs_...`
   - ⚠️ **IMPORTANT**: These are shown only once! Save them securely.

### Step 2: Configure LUX Platform

#### On Development (Replit)

Add these secrets in your Replit environment:

```
WC_STORE_URL=https://yourstore.com
WC_CONSUMER_KEY=ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WC_CONSUMER_SECRET=cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### On Production (VPS)

1. **Edit environment file:**
   ```bash
   sudo nano /etc/lux/lux-marketing.env
   ```

2. **Add WooCommerce credentials:**
   ```bash
   WC_STORE_URL=https://yourstore.com
   WC_CONSUMER_KEY=ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   WC_CONSUMER_SECRET=cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. **Set proper permissions:**
   ```bash
   sudo chmod 640 /etc/lux/lux-marketing.env
   sudo chown root:luxapp /etc/lux/lux-marketing.env
   ```

4. **Restart the service:**
   ```bash
   sudo systemctl restart lux-marketing.service
   ```

---

## Features & Usage

### 1. View WooCommerce Products

**Navigate to**: Dashboard → WooCommerce → Products

View all products from your WooCommerce store with:
- Product names and descriptions
- Prices and SKUs
- Stock levels
- Product images
- Direct links to products

### 2. Sync Products to LUX Database

**Purpose**: Import products locally for faster access and campaign creation

**Steps**:
1. Go to: Dashboard → WooCommerce
2. Click "Sync Products"
3. Wait for confirmation message
4. Products are now available in local database

**Benefits**:
- Faster campaign creation
- Offline product access
- Better performance

### 3. Create Product Campaigns

**Purpose**: Create email campaigns featuring specific products

**Steps**:
1. Navigate to: WooCommerce → Products
2. Find the product you want to promote
3. Click "View Details"
4. Click "Create Campaign"
5. Fill in campaign details:
   - Campaign Name
   - Email Subject
   - Target Tag/Segment
6. Click "Create Campaign"

**What happens**:
- Automatic email template generation with:
  - Product image
  - Product name and description
  - Price prominently displayed
  - "Shop Now" button linking to product
- Campaign is created in draft status
- You can edit and customize before sending

### 4. View Orders & Customers

**Navigate to**: Dashboard → WooCommerce → Orders

- View recent orders
- See customer information
- Track order status
- Analyze purchase patterns

---

## API Endpoints Reference

### Products
- `GET /woocommerce/products` - List all products
- `GET /woocommerce/products/{id}` - Single product details
- `POST /woocommerce/sync-products` - Sync products to local DB

### Orders
- `GET /woocommerce/orders` - List orders with filters
- `GET /woocommerce/orders/{id}` - Single order details

### Customers
- `GET /woocommerce/customers` - List customers
- `GET /woocommerce/customers/{id}` - Single customer details

---

## Advanced Features

### Automated Product Marketing

Create automation workflows that:
1. Trigger when new products are added
2. Send welcome emails to new customers
3. Follow up after purchases
4. Send abandoned cart reminders
5. Promote related products

**Example Automation**:
```
Trigger: New order placed
→ Wait 1 day
→ Send "Thank You" email
→ Wait 7 days
→ Send "Related Products" email
→ Wait 30 days
→ Send "Review Request" email
```

### Customer Segmentation

Segment customers based on:
- Purchase history
- Order value
- Product categories
- Purchase frequency
- Customer lifetime value

### A/B Testing Product Campaigns

Test different approaches:
- Subject lines
- Product images
- Call-to-action buttons
- Email layouts
- Pricing displays

---

## WordPress Integration (Coming Soon)

Future integration features:
- WordPress blog post announcements
- Content marketing automation
- User registration sync
- Comment engagement tracking
- Page view analytics

---

## Troubleshooting

### "WooCommerce not configured" Error

**Solution**:
1. Verify environment variables are set correctly
2. Check API credentials are valid
3. Ensure WordPress site is accessible
4. Verify WooCommerce REST API is enabled
5. Restart the LUX service

### "Authentication Failed" Error

**Causes**:
- Invalid Consumer Key or Secret
- API key was deleted in WordPress
- User permissions changed
- API key expired

**Solution**:
1. Generate new API keys in WooCommerce
2. Update environment variables
3. Restart service

### "Connection Timeout" Error

**Causes**:
- WordPress site is down
- Firewall blocking requests
- SSL certificate issues
- Network connectivity problems

**Solution**:
1. Verify WordPress site is accessible
2. Check server firewall rules
3. Verify SSL certificate is valid
4. Test from command line:
   ```bash
   curl -I https://yourstore.com
   ```

### Products Not Syncing

**Checks**:
1. Verify API credentials
2. Check WooCommerce has products
3. Review error logs:
   ```bash
   sudo journalctl -u lux-marketing.service -n 50
   ```
4. Increase sync timeout if you have many products

---

## Security Best Practices

1. **Never commit API keys to code repository**
2. **Use environment variables only**
3. **Restrict API permissions to Read/Write only**
4. **Rotate API keys regularly (every 90 days)**
5. **Monitor API usage in WooCommerce**
6. **Use HTTPS for all connections**
7. **Keep WooCommerce updated**
8. **Limit API key to specific IP addresses (if possible)**

---

## Performance Optimization

### For Large Product Catalogs (>1000 products)

1. **Scheduled Syncing**:
   - Sync products during off-peak hours
   - Use cron jobs for automated syncing
   - Sync only changed products

2. **Pagination**:
   - Use page parameters when fetching products
   - Limit per_page to 100 maximum

3. **Caching**:
   - Cache product data locally
   - Refresh cache periodically
   - Use database indexes

### Example Cron Job for Product Sync

```bash
# Sync products every night at 2 AM
0 2 * * * curl -X POST https://lux.lucifercruz.com/woocommerce/sync-products
```

---

## Support & Resources

### Official Documentation
- **WooCommerce REST API**: https://woocommerce.github.io/woocommerce-rest-api-docs/
- **WordPress REST API**: https://developer.wordpress.org/rest-api/
- **Python WooCommerce Library**: https://github.com/woocommerce/wc-api-python

### Getting Help
- Check the LUX Marketing dashboard for status
- Review system logs for errors
- Contact support with API credentials (Consumer Key only, never the secret)

---

## Changelog

### Version 1.0.0 (October 2025)
- ✅ Initial WooCommerce integration
- ✅ Product sync functionality
- ✅ Product campaign creation
- ✅ Order viewing
- ✅ Customer data access
- ⏳ WordPress blog integration (coming soon)
- ⏳ Abandoned cart automation (coming soon)
- ⏳ Purchase-based segmentation (coming soon)

---

## Example Use Cases

### 1. New Product Launch
```
1. Add new product in WooCommerce
2. Sync products in LUX
3. Create product campaign
4. Send to "VIP Customers" segment
5. Track opens and clicks
6. Analyze results in analytics dashboard
```

### 2. Seasonal Sale
```
1. Update product prices in WooCommerce
2. Sync products
3. Create A/B test campaign with two subject lines
4. Send to all active subscribers
5. Monitor conversion rates
6. Send reminder to non-openers after 48 hours
```

### 3. Customer Re-engagement
```
1. Segment customers who haven't purchased in 90 days
2. Select best-selling products
3. Create personalized campaign
4. Offer exclusive discount
5. Track campaign performance
6. Follow up with engaged users
```

---

**Need help?** Check the troubleshooting section or review the error logs for detailed information.
