# Email Marketing Automation Bot

## Overview

This is a comprehensive email marketing automation platform built with Flask. The system enables users to manage contacts, create email templates, design marketing campaigns, and track email performance analytics. It integrates with Microsoft Graph API for email delivery and provides a complete workflow from contact management to campaign execution and analytics.

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

### Python Libraries
- **Flask**: Web framework with SQLAlchemy, Login, and other extensions
- **MSAL**: Microsoft Authentication Library for Graph API access
- **APScheduler**: Background task scheduling for automated campaigns
- **Jinja2**: Template engine for email content personalization
- **Werkzeug**: WSGI utilities and security functions
- **OpenAI**: AI-powered content generation and optimization

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme support
- **Feather Icons**: Lightweight icon set for consistent UI
- **Custom CSS/JS**: Enhanced user experience and form validations

### Database Configuration
- **SQLAlchemy**: ORM supporting multiple database backends
- **Default**: SQLite for development (easily configurable for PostgreSQL, MySQL)
- **Features**: Connection pooling, health checks, and migration support