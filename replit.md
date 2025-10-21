# Email Marketing Automation Bot

## Overview

This is a comprehensive **multi-channel marketing automation platform** built with Flask. The system enables users to manage contacts, create email templates, design marketing campaigns, send SMS messages, schedule social media posts, manage events, and track performance analytics across all channels. It integrates with Microsoft Graph API for email delivery, Twilio for SMS, OpenAI for AI-powered content generation, and provides a complete workflow from contact management to campaign execution and analytics.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 dark theme
- **Static Assets**: Custom CSS and JavaScript for enhanced user experience
- **UI Components**: Responsive design with Feather icons and Bootstrap components
- **Page Structure**: Modular template inheritance with base.html as foundation

### Backend Architecture
- **Framework**: Flask web framework with Blueprint-based modular routing
- **Authentication**: Flask-Login for session management with password hashing
- **Database ORM**: SQLAlchemy with declarative base for database operations
- **Background Tasks**: APScheduler for campaign scheduling and automated email sending
- **Email Service**: Dedicated EmailService class handling Microsoft Graph API integration

### Data Storage Solutions
- **Primary Database**: SQLite (configurable to other databases via SQLAlchemy)
- **Schema Design**: Relational model with Users, Contacts, EmailTemplates, Campaigns, CampaignRecipients, and EmailTracking tables
- **Connection Management**: Connection pooling with health checks and automatic reconnection

### Authentication and Authorization
- **User Management**: Flask-Login with secure password hashing using Werkzeug
- **Session Security**: Configurable session secrets with secure cookie handling
- **Access Control**: Login required decorators protecting all main functionality
- **User Registration**: Admin-only user creation system

### Email Delivery System
- **Provider**: Microsoft Graph API for enterprise-grade email delivery
- **Authentication**: MSAL (Microsoft Authentication Library) with client credentials flow
- **Template Processing**: Jinja2 template rendering with contact personalization
- **Tracking**: Open and click tracking with unique tracking pixels and links

### Campaign Management
- **Scheduling**: Background scheduler for automated campaign execution
- **Status Tracking**: Comprehensive campaign status management (draft, scheduled, sending, sent, failed, paused)
- **Recipient Management**: Tag-based contact filtering and bulk operations
- **Analytics**: Real-time tracking of delivery, opens, clicks, and engagement metrics

## External Dependencies

### Microsoft Graph API Integration
- **Service**: Microsoft 365 email delivery service
- **Authentication**: OAuth 2.0 with tenant-specific configuration
- **Required Credentials**: Client ID, Client Secret, and Tenant ID
- **Permissions**: Mail.Send application permission for sending emails

### OpenAI Integration (LUX AI Agent)
- **Service**: OpenAI GPT-4o for automated email marketing intelligence
- **Authentication**: API key-based authentication
- **Features**: Campaign generation, content optimization, audience analysis
- **Agent Name**: LUX - Automated Email Marketing Assistant
- **DALL-E Integration**: Automatic image generation for email campaigns
- **WooCommerce Integration**: Product-focused campaigns with live product data

### Python Libraries
- **Flask**: Web framework with SQLAlchemy, Login, and other extensions
- **MSAL**: Microsoft Authentication Library for Graph API access
- **APScheduler**: Background task scheduling for automated campaigns
- **Jinja2**: Template engine for email content personalization
- **Werkzeug**: WSGI utilities and security functions
- **OpenAI**: AI-powered content generation and optimization
- **Twilio**: SMS marketing and communication platform

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme support
- **Feather Icons**: Lightweight icon set for consistent UI
- **Custom CSS/JS**: Enhanced user experience and form validations

### Database Configuration
- **SQLAlchemy**: ORM supporting multiple database backends
- **Default**: SQLite for development (easily configurable for PostgreSQL, MySQL)
- **Features**: Connection pooling, health checks, and migration support

## Production Deployment (October 21, 2025)

### VPS Deployment Details
- **Server**: Hostinger VPS at 194.195.92.52
- **Domain**: https://lux.lucifercruz.com
- **Application Path**: /var/www/lux-marketing
- **System User**: luxapp:www-data
- **Database**: PostgreSQL (luxuser@localhost/lux_marketing)

### Production Stack
- **Web Server**: Nginx 1.22.1 with SSL/TLS (Let's Encrypt)
- **Application Server**: Gunicorn with 4 workers
- **Process Manager**: systemd (lux-marketing.service)
- **Python Environment**: Virtual environment at /var/www/lux-marketing/venv
- **Log Location**: /var/log/lux-marketing/ and journalctl

### Security Configuration
- **Environment Variables**: /etc/lux/lux-marketing.env (640 permissions, root:luxapp)
- **Systemd Hardening**: ProtectSystem=strict, ProtectHome=true, NoNewPrivileges=true
- **SSL/TLS**: Full HTTPS with automatic HTTP→HTTPS redirect
- **Admin Account**: Initial admin user (password must be changed on first deployment)

### Service Management
- **Start**: systemctl start lux-marketing.service
- **Stop**: systemctl stop lux-marketing.service
- **Restart**: systemctl restart lux-marketing.service
- **Status**: systemctl status lux-marketing.service
- **Logs**: journalctl -u lux-marketing.service -f

### Database Schema
All tables successfully created:
- User (with admin authentication)
- Contact (email marketing contacts)
- EmailTemplate (reusable email templates)
- Campaign (marketing campaigns)
- CampaignRecipient (campaign delivery tracking)
- EmailTracking (analytics events)
- BrandKit (branding configurations)
- Automation (workflow automation)
- AutomationStep (workflow steps)
- Segment (contact segments)
- SegmentMember (segment membership)
- ABTest (A/B testing campaigns)
- EmailComponent (template components)

### Recent Changes (October 21, 2025)
- Fixed circular dependency between Campaign and ABTest models
- Deployed complete application to production VPS
- Configured systemd service with security hardening
- Set up Nginx reverse proxy with SSL
- Initialized PostgreSQL database with all schemas
- Configured OpenAI API key for LUX AI agent
- Added SMS Marketing feature with Twilio integration (campaigns, compliance, delivery tracking)
- Added Social Media Marketing feature (Facebook, Instagram, LinkedIn, Twitter scheduling with AI captions)
- Added SEO Tools feature (page analysis, meta optimization, content recommendations)
- Added Events Management feature (registration tracking, free events only)
- Fixed A/B Testing template error (preview_campaign link)
- Verified Automations dashboard functionality
- Configured Twilio credentials via environment secrets (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER)
- User declined Stripe integration (Events feature supports free events only, no paid registrations)