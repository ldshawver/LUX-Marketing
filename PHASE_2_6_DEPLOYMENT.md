# Phase 2-6 Deployment Guide

## Overview
This guide covers deployment of Phases 2-6 features to production VPS at 194.195.92.52 (lux.lucifercruz.com).

## New Features Added
- **Phase 2**: SEO & Analytics (keyword tracking, backlinks, competitors, site audits)
- **Phase 3**: Event Enhancements (ticketing system, check-in management)
- **Phase 4**: Social Media Expansion (multi-platform accounts, scheduling, cross-posting)
- **Phase 5**: Advanced Automations (test mode, trigger library, A/B testing)
- **Phase 6**: Unified Marketing Calendar

## Database Migration

### Step 1: Apply Schema Changes
Run the migration script on production database:

```bash
# SSH into VPS
ssh root@194.195.92.52

# Navigate to app directory
cd /var/www/lux-marketing

# Activate virtual environment
source venv/bin/activate

# Source environment variables
source .env

# Run migration
psql $DATABASE_URL -f migrations/phase_2_6_schema.sql
```

### Step 2: Verify Tables Created
```bash
psql $DATABASE_URL -c "\dt" | grep -E "(seo_|event_ticket|social_media|automation_)"
```

You should see 16 new tables:
- seo_keyword, keyword_ranking, seo_backlink, seo_competitor, competitor_snapshot, seo_audit, seo_page
- event_ticket, ticket_purchase, event_check_in
- social_media_account, social_media_schedule, social_media_cross_post
- automation_test, automation_trigger_library, automation_ab_test

## Code Deployment

### Option 1: Using deployment script
```bash
# From local machine
./deploy_current_app.sh
```

### Option 2: Manual sync
```bash
# On VPS
cd /var/www/lux-marketing
git pull origin main  # or sync files manually

# Restart application
systemctl restart lux-marketing
systemctl status lux-marketing
```

## Post-Deployment Verification

### 1. Check Application Logs
```bash
journalctl -u lux-marketing -f
```

Look for:
- "Automation trigger library seeded successfully"
- All 10 AI agents initialized
- No startup errors

### 2. Verify New Routes
Visit these URLs to test new features:
- https://lux.lucifercruz.com/seo/dashboard
- https://lux.lucifercruz.com/social/accounts
- https://lux.lucifercruz.com/calendar
- https://lux.lucifercruz.com/automations/triggers

### 3. Initialize Trigger Library (if needed)
If trigger library didn't seed automatically:
```bash
# Visit in browser (must be logged in as admin)
https://lux.lucifercruz.com/system/init
```

## Navigation Access

New features are accessible via navigation menu:
- **Multi-Channel** dropdown: SEO Dashboard, Keywords, Competitors, Social Accounts
- **Email Marketing** dropdown: Trigger Library (under automation section)
- **Analytics** dropdown: Marketing Calendar

## Troubleshooting

### Missing Tables
If routes fail with table not found errors:
```bash
# Re-run migration
psql $DATABASE_URL -f migrations/phase_2_6_schema.sql
```

### Trigger Library Empty
```bash
# Visit system init route or run manually in Python shell:
python3 << 'EOF'
from app import app, db
from services.automation_service import AutomationService
with app.app_context():
    AutomationService.seed_trigger_library()
    print("✓ Trigger library seeded")
EOF
```

### Application Won't Start
```bash
# Check logs
journalctl -u lux-marketing -n 100

# Common issues:
# - Import errors: Check all service files exist
# - Database connection: Verify DATABASE_URL in .env
# - Permission issues: Check file ownership (www-data)
```

## Rollback Plan

If issues occur, rollback is available:
1. Database tables are added with IF NOT EXISTS (safe to keep)
2. New routes are separate from existing functionality
3. To disable new features temporarily, comment out route registrations in routes.py

## Success Criteria
✓ All 16 database tables created
✓ Application starts without errors
✓ All 10 AI agents operational
✓ Trigger library contains 3+ templates
✓ New navigation links accessible
✓ No errors in application logs
✓ All new routes return 200 status codes

## Support
After deployment, test each module:
1. SEO: Add a keyword, run site audit
2. Events: Create ticket types for an event
3. Social: Connect a social account
4. Automations: View trigger library
5. Calendar: View upcoming activities
