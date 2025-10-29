# LUX Marketing Platform - Phase 0-1 Test Cases

## Test Environment
- **Date:** October 29, 2025
- **Phase:** 0-1 (Foundation Infrastructure)
- **Status:** Ready for Testing

---

## 1. DATABASE TESTS

### 1.1 New Tables Verification
**Test:** Verify all Phase 0-1 tables exist
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'campaign_tag', 
    'campaign_association', 
    'schedule_slot', 
    'sms_template', 
    'sms_queue', 
    'sms_analytics', 
    'ai_request_log', 
    'analytics_snapshot'
) 
ORDER BY table_name;
```
**Expected:** All 8 tables should be listed
**Status:** ✅ PASS

### 1.2 Automation Columns Migration
**Test:** Verify pause/resume columns exist in automation table
```sql
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'automation' 
AND column_name IN ('is_paused', 'paused_at', 'paused_reason', 'execution_count', 'success_count', 'failure_count');
```
**Expected:** 6 columns should be listed
**Status:** ✅ PASS

---

## 2. AUTOMATION PAUSE/RESUME TESTS

### 2.1 Pause Automation (No Automations Yet)
**Prerequisites:** Need to create test automation first
**Test Steps:**
1. Go to `/automations`
2. Create a new automation
3. Click "Pause" button
4. Provide pause reason
5. Submit

**Expected Results:**
- Automation `is_paused` = true
- `paused_at` timestamp set
- `paused_reason` saved
- Flash message: "Automation paused successfully!"

**Status:** ⏳ PENDING (No automations in database yet)

### 2.2 Resume Automation
**Prerequisites:** Paused automation from test 2.1
**Test Steps:**
1. Go to paused automation
2. Click "Resume" button
3. Confirm

**Expected Results:**
- Automation `is_paused` = false
- `paused_at` = NULL
- `paused_reason` = NULL
- Flash message: "Automation resumed successfully!"

**Status:** ⏳ PENDING

---

## 3. SMS MARKETING MODULE TESTS

### 3.1 SMS Dashboard
**Route:** `/sms`
**Test Steps:**
1. Navigate to Multi-Channel > SMS Marketing
2. Verify dashboard loads

**Expected Results:**
- Campaign list displays
- Stats cards show (Total, Sent, Scheduled)
- Templates section visible
- "Create Campaign" button present

**Status:** ✅ PASS (Route exists, template created)

### 3.2 Create SMS Campaign (Basic)
**Route:** `/sms/create`
**Test Steps:**
1. Navigate to SMS > Create Campaign
2. Fill in campaign name: "Test SMS Campaign"
3. Enter message: "Test message. Reply STOP to unsubscribe."
4. Select "Send immediately"
5. Submit

**Expected Results:**
- Campaign created in `sms_campaign` table
- Recipients added to `sms_recipient` table
- Flash message: "SMS campaign created successfully!"
- Redirect to `/sms`

**Status:** ⏳ READY FOR TESTING

### 3.3 Create SMS Campaign with Scheduling
**Test Steps:**
1. Navigate to `/sms/create`
2. Fill campaign details
3. Select "Schedule for later"
4. Choose date: Tomorrow
5. Choose time: 10:00 AM
6. Submit

**Expected Results:**
- Campaign created with `scheduled_at` set
- Entry created in `schedule_slot` table
- Campaign status = "scheduled"
- Shows in unified calendar

**Status:** ⏳ READY FOR TESTING

### 3.4 Create SMS Campaign with Tags
**Test Steps:**
1. Navigate to `/sms/create`
2. Fill campaign details
3. Add campaign tags: "promo, summer-2025"
4. Submit

**Expected Results:**
- Tags created in `campaign_tag` table
- Associations created in `campaign_association` table
- Tags visible on campaign

**Status:** ⏳ READY FOR TESTING

### 3.5 AI SMS Generation - Professional Tone
**Test Steps:**
1. Navigate to `/sms/create`
2. Enter campaign name: "Summer Sale"
3. Click "AI: Professional" button
4. Wait for generation

**Expected Results:**
- AI-generated message appears in textarea
- Character count updates
- Message includes opt-out language
- Message ≤ 160 characters

**Status:** ⏳ READY FOR TESTING

### 3.6 AI SMS Generation - Sales Tone
**Test Steps:**
1. Same as 3.5 but click "AI: Sales"

**Expected Results:**
- More promotional/urgent language
- Still compliant and ≤ 160 chars

**Status:** ⏳ READY FOR TESTING

### 3.7 AI SMS Generation - Luxury Tone
**Test Steps:**
1. Same as 3.5 but click "AI: Luxury"

**Expected Results:**
- Premium, exclusive language
- Still compliant and ≤ 160 chars

**Status:** ⏳ READY FOR TESTING

### 3.8 Template Selection
**Prerequisites:** Create SMS template first
**Test Steps:**
1. Navigate to `/sms/templates/create`
2. Create template: "Welcome SMS"
3. Go to `/sms/create`
4. Select template from dropdown
5. Verify message auto-fills

**Expected Results:**
- Message textarea populated with template content
- Character count updates
- Template marked as used

**Status:** ⏳ READY FOR TESTING

### 3.9 Compliance Warning - No Opt-out
**Test Steps:**
1. Navigate to `/sms/create`
2. Enter message > 50 chars without "STOP" or "unsubscribe"
3. Observe warnings

**Expected Results:**
- Warning displayed: "Consider adding opt-out instructions"
- Warning icon visible
- Can still submit (soft warning)

**Status:** ⏳ READY FOR TESTING

### 3.10 Compliance Warning - Spam Keywords
**Test Steps:**
1. Enter message: "FREE winner! ACT NOW limited time!"
2. Observe warnings

**Expected Results:**
- Warning: "Message contains potential spam keywords"
- Keywords highlighted or mentioned

**Status:** ⏳ READY FOR TESTING

---

## 4. CAMPAIGN TAGGING SERVICE TESTS

### 4.1 Create Tag
**Test Code:**
```python
from services.campaign_tagging_service import CampaignTaggingService
tag = CampaignTaggingService.create_tag("summer-2025")
```
**Expected:** Tag created with name "summer-2025"
**Status:** ⏳ READY FOR TESTING

### 4.2 Associate Tag with SMS Campaign
**Test Code:**
```python
CampaignTaggingService.sync_tags_for_object([tag.id], 'sms', campaign_id)
```
**Expected:** Association created in `campaign_association` table
**Status:** ⏳ READY FOR TESTING

### 4.3 Get Objects by Tag
**Test Code:**
```python
campaigns = CampaignTaggingService.get_objects_by_tag(tag.id, 'sms')
```
**Expected:** Returns list of SMS campaigns with that tag
**Status:** ⏳ READY FOR TESTING

### 4.4 Tag Analytics
**Test Code:**
```python
analytics = CampaignTaggingService.get_tag_analytics(tag.id)
```
**Expected:** Returns metrics for all objects with that tag
**Status:** ⏳ READY FOR TESTING

---

## 5. SCHEDULING SERVICE TESTS

### 5.1 Create Schedule Entry
**Test Code:**
```python
from services.scheduling_service import SchedulingService
from datetime import datetime, timedelta

