"""
Base AI Agent Class
Foundation for all LUX Marketing AI Agents
"""
import os
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from openai import OpenAI

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all AI marketing agents"""
    
    def __init__(self, agent_name: str, agent_type: str, description: str = ""):
        """
        Initialize base agent
        
        Args:
            agent_name: Human-readable name of the agent
            agent_type: Technical identifier (e.g., 'brand_strategy', 'content_seo')
            description: Brief description of agent's purpose
        """
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.description = description
        
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(f"{agent_name}: OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-5-2025-08-07"
        
        self.personality = self._define_personality()
        
        logger.info(f"{self.agent_name} initialized successfully")
    
    def _define_personality(self) -> str:
        """Define the agent's personality and expertise. Override in subclasses."""
        return f"""
        You are {self.agent_name}, an expert AI agent specialized in marketing automation.
        You are professional, data-driven, and focused on delivering actionable results.
        You understand marketing best practices and business objectives.
        """
    
    def generate_with_ai(self, prompt: str, system_prompt: Optional[str] = None, 
                        response_format: Optional[Dict] = None, temperature: float = 0.7) -> Optional[Dict]:
        """
        Generate content using OpenAI GPT-4
        
        Args:
            prompt: User prompt for generation
            system_prompt: Optional system prompt (uses personality if not provided)
            response_format: Optional response format (e.g., {"type": "json_object"})
            temperature: Creativity level (0.0 to 1.0)
            
        Returns:
            Generated content as dict or None on error
        """
        try:
            messages = [
                {"role": "system", "content": system_prompt or self.personality},
                {"role": "user", "content": prompt}
            ]
            
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature
            }
            
            if response_format:
                kwargs["response_format"] = response_format
            
            response = self.client.chat.completions.create(**kwargs)
            
            content = response.choices[0].message.content
            if not content:
                logger.error(f"{self.agent_name}: Received empty response from OpenAI")
                return None
            
            if response_format and response_format.get("type") == "json_object":
                return json.loads(content)
            
            return {"content": content}
            
        except Exception as e:
            logger.error(f"{self.agent_name} AI generation error: {e}")
            return None
    
    def generate_response(self, prompt: str, as_json: bool = True) -> Dict[str, Any]:
        """
        Generate AI response (helper method for agents)
        
        Args:
            prompt: Prompt for AI generation
            as_json: Whether to expect JSON response
            
        Returns:
            Generated response as dict
        """
        response_format = {"type": "json_object"} if as_json else None
        result = self.generate_with_ai(prompt, response_format=response_format)
        return result if result else {}
    
    def generate_image(self, description: str, style: str = "professional marketing") -> Optional[Dict]:
        """
        Generate images using DALL-E 3
        
        Args:
            description: What to generate
            style: Visual style preference
            
        Returns:
            Dict with image_url and metadata or None
        """
        try:
            prompt = f"""
            Create a professional marketing image for: {description}
            
            Style: {style}
            Requirements:
            - High-quality, professional design
            - Suitable for marketing campaigns
            - Clear, engaging visual
            - Modern, clean aesthetic
            """
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard"
            )
            
            image_url = response.data[0].url
            
            return {
                'image_url': image_url,
                'prompt_used': prompt,
                'description': description,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"{self.agent_name} image generation error: {e}")
            return None
    
    def log_activity(self, activity_type: str, details: Dict[str, Any], 
                     status: str = "success") -> None:
        """
        Log agent activity to database
        
        Args:
            activity_type: Type of activity performed
            details: Activity details as dict
            status: Status (success, error, warning)
        """
        try:
            from models import AgentLog, db
            
            log_entry = AgentLog(
                agent_type=self.agent_type,
                agent_name=self.agent_name,
                activity_type=activity_type,
                details=json.dumps(details),
                status=status,
                created_at=datetime.now()
            )
            
            db.session.add(log_entry)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"{self.agent_name} logging error: {e}")
    
    def create_task(self, task_name: str, task_data: Dict[str, Any], 
                   scheduled_at: Optional[datetime] = None) -> Optional[int]:
        """
        Create a task for this agent
        
        Args:
            task_name: Name/description of task
            task_data: Task configuration and parameters
            scheduled_at: When to execute (None = now)
            
        Returns:
            Task ID or None on error
        """
        try:
            from models import AgentTask, db
            
            task = AgentTask(
                agent_type=self.agent_type,
                agent_name=self.agent_name,
                task_name=task_name,
                task_data=json.dumps(task_data),
                status='pending',
                scheduled_at=scheduled_at or datetime.now(),
                created_at=datetime.now()
            )
            
            db.session.add(task)
            db.session.commit()
            
            return task.id
            
        except Exception as e:
            logger.error(f"{self.agent_name} task creation error: {e}")
            return None
    
    def get_pending_tasks(self) -> List:
        """Get all pending tasks for this agent"""
        try:
            from models import AgentTask
            
            tasks = AgentTask.query.filter_by(
                agent_type=self.agent_type,
                status='pending'
            ).filter(
                AgentTask.scheduled_at <= datetime.now()
            ).all()
            
            return tasks
            
        except Exception as e:
            logger.error(f"{self.agent_name} error fetching tasks: {e}")
            return []
    
    def complete_task(self, task_id: int, result: Dict[str, Any], 
                     status: str = "completed") -> bool:
        """
        Mark a task as completed with results
        
        Args:
            task_id: Task ID to complete
            result: Task execution result
            status: Final status (completed, failed)
            
        Returns:
            Success status
        """
        try:
            from models import AgentTask, db
            
            task = AgentTask.query.get(task_id)
            if not task:
                return False
            
            task.status = status
            task.result = json.dumps(result)
            task.completed_at = datetime.now()
            
            db.session.commit()
            
            self.log_activity(
                activity_type='task_completion',
                details={'task_id': task_id, 'task_name': task.task_name, 'result': result},
                status=status
            )
            
            return True
            
        except Exception as e:
            logger.error(f"{self.agent_name} error completing task: {e}")
            return False
    
    def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent's main function. Override in subclasses.
        
        Args:
            task_data: Task parameters and configuration
            
        Returns:
            Execution result
        """
        raise NotImplementedError(f"{self.agent_name} must implement execute method")
    
    def run_scheduled_tasks(self) -> int:
        """
        Execute all pending scheduled tasks for this agent
        
        Returns:
            Number of tasks processed
        """
        tasks = self.get_pending_tasks()
        processed = 0
        
        for task in tasks:
            try:
                task_data = json.loads(task.task_data)
                result = self.execute(task_data)
                
                self.complete_task(
                    task.id,
                    result,
                    status='completed' if result.get('success') else 'failed'
                )
                
                processed += 1
                
            except Exception as e:
                logger.error(f"{self.agent_name} task execution error: {e}")
                self.complete_task(
                    task.id,
                    {'success': False, 'error': str(e)},
                    status='failed'
                )
        
        return processed
