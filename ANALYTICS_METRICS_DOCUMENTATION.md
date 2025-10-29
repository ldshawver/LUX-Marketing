# LUX Marketing - Comprehensive Analytics Metrics Documentation

## Overview
The comprehensive analytics dashboard displays 6 categories of marketing metrics, pulling data from multiple sources including Google Analytics 4 (GA4), email campaigns, social media, and the internal database.

---

## Data Sources & Integration

### 1. Google Analytics 4 (GA4)
**Integration File**: `integrations/ga4_client.py`

**Configuration**:
- Property ID: Set via `GA4_PROPERTY_ID` environment variable
- Authentication: Service account JSON via `GA4_SERVICE_ACCOUNT_JSON` environment variable
- Library: `google-analytics-data` Python package

**Metrics Retrieved**:
- Sessions
- Total Users
- New Users
- Page Views
- Average Session Duration
- Engagement Rate
- Bounce Rate

**Query Method**: Uses GA4 Data API v1 Beta to fetch metrics for specified date ranges (7, 30, 60, or 90 days)

### 2. Email Campaign Data
**Database Tables**: `Campaign`, `CampaignRecipient`, `EmailTracking`

**Metrics Calculated**:
- Total emails sent
- Email opens (from `EmailTracking` where `event_type='opened'`)
- Email clicks (from `EmailTracking` where `event_type='clicked'`)
- Open rate and click-through rate

### 3. Social Media Data
**Database Table**: `SocialPost`

**Metrics Calculated**:
- Impressions (from `engagement_data` JSON field)
- Reach (from `engagement_data` JSON field)
- Social posts published

### 4. Contact/Lead Data
**Database Table**: `Contact`

**Metrics Calculated**:
- New contacts/leads
- Active contacts
- Churned contacts
- Contact growth rate

---

## 6 Metric Categories Explained

### 1. AWARENESS METRICS
**Purpose**: Measure brand visibility and reach

| Metric | Data Source | Calculation |
|--------|-------------|-------------|
| **Impressions** | Social Media (`SocialPost.engagement_data`) | Sum of all impressions from published social posts. If no data, estimates 500 per post. |
| **Reach** | Social Media (`SocialPost.engagement_data`) | Sum of unique users reached. If no data, estimates 300 per post. |
| **Website Traffic** | GA4 (`new_users`) | Real-time new users from GA4. Falls back to new contacts if GA4 unavailable. |
| **Page Views** | GA4 (`screenPageViews`) | Total page views from GA4 in the period. |
| **Sessions** | GA4 (`sessions`) | Total sessions from GA4 in the period. |
| **Brand Awareness Score** | Manual/Survey | Placeholder at 85%. Can integrate with survey tools. |

**Code Location**: `agents/analytics_agent.py` → `calculate_comprehensive_metrics()` → Lines 551-579

---

### 2. ENGAGEMENT METRICS
**Purpose**: Measure audience interaction with content

| Metric | Data Source | Calculation |
|--------|-------------|-------------|
| **Email Open Rate** | Email Tracking | `(total_opens / total_emails_sent) × 100` |
| **Click-Through Rate (CTR)** | Email Tracking | `(total_clicks / total_emails_sent) × 100` |
| **Avg Time on Site** | GA4 (`averageSessionDuration`) | Average session duration in seconds from GA4. Falls back to 145s placeholder. |
| **Social Engagement Rate** | GA4 (`engagementRate`) | Engagement rate from GA4 (% of engaged sessions). Falls back to 3.2% placeholder. |
| **Bounce Rate** | GA4 (`bounceRate`) | Percentage of single-page sessions from GA4. |
| **Total Opens** | Email Tracking | Count of all email open events. |
| **Total Clicks** | Email Tracking | Count of all email click events. |

**Code Location**: `agents/analytics_agent.py` → Lines 581-608

**Industry Benchmarks**:
- Average Email Open Rate: 21.33%
- Average Email Click Rate: 2.62%

---

