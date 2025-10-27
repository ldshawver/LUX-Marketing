# VPS Deployment Guide - October 27, 2025

## Files to Deploy

### 1. Python Files (Code Updates)
These files have been modified and need to be deployed to your VPS:

```bash
/var/www/lux-marketing/routes.py
/var/www/lux-marketing/models.py
/var/www/lux-marketing/woocommerce_service.py (NEW FILE)
/var/www/lux-marketing/templates/create_landing_page.html (NEW FILE)
```

### 2. Optional Test File
```bash
/var/www/lux-marketing/test_all_features.py (NEW FILE - for testing only)
```

---

## Deployment Steps

### Step 1: Deploy Updated Files via SSH

Connect to your VPS:
```bash
ssh root@194.195.92.52
```

### Step 2: Backup Current Files

```bash
cd /var/www/lux-marketing

# Create backup directory with timestamp
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup existing files
cp routes.py $BACKUP_DIR/routes.py.backup
cp models.py $BACKUP_DIR/models.py.backup

echo "✅ Backup created in $BACKUP_DIR"
```

### Step 3: Deploy routes.py

Open routes.py for editing:
```bash
nano routes.py
```

**Scroll to the end of the file (around line 2329)** and add the WooCommerce routes.

**OR** use this command to append the routes automatically:
```bash
cat >> routes.py << 'ENDOFROUTES'

# WooCommerce Integration Routes
@main_bp.route('/woocommerce')
@login_required
def woocommerce_dashboard():
    """WooCommerce integration dashboard"""
    from woocommerce_service import WooCommerceService
    wc_service = WooCommerceService()
    
    if not wc_service.is_configured():
        flash('WooCommerce integration is not configured. Please add WooCommerce credentials.', 'warning')
        return render_template('woocommerce_setup.html')
    
    try:
        # Get products summary
        products = wc_service.get_products(per_page=10)
        product_count = len(products) if products else 0
        
        # Get recent orders
        orders = wc_service.get_orders(per_page=5)
        order_count = len(orders) if orders else 0
        
        return render_template('woocommerce_dashboard.html', 
                             products=products,
                             product_count=product_count,
                             orders=orders,
                             order_count=order_count,
                             is_configured=True)
    except Exception as e:
        logger.error(f"WooCommerce error: {e}")
        flash('Error connecting to WooCommerce. Please check your credentials.', 'error')
        return render_template('woocommerce_setup.html')

@main_bp.route('/woocommerce/products')
@login_required
def woocommerce_products():
    """View WooCommerce products"""
    from woocommerce_service import WooCommerceService
    wc_service = WooCommerceService()
    
    if not wc_service.is_configured():
        flash('WooCommerce integration is not configured.', 'warning')
        return redirect(url_for('main.woocommerce_dashboard'))
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    if search:
        products = wc_service.search_products(search, per_page=20)
    else:
        products = wc_service.get_products(page=page, per_page=20)
    
    return render_template('woocommerce_products.html', 
                         products=products or [],
                         search=search,
                         page=page)

@main_bp.route('/woocommerce/products/<int:product_id>')
@login_required
def woocommerce_product_detail(product_id):
    """View single WooCommerce product"""
    from woocommerce_service import WooCommerceService
    wc_service = WooCommerceService()
    
    product = wc_service.get_product(product_id)
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('main.woocommerce_products'))
    
    return render_template('woocommerce_product_detail.html', product=product)

@main_bp.route('/woocommerce/sync-products', methods=['POST'])
@login_required
def sync_woocommerce_products():
    """Sync WooCommerce products to local database"""
    from woocommerce_service import WooCommerceService
    wc_service = WooCommerceService()
    
    try:
        products = wc_service.get_all_products(max_products=500)
        
        synced_count = 0
        for wc_product in products:
            # Check if product exists
            product = Product.query.filter_by(wc_product_id=wc_product['id']).first()
            
            if not product:
                product = Product()
                product.wc_product_id = wc_product['id']
            
            # Update product data
            product.name = wc_product['name']
            product.description = wc_product['description']
            product.price = float(wc_product['price']) if wc_product['price'] else 0.0
            product.sku = wc_product.get('sku', '')
            product.stock_quantity = wc_product.get('stock_quantity', 0)
            product.image_url = wc_product['images'][0]['src'] if wc_product.get('images') else None
            product.product_url = wc_product['permalink']
            
            db.session.add(product)
            synced_count += 1
        
        db.session.commit()
        flash(f'Successfully synced {synced_count} products from WooCommerce!', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error syncing WooCommerce products: {e}")
        flash('Error syncing products from WooCommerce', 'error')
    
    return redirect(url_for('main.woocommerce_dashboard'))

@main_bp.route('/woocommerce/create-product-campaign/<int:product_id>', methods=['GET', 'POST'])
@login_required
def create_product_campaign(product_id):
    """Create email campaign for a specific product"""
    from woocommerce_service import WooCommerceService
    wc_service = WooCommerceService()
    
    # Get product from WooCommerce
    product = wc_service.get_product(product_id)
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('main.woocommerce_products'))
    
    if request.method == 'POST':
        try:
            campaign_name = request.form.get('campaign_name')
            subject = request.form.get('subject')
            tag = request.form.get('tag')
            
            # Create campaign
            campaign = Campaign()
            campaign.name = campaign_name
            campaign.subject = subject
            campaign.status = 'draft'
            
            # Generate email content from product
            product_html = f"""
            <div style="max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif;">
                <h1 style="color: #333;">{product['name']}</h1>
                {'<img src="' + product['images'][0]['src'] + '" style="max-width: 100%; height: auto;" />' if product.get('images') else ''}
                <div style="margin: 20px 0;">
                    <h2 style="color: #0066cc;">Price: ${product['price']}</h2>
                </div>
                <div style="margin: 20px 0;">
                    {product.get('description', '')}
                </div>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{product['permalink']}" style="background: #0066cc; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Shop Now
                    </a>
                </div>
            </div>
            """
            
            # Create template for this campaign
            template = EmailTemplate()
            template.name = f"Product Campaign - {product['name']}"
            template.subject = subject
            template.html_content = product_html
            
            db.session.add(template)
            db.session.flush()
            
            campaign.template_id = template.id
            db.session.add(campaign)
            db.session.commit()
            
            flash(f'Product campaign created successfully!', 'success')
            return redirect(url_for('main.campaign_details', id=campaign.id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating product campaign: {e}")
            flash('Error creating campaign', 'error')
    
    return render_template('create_product_campaign.html', product=product)
ENDOFROUTES

echo "✅ WooCommerce routes added to routes.py"
```