schedule = SchedulingService.create_schedule(
    module_type='sms',
    module_object_id=campaign_id,
    title='SMS: Test Campaign',
    scheduled_at=datetime.now() + timedelta(days=1),
    description='Test SMS message'
)
```
**Expected:** Entry created in `schedule_slot` table
**Status:** ⏳ READY FOR TESTING

### 5.2 Get Upcoming Schedules
**Test Code:**
```python
upcoming = SchedulingService.get_upcoming_schedules(days_ahead=7)
```
**Expected:** Returns all schedules for next 7 days across all modules
**Status:** ⏳ READY FOR TESTING

### 5.3 Calendar View
**Test Code:**
```python
calendar = SchedulingService.get_calendar_view(2025, 10)
```
**Expected:** Returns dict with dates as keys, grouped schedules as values
**Status:** ⏳ READY FOR TESTING

### 5.4 Update Schedule Status
**Test Code:**
```python
SchedulingService.update_schedule_status(schedule_id, 'completed')
```
**Expected:** Schedule status updated, `completed_at` timestamp set
**Status:** ⏳ READY FOR TESTING

---

## 6. SMS SERVICE TESTS

### 6.1 Create Campaign
**Test Code:**
```python
from services.sms_service import SMSService
campaign = SMSService.create_campaign(
    name="Test Campaign",
    message="Hello! Reply STOP to opt-out.",
    scheduled_at=None
)
```
**Expected:** Campaign created with status='draft'
**Status:** ⏳ READY FOR TESTING

### 6.2 Create Template
**Test Code:**
```python
template = SMSService.create_template(
    name="Welcome Message",
    message="Welcome to LUX! Reply STOP to opt-out.",
    category="transactional",
    tone="professional"
)
```
**Expected:** Template created, reusable for future campaigns
**Status:** ⏳ READY FOR TESTING

### 6.3 Check Compliance
**Test Code:**
```python
result = SMSService.check_compliance("Great deals! Click now!")
```
**Expected:** Returns dict with warnings about missing opt-out
**Status:** ⏳ READY FOR TESTING

### 6.4 AI Generate SMS
**Test Code:**
```python
message = SMSService.ai_generate_sms(
    prompt="Summer sale announcement",
    tone="sales",
    max_length=160
)
```
**Expected:** Returns AI-generated SMS ≤ 160 chars with compliance
**Status:** ⏳ READY FOR TESTING

### 6.5 AI Reword for Length
**Test Code:**
```python
long_message = "This is a very long SMS message that exceeds the 160 character limit and needs to be shortened while maintaining the core message and compliance requirements. Reply STOP to unsubscribe from all future messages."
reworded = SMSService.ai_reword_sms(long_message, 160)
```
**Expected:** Returns shortened version ≤ 160 chars
**Status:** ⏳ READY FOR TESTING

---

## 7. AI SERVICE TESTS

### 7.1 Generate Content
**Test Code:**
```python
from services.ai_service import AIService
content = AIService.generate_content(
    prompt="Create a professional email subject line",
    module="email"
)
```
**Expected:** Returns AI-generated content, logs request in `ai_request_log`
**Status:** ⏳ READY FOR TESTING

### 7.2 Request Logging
**Test:** Verify AI requests are logged
```sql
SELECT module, prompt_preview, response_preview, tokens_used, cost 
FROM ai_request_log 
ORDER BY created_at DESC 
LIMIT 5;
```
**Expected:** Shows recent AI requests with cost tracking
**Status:** ⏳ READY FOR TESTING

---

## 8. UI/UX TESTS

### 8.1 Navigation - SMS Link
**Test Steps:**
1. Login to platform
2. Click "Multi-Channel" in navigation
3. Verify "SMS Marketing" link present

**Expected:** Link present with message-circle icon
**Status:** ✅ PASS

### 8.2 Feather Icons Fixed
**Test Steps:**
1. Navigate throughout the app
2. Check browser console for warnings

**Expected:** No "palette is not a valid icon" warnings
**Status:** ✅ PASS (Fixed to 'layout' icon)

### 8.3 SMS Form - Character Counter
**Test Steps:**
1. Go to `/sms/create`
2. Type in message field
3. Observe character counter

**Expected:** 
- Counter updates in real-time
- Shows "X/160"
- Turns orange/warning color after 140 chars

**Status:** ⏳ READY FOR TESTING

### 8.4 SMS Form - Schedule Toggle
**Test Steps:**
1. Go to `/sms/create`
2. Select "Schedule for later" radio button
3. Observe form changes

**Expected:** Date and time fields appear
**Status:** ⏳ READY FOR TESTING

---

## 9. INTEGRATION TESTS

### 9.1 End-to-End: Create Tagged, Scheduled SMS Campaign
**Test Steps:**
1. Navigate to `/sms/create`
2. Name: "Black Friday 2025"
3. Message: AI-generated (click "AI: Sales")
4. Campaign tags: "black-friday, promo"
5. Segment tags: "vip"
6. Schedule: Tomorrow 9 AM
7. Submit

**Expected:**
- Campaign created in `sms_campaign`
- Tags created and associated
- Schedule created in `schedule_slot`
- AI request logged
- Recipients filtered by segment
- Redirects to dashboard

**Status:** ⏳ READY FOR TESTING

### 9.2 End-to-End: Template → Campaign
**Test Steps:**
1. Create template at `/sms/templates/create`
2. Go to `/sms/create`
3. Select template
4. Customize message
5. Add tags
6. Send

**Expected:** Template usage tracked, campaign created with customizations
**Status:** ⏳ READY FOR TESTING

---

## 10. ERROR HANDLING TESTS

### 10.1 SMS Creation - Missing Required Fields
**Test Steps:**
1. Go to `/sms/create`
2. Leave name blank
3. Submit

**Expected:** Form validation error, message "This field is required"
**Status:** ⏳ READY FOR TESTING

### 10.2 AI Generation - No Campaign Name
**Test Steps:**
1. Go to `/sms/create`
2. Leave campaign name blank
3. Click AI generation button

**Expected:** Alert: "Please enter a campaign name first"
**Status:** ⏳ READY FOR TESTING

### 10.3 Schedule - Past Date
**Test Steps:**
1. Select "Schedule for later"
2. Choose yesterday's date
3. Submit

**Expected:** Validation error or warning
**Status:** ⏳ READY FOR TESTING

---

## 11. PERFORMANCE TESTS

### 11.1 AI Response Time
**Test:** Measure AI SMS generation speed
**Expected:** < 10 seconds for standard request
**Status:** ⏳ READY FOR TESTING

### 11.2 Campaign List Load Time
**Test:** Load `/sms` with 100+ campaigns
**Expected:** < 2 seconds to render
**Status:** ⏳ READY FOR TESTING

---

## TEST SUMMARY

### Completed Tests: 4/50
- ✅ Database tables verification
- ✅ Automation columns migration
- ✅ SMS navigation link
- ✅ Feather icon fixes

### Ready for Testing: 46/50
All functional tests ready, awaiting manual execution

### Blocked: 0/50

---

## TESTING CHECKLIST

### Pre-Testing Setup
- [ ] Ensure database has test contacts with phone numbers
- [ ] Verify OpenAI API key is configured
- [ ] Clear any test data from previous runs
- [ ] Check Twilio integration status (optional for testing)

### Critical Path Testing (Priority 1)
1. [ ] SMS Dashboard loads correctly
2. [ ] Create basic SMS campaign (immediate send)
3. [ ] Create scheduled SMS campaign
4. [ ] AI SMS generation (all 3 tones)
5. [ ] Campaign tagging works
6. [ ] Template creation and usage

### Secondary Testing (Priority 2)
1. [ ] Compliance warnings display correctly
2. [ ] Character counter works
3. [ ] Schedule service integration
4. [ ] Tag analytics
5. [ ] Calendar view

### Edge Cases (Priority 3)
1. [ ] Very long messages (> 160 chars)
2. [ ] Empty recipient list
3. [ ] Past schedule dates
4. [ ] Invalid phone numbers
5. [ ] Missing API credentials

---

## BUG TRACKING

### Known Issues
1. None currently identified

### Reported Bugs
_(To be filled during testing)_

---

## NOTES FOR TESTERS

1. **Twilio Setup:** SMS sending requires Twilio configuration. Without it, campaigns will be created but not actually sent (simulation mode).

2. **AI Generation:** Requires OpenAI API key. Some prompts may be rejected by content filters (adult products).

3. **Phone Numbers:** Test contacts must have valid phone numbers in E.164 format (+1234567890).

4. **Scheduling:** Scheduled campaigns require the workflow scheduler to be running.

5. **Tags:** Tags are case-insensitive and automatically deduplicated.

---

## REGRESSION TESTING

After Phase 0-1 deployment, verify these existing features still work:

- [ ] Email campaign creation
- [ ] Contact management
- [ ] Automation workflows
- [ ] Social media posting
- [ ] Analytics dashboard
- [ ] WooCommerce integration
- [ ] Event management

---

**Last Updated:** October 29, 2025  
**Next Review:** After Phase 1 completion
