"""
AI Agent Scheduler
Manages automated execution of all marketing AI agents
"""
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class AgentScheduler:
    """Scheduler for automated agent tasks"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.agents = {}
        logger.info("Agent Scheduler initialized")
    
    def register_agent(self, agent_type: str, agent_instance):
        """Register an agent instance for scheduling"""
        self.agents[agent_type] = agent_instance
        logger.info(f"Registered agent: {agent_type}")
    
    def schedule_brand_strategy_agent(self):
        """Schedule Brand & Strategy Agent - Quarterly strategy updates"""
        if 'brand_strategy' not in self.agents:
            return
        
        agent = self.agents['brand_strategy']
        
        # Quarterly strategy generation - First day of each quarter
        self.scheduler.add_job(
            func=lambda: self._run_agent_task(agent, {
                'task_type': 'quarterly_strategy',
                'quarter': f'Q{((datetime.now().month-1)//3)+1} {datetime.now().year}',
                'business_goals': ['Growth', 'Engagement', 'Revenue'],
                'budget': 'Standard'
            }),
            trigger=CronTrigger(month='1,4,7,10', day=1, hour=9),
            id='brand_quarterly_strategy',
            name='Brand Strategy - Quarterly Planning'
        )
        
        # Monthly market research - First Monday of each month
        self.scheduler.add_job(
            func=lambda: self._run_agent_task(agent, {
                'task_type': 'market_research',
                'industry': 'General',
                'focus_areas': ['trends', 'opportunities']
            }),
            trigger=CronTrigger(day='1-7', day_of_week='mon', hour=10),
            id='brand_monthly_research',
            name='Brand Strategy - Monthly Research'
        )
        
        logger.info("Brand Strategy Agent scheduled")
    
    def schedule_content_seo_agent(self):
        """Schedule Content & SEO Agent - Weekly blog posts"""
        if 'content_seo' not in self.agents:
            return
        
        agent = self.agents['content_seo']
        
        # Weekly blog post generation - Every Monday
        self.scheduler.add_job(
            func=lambda: self._run_agent_task(agent, {
                'task_type': 'blog_post',
                'topic': 'Industry insights and tips',
                'word_count': 1500,
                'tone': 'professional'
            }),
            trigger=CronTrigger(day_of_week='mon', hour=8),
            id='content_weekly_blog',
            name='Content - Weekly Blog Post'
        )
        
        # Monthly content calendar - Last Friday of each month
        self.scheduler.add_job(
            func=lambda: self._run_agent_task(agent, {
                'task_type': 'content_calendar',
                'month': (datetime.now() + timedelta(days=30)).strftime('%B %Y'),
                'frequency': 'weekly'
            }),
            trigger=CronTrigger(day='22-28', day_of_week='fri', hour=14),
            id='content_monthly_calendar',
            name='Content - Monthly Calendar'
        )
        
        logger.info("Content & SEO Agent scheduled")
    
    def schedule_analytics_agent(self):
        """Schedule Analytics Agent - Real-time tracking and reports"""
        if 'analytics' not in self.agents:
            return
        
        agent = self.agents['analytics']
        
        # Weekly performance summary - Every Friday
        self.scheduler.add_job(
            func=lambda: self._run_agent_task(agent, {
                'task_type': 'performance_summary',
                'period_days': 7
            }),
            trigger=CronTrigger(day_of_week='fri', hour=16),
            id='analytics_weekly_summary',
            name='Analytics - Weekly Summary'
        )
        
        # Monthly performance report - First day of month
        self.scheduler.add_job(
            func=lambda: self._run_agent_task(agent, {
                'task_type': 'performance_summary',
                'period_days': 30
            }),
            trigger=CronTrigger(day=1, hour=9),
            id='analytics_monthly_report',
            name='Analytics - Monthly Report'
        )
        
        # Daily optimization recommendations - Every day
        self.scheduler.add_job(
            func=lambda: self._run_agent_task(agent, {
                'task_type': 'optimization_recommendations',
                'focus_area': 'overall'
            }),
            trigger=CronTrigger(hour=7),
            id='analytics_daily_recommendations',
            name='Analytics - Daily Recommendations'
        )
        
        logger.info("Analytics Agent scheduled")
    
    def schedule_creative_agent(self):
        """Schedule Creative Agent - On-demand creative generation"""
        if 'creative_design' not in self.agents:
            return
        
        # Creative agent typically runs on-demand, not on schedule
        # But we can schedule weekly creative asset generation
        
        agent = self.agents['creative_design']
        
        # Weekly creative assets - Every Wednesday
        self.scheduler.add_job(
            func=lambda: self._run_agent_task(agent, {
                'task_type': 'social_media_graphic',
                'message': 'Weekly inspiration',
                'platform': 'instagram',
                'theme': 'modern'
            }),
            trigger=CronTrigger(day_of_week='wed', hour=10),
            id='creative_weekly_assets',
            name='Creative - Weekly Assets'
        )
        
        logger.info("Creative Agent scheduled")
    
    def schedule_additional_agents(self):
        """Schedule remaining 6 agents"""
        # Advertising Agent - Weekly campaign checks
        if 'advertising' in self.agents:
            agent = self.agents['advertising']
            self.scheduler.add_job(
                func=lambda: self._run_agent_task(agent, {'task_type': 'campaign_strategy'}),
                trigger=CronTrigger(day_of_week='wed', hour=11),
                id='advertising_weekly_strategy',
                name='Advertising - Weekly Strategy Review'
            )
            logger.info("Advertising Agent scheduled")
        
        # Social Media Agent - Daily posts
        if 'social_media' in self.agents:
            agent = self.agents['social_media']
            self.scheduler.add_job(
                func=lambda: self._run_agent_task(agent, {'task_type': 'daily_posts'}),
                trigger=CronTrigger(hour=9),
                id='social_daily_posts',
                name='Social Media - Daily Posts'
            )
            logger.info("Social Media Agent scheduled")
        
        # Email CRM Agent - Weekly campaigns
        if 'email_crm' in self.agents:
            agent = self.agents['email_crm']
            self.scheduler.add_job(
                func=lambda: self._run_agent_task(agent, {'task_type': 'weekly_campaign'}),
                trigger=CronTrigger(day_of_week='tue', hour=10),
                id='email_weekly_campaign',
                name='Email CRM - Weekly Campaign'
            )
            logger.info("Email CRM Agent scheduled")
        
        # Sales Enablement Agent - Weekly lead review
        if 'sales_enablement' in self.agents:
            agent = self.agents['sales_enablement']
            self.scheduler.add_job(
                func=lambda: self._run_agent_task(agent, {'task_type': 'lead_scoring'}),
                trigger=CronTrigger(day_of_week='thu', hour=10),
                id='sales_weekly_leads',
                name='Sales Enablement - Weekly Lead Scoring'
            )
            logger.info("Sales Enablement Agent scheduled")
        
        # Retention Agent - Monthly churn analysis
        if 'retention' in self.agents:
            agent = self.agents['retention']
            self.scheduler.add_job(
                func=lambda: self._run_agent_task(agent, {'task_type': 'churn_analysis'}),
                trigger=CronTrigger(day=1, hour=14),
                id='retention_monthly_churn',
                name='Retention - Monthly Churn Analysis'
            )
            logger.info("Retention Agent scheduled")
        
        # Operations Agent - Daily system health
        if 'operations' in self.agents:
            agent = self.agents['operations']
            self.scheduler.add_job(
                func=lambda: self._run_agent_task(agent, {'task_type': 'system_health'}),
                trigger=CronTrigger(hour=6),
                id='operations_daily_health',
                name='Operations - Daily Health Check'
            )
            logger.info("Operations Agent scheduled")
    
    def _run_agent_task(self, agent, task_data: dict):
        """Execute an agent task and log results"""
        try:
            agent_name = agent.agent_name
            logger.info(f"Running scheduled task for {agent_name}")
            
            # Create task in database
            task_id = agent.create_task(
                task_name=task_data.get('task_type', 'scheduled_task'),
                task_data=task_data
            )
            
            # Execute task
            result = agent.execute(task_data)
            
            # Complete task
            if task_id:
                agent.complete_task(
                    task_id,
                    result,
                    status='completed' if result.get('success') else 'failed'
                )
            
            logger.info(f"Completed scheduled task for {agent_name}: {result.get('success', False)}")
            
        except Exception as e:
            logger.error(f"Error running scheduled agent task: {e}")
    
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Agent Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Agent Scheduler stopped")
    
    def get_scheduled_jobs(self):
        """Get list of all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        return jobs