### Step 4: Update models.py - Product Model

Find the Product model (around line 451) and update it:

```bash
# Use sed to update the Product model
sed -i '456a\    wc_product_id = db.Column(db.Integer, unique=True)  # WooCommerce product ID' models.py
sed -i '463a\    product_url = db.Column(db.String(255))  # WooCommerce product permalink' models.py
sed -i '464a\    stock_quantity = db.Column(db.Integer, default=0)' models.py
sed -i '467a\    last_synced = db.Column(db.DateTime)  # Last WooCommerce sync' models.py

echo "✅ Product model updated"
```

**OR** edit manually:
```bash
nano models.py
# Find the Product class and add these fields after the existing ones
```

### Step 5: Create woocommerce_service.py

```bash
nano woocommerce_service.py
```

Paste the entire WooCommerce service code from Replit, or download it and upload via SCP.

### Step 6: Create Landing Page Template

```bash
nano templates/create_landing_page.html
```

Paste the template code from Replit.

### Step 7: Install WooCommerce Python Library

```bash
cd /var/www/lux-marketing
source venv/bin/activate
pip install woocommerce==3.0.0
deactivate

echo "✅ WooCommerce library installed"
```

### Step 8: Update Environment Variables (if using WooCommerce)

```bash
sudo nano /etc/lux/lux-marketing.env
```

Add these lines:
```bash
WC_STORE_URL=https://your-wordpress-site.com
WC_CONSUMER_KEY=ck_xxxxxxxxxxxxxxxxxx
WC_CONSUMER_SECRET=cs_xxxxxxxxxxxxxxxxxx
```

Save and exit.

Set permissions:
```bash
sudo chmod 640 /etc/lux/lux-marketing.env
sudo chown root:luxapp /etc/lux/lux-marketing.env
```

