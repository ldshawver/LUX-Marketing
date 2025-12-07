# LUX Marketing Platform - Project Documentation

## Overview
LUX Marketing is a comprehensive multi-channel marketing automation platform designed to streamline marketing efforts. It features a tile-based dashboard with 11 AI agents, AI-powered campaign generation using GPT-4o, and seamless contact capture via Zapier webhooks. The platform includes an advanced error logging and diagnostics system, an AI chatbot with auto-repair capabilities, and robust integrations with major social media platforms for content publishing and management. Its core ambition is to provide a launch-ready, automated marketing solution with centralized management for all integrations and API keys.

## User Preferences
- Black background with purple, cyan, pink branding
- Launch-ready with all features on Replit and VPS
- Automated systems that work without manual intervention
- Clear error diagnostics and auto-repair capabilities
- Centralized API keys & secrets management (not scattered modal dialogs)
- All social media platforms available in Settings → Integrations for all companies

## System Architecture
The platform is built around a tile-based dashboard with 11 AI agents. It leverages GPT-4o for AI-powered campaign generation. UI/UX features a pure black background accented with brand colors (purple, cyan, pink). Authentication is handled via Replit Auth OAuth, supporting Google, GitHub, Apple, and email sign-in, with JWKS-based JWT signature verification for security.

Key technical implementations include:
- **Social Media Integrations**: Full OAuth 2.0 implementations for Instagram and TikTok, supporting content publishing, media listing, and insights. This includes handling OAuth flows, encrypted token storage, token refresh mechanisms, and comprehensive scope management for each platform.
- **Centralized API Keys & Secrets Management**: A dedicated section in Settings → Integrations allows for secure, encrypted storage and management of API keys and secrets for various platforms (TikTok, Instagram, Facebook, Reddit, YouTube, LinkedIn, Snapchat, X/Twitter). All secrets are encrypted and stored per company.
- **Zapier Webhook Integration**: An authenticated endpoint (`/api/webhook/zapier-contact`) accepts JSON payloads for contact capture, enabling auto-segmentation for newsletter signups.
- **Error Logging & Diagnostics**: A robust system logs all application errors to a `error_log` database table, capturing details like type, message, stack trace, and severity. Diagnostic endpoints provide system health and error retrieval.
- **AI Chatbot with Auto-Repair**: The chatbot acts as a marketing assistant, error detector, and troubleshooter. It can analyze server logs (Nginx, Gunicorn, Systemd, app logs) and trigger an automated error repair system. The auto-repair mechanism uses ChatGPT to generate fix plans, tests resolutions, and automatically marks errors as resolved. It supports both automatic and manual triggers for repair sequences.
- **Keyword Research Integrations**: Multi-provider keyword research supporting DataForSEO (affordable $50/mo), SEMrush (premium $120/mo), and Moz (domain authority). Endpoints: `/api/keyword-research/research`, `/api/keyword-research/suggestions`, `/api/keyword-research/providers`
- **Event Integrations**: Multi-provider event search supporting Eventbrite and Ticketmaster. Endpoints: `/api/events/search`, `/api/events/local`, `/api/events/providers`

## External Dependencies
- **OpenAI API**: Used for AI-powered campaign generation and the AI chatbot's capabilities, including error diagnosis and auto-repair plan generation.
- **Zapier**: Integrated via webhooks for contact capture and automation.
- **Replit Auth (OpenID Connect)**: Provides secure OAuth authentication for user login (Google, GitHub, Apple, email).
- **Instagram Graph API**: For Instagram OAuth 2.0 integration, enabling profile access, content publishing, comment management, and insights.
- **TikTok API**: For TikTok OAuth 2.0 integration, supporting user info, video listing, upload, and publishing.
- **Facebook API**: For Facebook Page integration (indirectly via Instagram Business accounts) and potentially direct Facebook Page management.
- **Reddit API**: For Reddit integration, requiring client ID, client secret, username, and password.
- **YouTube Data API**: For YouTube integration, requiring an API Key and Channel ID.
- **LinkedIn API**: For LinkedIn integration, requiring client ID, client secret, and access token.
- **Snapchat API**: For Snapchat integration, requiring Business Account ID and access token.
- **X (formerly Twitter) API**: For Twitter integration, requiring API key, API secret, bearer token, client ID, and client secret.
- **DataForSEO API**: Affordable keyword research data ($50/mo) - login/password authentication
- **SEMrush API**: Premium keyword and competitor data ($120/mo) - API key authentication
- **Moz API**: Domain authority and keyword difficulty - access ID/secret key authentication
- **Eventbrite API**: Local events, ticketing, categories - bearer token authentication
- **Ticketmaster Discovery API**: Concerts, sports, theater, venues, attractions - API key authentication
- **PostgreSQL**: Primary database for storing application data, including `error_log` and `Contact` information.

## Recent Changes (Dec 7, 2025)
- Created `integrations/keyword_research.py` with DataForSEO, SEMrush, and Moz clients
- Created `integrations/events.py` with Eventbrite and Ticketmaster clients
- Added 6 new API endpoints for keyword research and event integrations
- All integrations load credentials from CompanySecret model via Settings → Integrations
- Credentials stored per company: `dataforseo_login`/`password`, `semrush_api_key`, `moz_access_id`/`secret_key`, `eventbrite_api_key`, `ticketmaster_api_key`
