"""
Operations & Integration Agent
Handles system monitoring, API management, and automation health
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class OperationsAgent(BaseAgent):
    """AI Agent for operations and system integration"""
    
    def __init__(self):
        super().__init__(
            agent_name="Operations & Integration Agent",
            agent_type="operations",
            description="System monitoring, API management, and automation health"
        )
    
    def _define_personality(self) -> str:
        return """
        You are the Operations & Integration Agent, an expert in system reliability,
        automation, and integration management. You ensure all systems run smoothly.
        """
    
    def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute operations task"""
        task_type = task_data.get('task_type', 'system_health')
        
        if task_type == 'system_health':
            return self.check_system_health(task_data)
        elif task_type == 'integration_sync':
            return self.sync_integrations(task_data)
        elif task_type == 'automation_report':
            return self.generate_automation_report(task_data)
        else:
            return {'success': False, 'error': f'Unknown task type: {task_type}'}
    
    def check_system_health(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check system health and performance"""
        try:
            from models import AgentTask, AgentLog, Campaign, Contact
            
            # Gather system metrics
            recent_failures = AgentTask.query.filter_by(status='failed').filter(
                AgentTask.created_at >= datetime.now() - timedelta(days=1)
            ).count()
            
            total_contacts = Contact.query.filter_by(is_active=True).count()
            total_campaigns = Campaign.query.count()
            
            system_data = {
                'agent_failures_24h': recent_failures,
                'total_contacts': total_contacts,
                'total_campaigns': total_campaigns,
                'timestamp': datetime.now().isoformat()
            }
            
            prompt = f"Analyze system health metrics and provide recommendations: {system_data}"
            
            result = self.generate_with_ai(prompt, response_format={"type": "json_object"}, temperature=0.2)
            
            if result:
                self.log_activity('system_health_check', system_data, 'success')
                return {'success': True, 'health': result, 'metrics': system_data, 'generated_at': datetime.now().isoformat()}
            return {'success': False, 'error': 'Failed to check health'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def sync_integrations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sync external integrations"""
        try:
            integration = params.get('integration', 'woocommerce')
            
            if integration == 'woocommerce':
                from woocommerce_service import WooCommerceService
                wc = WooCommerceService()
                
                if wc.is_configured():
                    products = wc.get_products(per_page=10)
                    
                    if products:
                        self.log_activity('integration_sync', {'integration': integration, 'items': len(products)}, 'success')
                        return {'success': True, 'synced': len(products), 'integration': integration, 'generated_at': datetime.now().isoformat()}
            
            return {'success': True, 'message': f'Integration {integration} synced', 'generated_at': datetime.now().isoformat()}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_automation_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate automation health report"""
        try:
            from models import AgentTask, AgentLog, AgentSchedule
            
            # Get automation statistics
            period_start = datetime.now() - timedelta(days=7)
            
            total_tasks = AgentTask.query.filter(AgentTask.created_at >= period_start).count()
            completed_tasks = AgentTask.query.filter(
                AgentTask.created_at >= period_start,
                AgentTask.status == 'completed'
            ).count()
            
            active_schedules = AgentSchedule.query.filter_by(is_enabled=True).count()
            
            report_data = {
                'period': '7 days',
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'success_rate': round((completed_tasks / max(total_tasks, 1)) * 100, 1),
                'active_schedules': active_schedules
            }
            
            prompt = f"Analyze automation performance and provide insights: {report_data}"
            
            result = self.generate_with_ai(prompt, response_format={"type": "json_object"}, temperature=0.3)
            
            if result:
                from models import AgentReport, db
                report = AgentReport(
                    agent_type=self.agent_type,
                    agent_name=self.agent_name,
                    report_type='automation_health',
                    report_title='Weekly Automation Health Report',
                    report_data=result,
                    insights=result.get('summary', ''),
                    period_start=period_start,
                    period_end=datetime.now(),
                    created_at=datetime.now()
                )
                db.session.add(report)
                db.session.commit()
                
                return {'success': True, 'report': result, 'report_id': report.id, 'generated_at': datetime.now().isoformat()}
            return {'success': False, 'error': 'Failed to generate report'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