### Step 9: Update Database Schema

```bash
cd /var/www/lux-marketing
source venv/bin/activate

# Run Python to update database
python3 << 'ENDPYTHON'
from app import app, db
with app.app_context():
    db.create_all()
    print("✅ Database schema updated")
ENDPYTHON

deactivate
```

### Step 10: Restart Services

```bash
sudo systemctl restart lux-marketing.service

# Check status
sudo systemctl status lux-marketing.service

# View recent logs
sudo journalctl -u lux-marketing.service --since "1 minute ago" -n 30
```

### Step 11: Verify Deployment

1. **Check service is running:**
   ```bash
   sudo systemctl status lux-marketing.service
   ```

2. **Test the website:**
   - Visit: https://lux.lucifercruz.com
   - Login with your credentials
   - Test Landing Pages: Navigate to Landing Pages → Create Landing Page
   - Test WooCommerce (if configured): Navigate to WooCommerce dashboard

3. **Check logs for errors:**
   ```bash
   sudo journalctl -u lux-marketing.service -f
   ```

---

## Quick Deployment Commands (All-in-One)

If you want to deploy everything quickly:

```bash
# Connect to VPS
ssh root@194.195.92.52

# Navigate to app directory
cd /var/www/lux-marketing

# Create backup
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
cp routes.py models.py $BACKUP_DIR/

# Install WooCommerce library
source venv/bin/activate
pip install woocommerce==3.0.0
deactivate

# Update database schema
source venv/bin/activate
python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Database updated')"
deactivate

# Restart service
sudo systemctl restart lux-marketing.service

# Check status
sudo systemctl status lux-marketing.service

echo "✅ Deployment complete!"
echo "Visit: https://lux.lucifercruz.com"
```

---

## Rollback Instructions (If Something Goes Wrong)

```bash
cd /var/www/lux-marketing

# Find your backup directory
ls -lt backup_*

# Restore from backup
BACKUP_DIR="backup_YYYYMMDD_HHMMSS"  # Replace with your backup directory
cp $BACKUP_DIR/routes.py.backup routes.py
cp $BACKUP_DIR/models.py.backup models.py

# Restart service
sudo systemctl restart lux-marketing.service

echo "✅ Rollback complete"
```

---

## Post-Deployment Testing

### Test Landing Pages
1. Go to: https://lux.lucifercruz.com/landing-pages
2. Click "Create Landing Page"
3. Fill in the form:
   - Name: Test Page
   - Slug: test-page
   - HTML Content: `<h1>Test</h1>`
4. Click "Create Landing Page"
5. Should see success message

### Test WooCommerce (if configured)
1. Add WooCommerce credentials to environment file
2. Restart service
3. Go to: https://lux.lucifercruz.com/woocommerce
4. Should see WooCommerce dashboard
5. Try "Sync Products" button

---

## Troubleshooting

### Service won't start
```bash
# Check detailed error logs
sudo journalctl -u lux-marketing.service -n 100 --no-pager

# Check Python syntax errors
cd /var/www/lux-marketing
source venv/bin/activate
python3 -c "import routes; import models; import woocommerce_service"
deactivate
```

### Landing page error still occurs
```bash
# Check if template exists
ls -lh templates/create_landing_page.html

# Check database has Product table with new fields
source venv/bin/activate
python3 -c "from app import app, db; from models import Product; app.app_context().push(); print(Product.__table__.columns.keys())"
deactivate
```

### WooCommerce not working
```bash
# Verify environment variables
sudo cat /etc/lux/lux-marketing.env | grep WC_

# Test WooCommerce library
source venv/bin/activate
python3 -c "import woocommerce; print('✅ WooCommerce library installed')"
deactivate
```

---

## Files Updated Summary

✅ **routes.py** - Added WooCommerce integration routes  
✅ **models.py** - Updated Product model with WooCommerce fields  
✅ **woocommerce_service.py** - NEW FILE - WooCommerce API service  
✅ **templates/create_landing_page.html** - NEW FILE - Landing page creation form  
✅ **requirements.txt** - Add `woocommerce==3.0.0` (or install via pip)

---

**Need help?** Review the logs and contact support with specific error messages.
