# Manual Regression Test Checklist - Phases 2-6

## Test Environment
- **Application URL**: https://lux.lucifercruz.com
- **Test Date**: 2025-10-30
- **Tester**: QA Engineer
- **Build Version**: Phase 2-6 Release

## Test Status Legend
- ✅ PASS - Feature works as expected
- ❌ FAIL - Feature broken or not working
- ⚠️  PARTIAL - Feature works but has issues
- ⏭️  SKIP - Not tested yet

---

## PHASE 2: SEO & ANALYTICS MODULE

### SEO Dashboard
- [ ] Navigate to SEO Dashboard via menu (Multi-Channel → SEO Dashboard)
- [ ] Verify dashboard loads without errors
- [ ] Check all 4 stat cards display (Keywords, Top Rankings, Backlinks, Competitors)
- [ ] Verify "Quick Actions" buttons present
- [ ] **Screenshot**: `evidence/seo_dashboard.png`

### Keyword Tracking
- [ ] Navigate to SEO Keywords page
- [ ] Click "Add Keyword" button
- [ ] Modal opens correctly
- [ ] Fill form: Keyword = "test marketing", Target URL = "https://example.com"
- [ ] Submit form (verify CSRF token present)
- [ ] Keyword appears in table
- [ ] Table shows: Keyword, Position, Volume, Difficulty, Last Checked
- [ ] **Screenshot**: `evidence/seo_keywords_add.png`
- [ ] **Screenshot**: `evidence/seo_keywords_list.png`

### Backlink Monitoring
- [ ] Navigate to SEO Backlinks page
- [ ] Page loads without error
- [ ] Table structure correct (Source, Anchor, DA, Status)
- [ ] **Screenshot**: `evidence/seo_backlinks.png`

### Competitor Tracking
- [ ] Navigate to SEO Competitors page
- [ ] Page loads without error
- [ ] Card layout displays correctly
- [ ] **Screenshot**: `evidence/seo_competitors.png`

### Site Audit
- [ ] Navigate to "Run Site Audit"
- [ ] Form displays correctly
- [ ] Fill URL: "https://example.com"
- [ ] Select audit type: "Full Audit"
- [ ] Submit form
- [ ] Redirect to audit results page
- [ ] Results show: Overall score, Technical, Content, Performance scores
- [ ] Issues and recommendations displayed
- [ ] **Screenshot**: `evidence/seo_audit_form.png`
- [ ] **Screenshot**: `evidence/seo_audit_results.png`

---

## PHASE 3: EVENT ENHANCEMENTS

### Event Ticketing
- [ ] Create a test event first (if needed)
- [ ] Navigate to Event Tickets page for event
- [ ] Click "Add Ticket Type"
- [ ] Fill form: Name = "VIP", Price = "99.99", Quantity = "50"
- [ ] Submit form
- [ ] Ticket appears in table
- [ ] Verify price formatting ($99.99)
- [ ] Verify sold/available quantities
- [ ] **Screenshot**: `evidence/event_tickets_create.png`
- [ ] **Screenshot**: `evidence/event_tickets_list.png`

### Ticket Purchase
- [ ] Attempt to purchase ticket
- [ ] Verify purchase creates ticket codes
- [ ] Check payment status
- [ ] **Screenshot**: `evidence/ticket_purchase.png`

### Event Check-in
- [ ] Navigate to Event Check-in page
- [ ] Form displays correctly
- [ ] Enter Contact ID
- [ ] Submit check-in
- [ ] Check-in appears in recent list
- [ ] **Screenshot**: `evidence/event_checkin.png`

---

## PHASE 4: SOCIAL MEDIA EXPANSION

### Social Media Accounts
- [ ] Navigate to Social Accounts (Multi-Channel → Social Accounts)
- [ ] Page loads correctly
- [ ] Click "Connect Account"
- [ ] Modal opens
- [ ] Fill form: Platform = "Twitter", Account Name = "testuser", Access Token = "test123"
- [ ] Submit form (verify CSRF token)
- [ ] Account appears in grid
- [ ] Card shows: Platform, Username, Verified badge, Followers
- [ ] **Screenshot**: `evidence/social_accounts_empty.png`
- [ ] **Screenshot**: `evidence/social_accounts_connect.png`
- [ ] **Screenshot**: `evidence/social_accounts_connected.png`

### Post Scheduling
- [ ] Click "Schedule Post" on account card
- [ ] Navigate to scheduling form
- [ ] Fill content, hashtags, date/time
- [ ] Submit form
- [ ] Post scheduled successfully
- [ ] **Screenshot**: `evidence/social_schedule.png`

