"""
Log Reader for VPS Diagnostics
Safely reads and parses server logs for chatbot analysis
Works on both Replit and VPS deployments
"""
import os
import subprocess
import logging
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class LogReader:
    """Read and parse server logs for diagnostics"""
    
    # Define log locations for different environments
    LOG_PATHS = {
        'nginx_error': [
            '/var/log/nginx/error.log',
            '/var/log/nginx/error.log.1',
        ],
        'gunicorn': [
            '/var/log/gunicorn/gunicorn.err',
            '/var/log/gunicorn.err',
            '/var/log/gunicorn.log',
        ],
        'app': [
            '/var/www/lux/logs/app.log',
            '/var/www/lux/logs/error.log',
            './logs/app.log',
            './logs/error.log',
        ],
        'systemd': None,  # Read via journalctl
    }
    
    @staticmethod
    def read_nginx_errors(lines=50):
        """Read recent Nginx errors"""
        try:
            for log_path in LogReader.LOG_PATHS['nginx_error']:
                if os.path.exists(log_path):
                    try:
                        with open(log_path, 'r', errors='ignore') as f:
                            # Get last N lines
                            content = f.read()
                            log_lines = content.strip().split('\n')
                            recent = log_lines[-lines:] if len(log_lines) > lines else log_lines
                            return {
                                'source': log_path,
                                'logs': recent,
                                'count': len(recent)
                            }
                    except (PermissionError, IOError) as e:
                        logger.warning(f"Cannot read {log_path}: {e}")
            return {'source': 'none', 'logs': [], 'count': 0, 'note': 'Nginx error log not found'}
        except Exception as e:
            logger.error(f"Error reading nginx logs: {e}")
            return {'source': 'error', 'logs': [str(e)], 'count': 0}
    
    @staticmethod
    def read_gunicorn_logs(lines=50):
        """Read recent Gunicorn logs"""
        try:
            for log_path in LogReader.LOG_PATHS['gunicorn']:
                if os.path.exists(log_path):
                    try:
                        with open(log_path, 'r', errors='ignore') as f:
                            content = f.read()
                            log_lines = content.strip().split('\n')
                            recent = log_lines[-lines:] if len(log_lines) > lines else log_lines
                            return {
                                'source': log_path,
                                'logs': recent,
                                'count': len(recent)
                            }
                    except (PermissionError, IOError) as e:
                        logger.warning(f"Cannot read {log_path}: {e}")
            return {'source': 'none', 'logs': [], 'count': 0, 'note': 'Gunicorn log not found'}
        except Exception as e:
            logger.error(f"Error reading gunicorn logs: {e}")
            return {'source': 'error', 'logs': [str(e)], 'count': 0}
    
    @staticmethod
    def read_app_logs(lines=50):
        """Read recent application logs"""
        try:
            for log_path in LogReader.LOG_PATHS['app']:
                if os.path.exists(log_path):
                    try:
                        with open(log_path, 'r', errors='ignore') as f:
                            content = f.read()
                            log_lines = content.strip().split('\n')
                            recent = log_lines[-lines:] if len(log_lines) > lines else log_lines
                            return {
                                'source': log_path,
                                'logs': recent,
                                'count': len(recent)
                            }
                    except (PermissionError, IOError) as e:
                        logger.warning(f"Cannot read {log_path}: {e}")
            return {'source': 'none', 'logs': [], 'count': 0, 'note': 'App log not found'}
        except Exception as e:
            logger.error(f"Error reading app logs: {e}")
            return {'source': 'error', 'logs': [str(e)], 'count': 0}
    
    @staticmethod
    def read_systemd_logs(lines=50):
        """Read recent systemd journal logs for lux service"""
        try:
            cmd = f"journalctl -u lux.service -n {lines} --no-pager 2>/dev/null || echo 'Service not found'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            log_lines = result.stdout.strip().split('\n') if result.stdout else []
            
            return {
                'source': 'journalctl',
                'logs': log_lines,
                'count': len([l for l in log_lines if l.strip()])
            }
        except subprocess.TimeoutExpired:
            logger.warning("Systemd journal read timeout")
            return {'source': 'journalctl', 'logs': ['Timeout reading journal'], 'count': 0}
        except Exception as e:
            logger.warning(f"Cannot read systemd logs: {e}")
            return {'source': 'journalctl', 'logs': [f"Error: {str(e)}"], 'count': 0}
    
    @staticmethod
    def get_all_logs(lines=50):
        """Read all available logs for comprehensive diagnostics"""
        return {
            'nginx': LogReader.read_nginx_errors(lines),
            'gunicorn': LogReader.read_gunicorn_logs(lines),
            'app': LogReader.read_app_logs(lines),
            'systemd': LogReader.read_systemd_logs(lines),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def format_logs_for_ai(all_logs):
        """Format all logs into a readable string for AI analysis"""
        formatted = []
        
        for log_type, log_data in all_logs.items():
            if log_type == 'timestamp':
                continue
            
            if not log_data.get('logs'):
                continue
            
            source = log_data.get('source', 'unknown')
            count = log_data.get('count', 0)
            
            formatted.append(f"\n{'='*60}")
            formatted.append(f"{log_type.upper()} LOGS ({source})")
            formatted.append(f"Total lines: {count}")
            formatted.append('='*60)
            
            for line in log_data['logs']:
                if line.strip():
                    formatted.append(line)
        
        return '\n'.join(formatted)
    
    @staticmethod
    def analyze_logs_for_errors(all_logs):
        """Quick analysis of logs to identify common error patterns"""
        error_patterns = {
            'connection_errors': [],
            'auth_errors': [],
            'permission_errors': [],
            'timeout_errors': [],
            'resource_errors': [],
            'api_errors': []
        }
        
        all_text = LogReader.format_logs_for_ai(all_logs).lower()
        
        # Check for common error patterns
        if any(pattern in all_text for pattern in ['connection refused', 'connection reset', 'connection timeout']):
            error_patterns['connection_errors'].append('Connection issues detected')
        
        if any(pattern in all_text for pattern in ['unauthorized', 'forbidden', '401', '403', 'permission denied']):
            error_patterns['auth_errors'].append('Authentication/authorization issues detected')
        
        if any(pattern in all_text for pattern in ['permission denied', 'access denied', 'eacces']):
            error_patterns['permission_errors'].append('File permission issues detected')
        
        if any(pattern in all_text for pattern in ['timeout', 'timed out', 'deadline exceeded']):
            error_patterns['timeout_errors'].append('Timeout issues detected')
        
        if any(pattern in all_text for pattern in ['out of memory', 'no space left', 'disk full', 'oom']):
            error_patterns['resource_errors'].append('Resource exhaustion detected')
        
        if any(pattern in all_text for pattern in ['api error', 'invalid api key', 'rate limit']):
            error_patterns['api_errors'].append('API/integration issues detected')
        
        return {key: val for key, val in error_patterns.items() if val}