# Global scheduler instance
_agent_scheduler = None


def get_agent_scheduler():
    """Get or create the global agent scheduler instance"""
    global _agent_scheduler
    if _agent_scheduler is None:
        _agent_scheduler = AgentScheduler()
    return _agent_scheduler


def initialize_agent_scheduler():
    """Initialize and start the agent scheduler with all agents"""
    try:
        from agents.brand_strategy_agent import BrandStrategyAgent
        from agents.content_seo_agent import ContentSEOAgent
        from agents.analytics_agent import AnalyticsAgent
        from agents.creative_agent import CreativeAgent
        from agents.advertising_agent import AdvertisingAgent
        from agents.social_media_agent import SocialMediaAgent
        from agents.email_crm_agent import EmailCRMAgent
        from agents.sales_enablement_agent import SalesEnablementAgent
        from agents.retention_agent import RetentionAgent
        from agents.operations_agent import OperationsAgent
        
        scheduler = get_agent_scheduler()
        
        # Register all 10 agents
        scheduler.register_agent('brand_strategy', BrandStrategyAgent())
        scheduler.register_agent('content_seo', ContentSEOAgent())
        scheduler.register_agent('analytics', AnalyticsAgent())
        scheduler.register_agent('creative_design', CreativeAgent())
        scheduler.register_agent('advertising', AdvertisingAgent())
        scheduler.register_agent('social_media', SocialMediaAgent())
        scheduler.register_agent('email_crm', EmailCRMAgent())
        scheduler.register_agent('sales_enablement', SalesEnablementAgent())
        scheduler.register_agent('retention', RetentionAgent())
        scheduler.register_agent('operations', OperationsAgent())
        
        # Schedule all agents
        scheduler.schedule_brand_strategy_agent()
        scheduler.schedule_content_seo_agent()
        scheduler.schedule_analytics_agent()
        scheduler.schedule_creative_agent()
        scheduler.schedule_additional_agents()
        
        # Start scheduler
        scheduler.start()
        
        logger.info("All 10 AI agents initialized and scheduled successfully")
        return scheduler
        
    except Exception as e:
        logger.error(f"Failed to initialize agent scheduler: {e}")
        return None