### 3. ACQUISITION METRICS
**Purpose**: Measure new customer and lead generation

| Metric | Data Source | Calculation |
|--------|-------------|-------------|
| **Leads Generated** | Contact Database | `Contact.query.filter(created_at >= period_start).count()` |
| **Cost Per Lead (CPL)** | Estimated | `estimated_ad_spend / leads_generated` |
| **Conversion Rate** | Contact + Email | `(new_leads / total_emails_sent) × 100` |
| **Customer Acquisition Cost (CAC)** | Estimated | `estimated_ad_spend / leads_generated` |
| **Lead Quality Score** | Manual | Placeholder at 7.5/10. Can integrate with lead scoring system. |
| **Leads Growth** | Contact Database | `((current_period_leads - previous_period_leads) / previous_period_leads) × 100` |

**Ad Spend Estimation**: `Number of campaigns × $50 per campaign`

**Code Location**: `agents/analytics_agent.py` → Lines 610-627

---

### 4. REVENUE METRICS
**Purpose**: Track sales performance and monetization

| Metric | Data Source | Calculation |
|--------|-------------|-------------|
| **Total Revenue** | Estimated | `new_leads × $150 (average order value)` |
| **Average Order Value (AOV)** | WooCommerce/Manual | Default: $150. Can integrate with WooCommerce for real data. |
| **Return on Ad Spend (ROAS)** | Revenue + Ad Spend | `total_revenue / estimated_ad_spend` |
| **Revenue Per Contact** | Revenue + Contact | `total_revenue / total_contacts` |
| **Revenue Growth** | Historical Comparison | Placeholder at 15.3%. Calculate from historical revenue data. |

**Future Enhancement**: Integrate with WooCommerce API (`woocommerce_service.py`) to pull actual order and revenue data.

**Code Location**: `agents/analytics_agent.py` → Lines 629-639

---

### 5. RETENTION METRICS
**Purpose**: Measure customer loyalty and lifetime value

| Metric | Data Source | Calculation |
|--------|-------------|-------------|
| **Customer Lifetime Value (CLV)** | Historical/Estimated | Default: $1,250. Calculate from `(average_order_value × purchase_frequency × customer_lifespan)` |
| **Repeat Purchase Rate** | WooCommerce/Estimated | Default: 35%. Percentage of customers who make multiple purchases. |
| **Churn Rate** | Contact Database | `(churned_contacts / total_contacts) × 100` where churned = `is_active=False` |
| **Net Promoter Score (NPS)** | Survey/Manual | Default: 52. Integrate with survey tools for real data. |
| **Customer Retention Rate** | Contact Database | `((total_contacts - churned) / total_contacts) × 100` |
| **Active Engagement Rate** | Contact Database | `(contacts_with_recent_activity / total_contacts) × 100` |

**Active Contact Definition**: Contact with `last_activity >= period_start`

**Code Location**: `agents/analytics_agent.py` → Lines 641-659

---

### 6. EFFICIENCY METRICS
**Purpose**: Measure marketing ROI and resource optimization

| Metric | Data Source | Calculation |
|--------|-------------|-------------|
| **Marketing ROI** | Revenue + Costs | `((revenue - total_marketing_cost) / total_marketing_cost) × 100` |
| **Cost Per Acquisition (CPA)** | Costs + Leads | `total_marketing_cost / new_leads` |
| **Funnel Conversion Rate** | Multi-source | `(new_leads / (emails_sent + website_traffic)) × 100` |
| **Email Efficiency** | Email Tracking | `(total_clicks / total_opens) × 100` (click-to-open rate) |
| **Campaign Efficiency Score** | AI Analysis | Default: 8.2/10. Can be calculated by AI agent based on all metrics. |
| **Cost Per Click (CPC)** | Ad Spend + Clicks | `estimated_ad_spend / total_clicks` |

**Marketing Cost Calculation**: `Ad spend + $2,000 operational costs`