---

## PHASE 5: ADVANCED AUTOMATIONS

### Automation Trigger Library
- [ ] Navigate to Trigger Library (Email Marketing → Trigger Library)
- [ ] Page loads successfully
- [ ] Pre-built triggers display (3+ templates)
- [ ] Verify templates: "Welcome Series", "Abandoned Cart", "Re-engagement Campaign"
- [ ] Category filter buttons work
- [ ] Each trigger shows: Name, Description, Category, Usage count
- [ ] **Screenshot**: `evidence/automation_triggers_all.png`
- [ ] **Screenshot**: `evidence/automation_triggers_filtered.png`

### Automation Test Mode
- [ ] Create or select an automation
- [ ] Access test mode
- [ ] Run test
- [ ] View test results
- [ ] **Screenshot**: `evidence/automation_test.png`

---

## PHASE 6: UNIFIED MARKETING CALENDAR

### Marketing Calendar
- [ ] Navigate to Marketing Calendar (Analytics → Marketing Calendar)
- [ ] Page loads without errors
- [ ] Current month/year displayed
- [ ] Upcoming activities list visible (30 days)
- [ ] Previous/Next month buttons work
- [ ] Activity types legend shows
- [ ] **Screenshot**: `evidence/calendar_view.png`
- [ ] **Screenshot**: `evidence/calendar_upcoming.png`

---

## NAVIGATION & INTEGRATION TESTS

### Menu Navigation
- [ ] Multi-Channel dropdown includes:
  - [ ] Social Media
  - [ ] Social Accounts ✨ NEW
  - [ ] SMS Marketing
  - [ ] SEO Dashboard ✨ NEW
  - [ ] Keywords ✨ NEW
  - [ ] Competitors ✨ NEW
  - [ ] Events

- [ ] Email Marketing dropdown includes:
  - [ ] Trigger Library ✨ NEW

- [ ] Analytics dropdown includes:
  - [ ] Marketing Calendar ✨ NEW

- [ ] **Screenshot**: `evidence/navigation_menu.png`

### Cross-Module Integration
- [ ] Create event → Create tickets → View in calendar
- [ ] Add keyword → Run audit → View in dashboard
- [ ] Connect social account → Schedule post → View in calendar
- [ ] Create automation → Browse triggers → Run test

---

## FORMS & CSRF PROTECTION

### All Forms Have CSRF Tokens
- [ ] SEO: Add Keyword form
- [ ] Social: Connect Account form
- [ ] Events: Create Ticket Type form
- [ ] Events: Check-in form
- [ ] Social: Schedule Post form
- [ ] SEO: Run Audit form

### Form Validation
- [ ] Required fields enforced
- [ ] Email validation works
- [ ] Number fields accept numbers only
- [ ] Date/time pickers work correctly

---

## ERROR HANDLING

### 404 Errors
- [ ] Access non-existent route returns proper 404
- [ ] 404 page is user-friendly

### 500 Errors
- [ ] Application handles database errors gracefully
- [ ] No stack traces exposed to users

### Form Errors
- [ ] Invalid data shows validation messages
- [ ] CSRF errors show friendly message

---

## PERFORMANCE & MONITORING

### Page Load Times
- [ ] All pages load within 3 seconds
- [ ] No console errors in browser
- [ ] No JavaScript errors

### Database Operations
- [ ] All queries execute efficiently
- [ ] No N+1 query problems
- [ ] Proper indexing on frequently queried fields

---

## PRODUCTION READINESS

### Logs
- [ ] Application starts without errors
- [ ] Trigger library seeds successfully
- [ ] All 10 AI agents initialized
- [ ] No error logs during normal operation

### Database
- [ ] All 16 new tables exist
- [ ] Foreign keys properly configured
- [ ] Cascading deletes work correctly

### Monitoring
- [ ] Health check endpoint responds
- [ ] Error reporting configured
- [ ] Log aggregation working

---

## SUMMARY

### Total Tests: ____ / ____
### Passed: ____
### Failed: ____
### Blocked: ____

### Critical Issues Found:
1. [Issue description]
2. [Issue description]

### Recommendations:
1. [Recommendation]
2. [Recommendation]

### Sign-off:
- [ ] All critical issues resolved
- [ ] All high-priority issues resolved or documented
- [ ] Evidence pack complete
- [ ] Ready for production deployment

**Tester Signature**: ________________  **Date**: ____________
**Approver Signature**: ________________  **Date**: ____________
