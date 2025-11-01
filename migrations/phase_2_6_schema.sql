-- LUX Marketing - Phases 2-6 Database Migration
-- Run this script on production database to add new tables
-- This is safe to run multiple times (CREATE TABLE IF NOT EXISTS)

-- ===== PHASE 2: SEO & ANALYTICS MODULE =====
CREATE TABLE IF NOT EXISTS seo_keyword (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(255) NOT NULL,
    target_url VARCHAR(500),
    search_volume INTEGER DEFAULT 0,
    difficulty INTEGER DEFAULT 0,
    current_position INTEGER,
    previous_position INTEGER,
    best_position INTEGER,
    search_engine VARCHAR(20) DEFAULT 'google',
    location VARCHAR(100) DEFAULT 'US',
    device VARCHAR(20) DEFAULT 'desktop',
    is_tracking BOOLEAN DEFAULT TRUE,
    last_checked TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS keyword_ranking (
    id SERIAL PRIMARY KEY,
    keyword_id INTEGER REFERENCES seo_keyword(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    url VARCHAR(500),
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    ctr FLOAT DEFAULT 0.0,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS seo_backlink (
    id SERIAL PRIMARY KEY,
    source_url VARCHAR(500) NOT NULL,
    source_domain VARCHAR(255),
    target_url VARCHAR(500) NOT NULL,
    anchor_text VARCHAR(255),
    link_type VARCHAR(20) DEFAULT 'dofollow',
    status VARCHAR(20) DEFAULT 'active',
    domain_authority INTEGER DEFAULT 0,
    page_authority INTEGER DEFAULT 0,
    spam_score INTEGER DEFAULT 0,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    lost_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS seo_competitor (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    domain VARCHAR(255) NOT NULL UNIQUE,
    organic_traffic INTEGER DEFAULT 0,
    organic_keywords INTEGER DEFAULT 0,
    backlinks INTEGER DEFAULT 0,
    domain_authority INTEGER DEFAULT 0,
    page_authority INTEGER DEFAULT 0,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_analyzed TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS competitor_snapshot (
    id SERIAL PRIMARY KEY,
    competitor_id INTEGER REFERENCES seo_competitor(id) ON DELETE CASCADE,
    organic_traffic INTEGER DEFAULT 0,
    organic_keywords INTEGER DEFAULT 0,
    backlinks INTEGER DEFAULT 0,
    domain_authority INTEGER DEFAULT 0,
    top_keywords JSON,
    snapshot_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS seo_audit (
    id SERIAL PRIMARY KEY,
    url VARCHAR(500) NOT NULL,
    audit_type VARCHAR(50) DEFAULT 'full',
    overall_score INTEGER DEFAULT 0,
    technical_score INTEGER DEFAULT 0,
    content_score INTEGER DEFAULT 0,
    performance_score INTEGER DEFAULT 0,
    mobile_score INTEGER DEFAULT 0,
    issues_found JSON,
    recommendations JSON,
    audit_data JSON,
    status VARCHAR(20) DEFAULT 'completed',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS seo_page (
    id SERIAL PRIMARY KEY,
    url VARCHAR(500) NOT NULL UNIQUE,
    title VARCHAR(255),
    meta_description VARCHAR(500),
    h1_tag VARCHAR(255),
    word_count INTEGER DEFAULT 0,
    internal_links INTEGER DEFAULT 0,
    external_links INTEGER DEFAULT 0,
    images_count INTEGER DEFAULT 0,
    images_without_alt INTEGER DEFAULT 0,
    page_speed INTEGER DEFAULT 0,
    mobile_friendly BOOLEAN DEFAULT TRUE,
    schema_markup JSON,
    canonical_url VARCHAR(500),
    status_code INTEGER DEFAULT 200,
    last_crawled TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== PHASE 3: EVENT ENHANCEMENTS =====
CREATE TABLE IF NOT EXISTS event_ticket (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES event(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price FLOAT NOT NULL,
    quantity_total INTEGER NOT NULL,
    quantity_sold INTEGER DEFAULT 0,
    sale_start TIMESTAMP,
    sale_end TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ticket_purchase (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER REFERENCES event_ticket(id) ON DELETE CASCADE,
    contact_id INTEGER REFERENCES contact(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 1,
    total_amount FLOAT NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'pending',
    payment_method VARCHAR(50),
    transaction_id VARCHAR(100),
    ticket_codes JSON,
    checked_in BOOLEAN DEFAULT FALSE,
    check_in_time TIMESTAMP,
    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS event_check_in (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES event(id) ON DELETE CASCADE,
    contact_id INTEGER REFERENCES contact(id) ON DELETE CASCADE,
    ticket_purchase_id INTEGER REFERENCES ticket_purchase(id),
    check_in_method VARCHAR(50) DEFAULT 'manual',
    checked_in_by VARCHAR(100),
    checked_in_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- ===== PHASE 4: SOCIAL MEDIA EXPANSION =====
CREATE TABLE IF NOT EXISTS social_media_account (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    account_name VARCHAR(100) NOT NULL,
    account_id VARCHAR(100),
    access_token VARCHAR(500),
    refresh_token VARCHAR(500),
    token_expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    follower_count INTEGER DEFAULT 0,
    last_synced TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS social_media_schedule (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES social_media_account(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    media_urls JSON,
    hashtags VARCHAR(500),
    scheduled_for TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'scheduled',
    post_id VARCHAR(100),
    engagement_metrics JSON,
    posted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS social_media_cross_post (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    media_urls JSON,
    platforms JSON,
    scheduled_for TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'scheduled',
    post_results JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===== PHASE 5: ADVANCED AUTOMATIONS =====
CREATE TABLE IF NOT EXISTS automation_test (
    id SERIAL PRIMARY KEY,
    automation_id INTEGER REFERENCES automation(id) ON DELETE CASCADE,
    test_contact_id INTEGER REFERENCES contact(id),
    test_data JSON,
    test_results JSON,
    status VARCHAR(20) DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS automation_trigger_library (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    trigger_type VARCHAR(50) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    trigger_config JSON,
    steps_template JSON,
    is_predefined BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS automation_ab_test (
    id SERIAL PRIMARY KEY,
    automation_id INTEGER REFERENCES automation(id) ON DELETE CASCADE,
    step_id INTEGER REFERENCES automation_step(id) ON DELETE CASCADE,
    variant_a_template_id INTEGER REFERENCES email_template(id),
    variant_b_template_id INTEGER REFERENCES email_template(id),
    split_percentage INTEGER DEFAULT 50,
    winner_criteria VARCHAR(50) DEFAULT 'open_rate',
    status VARCHAR(20) DEFAULT 'running',
    variant_a_sent INTEGER DEFAULT 0,
    variant_b_sent INTEGER DEFAULT 0,
    variant_a_opens INTEGER DEFAULT 0,
    variant_b_opens INTEGER DEFAULT 0,
    variant_a_clicks INTEGER DEFAULT 0,
    variant_b_clicks INTEGER DEFAULT 0,
    winner_variant VARCHAR(1),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Migration complete
-- All 16 new tables added successfully