**Code Location**: `agents/analytics_agent.py` → Lines 661-673

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER REQUEST                              │
│         /analytics/comprehensive?period_days=30              │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              routes.py → comprehensive_analytics()           │
│         Calls: AnalyticsAgent.calculate_comprehensive_metrics│
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│        AnalyticsAgent.calculate_comprehensive_metrics()      │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  1. Initialize GA4 Client (integrations/ga4_client.py) │ │
│  │     - Check if GA4_PROPERTY_ID exists                  │ │
│  │     - Check if GA4_SERVICE_ACCOUNT_JSON exists         │ │
│  │     - Authenticate with Google                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  2. Fetch GA4 Metrics (if configured)                  │ │
│  │     - Sessions, Users, Page Views                      │ │
│  │     - Session Duration, Engagement Rate, Bounce Rate   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  3. Query Database Tables                              │ │
│  │     - SocialPost (impressions, reach)                  │ │
│  │     - Campaign & CampaignRecipient (emails sent)       │ │
│  │     - EmailTracking (opens, clicks)                    │ │
│  │     - Contact (leads, churn, activity)                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  4. Calculate All 6 Metric Categories                  │ │
│  │     - Awareness (GA4 + Social)                         │ │
│  │     - Engagement (GA4 + Email)                         │ │
│  │     - Acquisition (Contact DB + Calculations)          │ │
│  │     - Revenue (Estimates + WooCommerce future)         │ │
│  │     - Retention (Contact DB + Calculations)            │ │
│  │     - Efficiency (Combined calculations)               │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  5. Return JSON Response                               │ │
│  │     {                                                  │ │
│  │       "success": true,                                 │ │
│  │       "metrics": {                                     │ │
│  │         "awareness": {...},                            │ │
│  │         "engagement": {...},                           │ │
│  │         "acquisition": {...},                          │ │
│  │         "revenue": {...},                              │ │
│  │         "retention": {...},                            │ │
│  │         "efficiency": {...}                            │ │
│  │       }                                                │ │
│  │     }                                                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│     templates/analytics_comprehensive.html                   │
│         Renders all 6 metric categories in cards            │
└─────────────────────────────────────────────────────────────┘
```

---

## Environment Variables Required

| Variable | Purpose | Example |
|----------|---------|---------|
| `GA4_PROPERTY_ID` | GA4 Property ID | `404105265` |
| `GA4_SERVICE_ACCOUNT_JSON` | Service account credentials | JSON string from service account key file |
| `OPENAI_API_KEY` | AI-powered insights (optional) | `sk-...` |

---

## Fallback Behavior

When GA4 is **not configured** or **unavailable**:

1. **Website Traffic**: Falls back to counting new contacts from database
2. **Avg Time on Site**: Uses placeholder value (145 seconds)
3. **Social Engagement Rate**: Uses placeholder value (3.2%)
4. **Bounce Rate**: Returns 0 or omitted

When **no social posts** exist:
- Impressions and Reach estimate based on typical values per post

When **no email campaigns** sent:
- Open rate and CTR default to 0%

---

## Future Enhancements

### 1. WooCommerce Integration
- Pull actual revenue, orders, and AOV from WooCommerce API
- Calculate true ROAS and revenue growth
- Link customers to contacts for accurate CLV

**File to enhance**: `woocommerce_service.py`

### 2. Enhanced Social Media Integration
- Connect to Facebook/LinkedIn/Instagram APIs
- Pull real impressions, reach, and engagement data
- Track follower growth and content performance

### 3. Survey Integration for NPS
- Integrate with survey tools (Typeform, SurveyMonkey)
- Automatically calculate NPS from customer feedback
- Track brand awareness scores

### 4. Advanced Lead Scoring
- AI-powered lead quality scoring
- Behavioral scoring based on email/website engagement
- Predictive lead-to-customer conversion probability

### 5. Real-time Data Updates
- WebSocket connection for live metric updates
- Streaming analytics from GA4
- Real-time campaign performance tracking

---

## API Endpoints

### Get Comprehensive Metrics
```
GET /analytics/comprehensive?period_days=30
```

**Query Parameters**:
- `period_days` (optional): Number of days to look back (default: 30)
  - Options: 7, 30, 60, 90

**Response**:
```json
{
  "success": true,
  "period_days": 30,
  "period_start": "2025-09-29T06:45:00",
  "period_end": "2025-10-29T06:45:00",
  "metrics": {
    "awareness": {
      "impressions": 5000,
      "reach": 3000,
      "website_traffic": 1250,
      "brand_awareness_score": 85,
      "page_views": 8500,
      "sessions": 1450
    },
    "engagement": {
      "email_open_rate": 28.5,
      "click_through_rate": 4.2,
      "avg_time_on_site": 185.5,
      "social_engagement_rate": 4.8,
      "total_opens": 1425,
      "total_clicks": 210,
      "bounce_rate": 42.3
    },
    "acquisition": {
      "leads_generated": 156,
      "cost_per_lead": 12.82,
      "conversion_rate": 3.1,
      "customer_acquisition_cost": 12.82,
      "lead_quality_score": 7.5,
      "leads_growth": 18.5
    },
    "revenue": {
      "total_revenue": 23400,
      "average_order_value": 150.0,
      "return_on_ad_spend": 11.7,
      "revenue_per_contact": 18.72,
      "revenue_growth": 15.3
    },
    "retention": {
      "customer_lifetime_value": 1250.0,
      "repeat_purchase_rate": 35.0,
      "churn_rate": 2.8,
      "net_promoter_score": 52,
      "customer_retention_rate": 97.2,
      "active_engagement_rate": 68.5
    },
    "efficiency": {
      "marketing_roi": 1070.0,
      "cost_per_acquisition": 14.10,
      "funnel_conversion_rate": 2.5,
      "email_efficiency": 14.7,
      "campaign_efficiency_score": 8.2,
      "cost_per_click": 9.52
    }
  },
  "generated_at": "2025-10-29T06:45:00"
}
```

---

## Testing & Validation

To verify metrics are calculating correctly:

1. **Check GA4 Connection**:
   ```python
   from integrations.ga4_client import get_ga4_client
   ga4 = get_ga4_client()
   print(ga4.is_configured())  # Should return True
   print(ga4.get_metrics(days=7))  # Should return GA4 data
   ```

2. **Test Analytics Agent**:
   ```python
   from agents.analytics_agent import AnalyticsAgent
   agent = AnalyticsAgent()
   result = agent.calculate_comprehensive_metrics({'period_days': 30})
   print(result)
   ```

3. **Verify Dashboard**:
   - Navigate to `/analytics/comprehensive`
   - Check all 6 metric cards display
   - Change period filter (7, 30, 60, 90 days)
   - Verify metrics update accordingly

---

## Troubleshooting

### GA4 Not Connecting
- Verify `GA4_PROPERTY_ID` is set correctly
- Check `GA4_SERVICE_ACCOUNT_JSON` contains valid JSON
- Ensure service account has Analytics Data API access
- Check logs for authentication errors

### Metrics Show Zero
- Verify database has data (campaigns, contacts, social posts)
- Check date range filter isn't excluding all data
- Confirm GA4 property has recent traffic

### Dashboard Not Loading
- Check server logs for errors
- Verify all dependencies are installed (`google-analytics-data`)
- Ensure Analytics Agent initializes without errors

---

## Maintenance

### Regular Updates Needed:
1. **Industry Benchmarks**: Update quarterly based on latest research
2. **Placeholder Values**: Replace with real integrations (NPS, Brand Awareness)
3. **Ad Spend Estimates**: Calibrate based on actual marketing spend
4. **CLV Calculation**: Refine with historical purchase data

### Monitoring:
- Track GA4 API quota usage
- Monitor database query performance
- Log calculation errors for debugging
- Set up alerts for metric anomalies

---

**Last Updated**: October 29, 2025
**Version**: 1.0
**Maintained by**: LUX Marketing Development Team
