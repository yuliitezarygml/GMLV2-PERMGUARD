"""
Unified PermGuard Authorization Module
Handles all authorization logic and policy management for SwaWeb application
"""

import json
import logging
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, Optional, List
import traceback

from flask import request, jsonify, session, g

# Configure detailed logging for PermGuard
def setup_permguard_logging():
    """Setup detailed logging for PermGuard operations"""

    # Create PermGuard logger
    permguard_logger = logging.getLogger('permguard_detailed')
    permguard_logger.setLevel(logging.DEBUG)

    # Remove existing handlers to avoid duplication
    for handler in permguard_logger.handlers[:]:
        permguard_logger.removeHandler(handler)

    # Create detailed formatter
    detailed_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler for detailed logs
    file_handler = logging.FileHandler('permguard_detailed.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)

    # Console handler for detailed output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(detailed_formatter)

    # Add handlers
    permguard_logger.addHandler(file_handler)
    permguard_logger.addHandler(console_handler)

    return permguard_logger

# Setup loggers
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)
permguard_logger = setup_permguard_logging()

# PermGuard imports - handle import errors gracefully
try:
    from permguard.az_client import AZClient
    from permguard.az_config import AZConfig
    PERMGUARD_AVAILABLE = True
    permguard_logger.info("✅ PermGuard Python client imported successfully")
except ImportError as e:
    logger.warning("PermGuard not available - running in fallback mode")
    permguard_logger.error(f"❌ Failed to import PermGuard client: {e}")
    AZClient = None
    AZConfig = None
    PERMGUARD_AVAILABLE = False

class PermGuardAuth:
    """Unified PermGuard Authorization System"""

    def __init__(self, app=None):
        self.app = app
        self.client = None
        self.connected = False
        self.config = {}
        self.authorization_log = []  # In-memory log for demo purposes
        self.traffic_log = []  # Web traffic log

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize PermGuard with Flask app"""
        self.app = app

        # Load configuration
        self.config = {
            'endpoint': os.getenv('PERMGUARD_ENDPOINT', 'localhost'),
            'port': int(os.getenv('PERMGUARD_PORT', '9094')),
            'workspace_id': os.getenv('WORKSPACE_ID', '875986860059'),
            'policy_store_id': os.getenv('POLICY_STORE_ID', '4b16807f1d724a118ac52c295f9794dd'),
            'fallback_allowed': app.config.get('PERMGUARD_FALLBACK_ALLOWED', True)
        }

        # Initialize PermGuard client
        self._init_client()

        # Register teardown handler
        app.teardown_appcontext(self._teardown)

        # Register traffic monitoring middleware
        app.before_request(self._before_request)
        app.after_request(self._after_request)

    def _init_client(self):
        """Initialize PermGuard client connection"""
        try:
            permguard_logger.info("=== PERMGUARD INITIALIZATION ===")
            permguard_logger.info(f"Endpoint: {self.config['endpoint']}:{self.config['port']}")
            permguard_logger.info(f"Workspace ID: {self.config['workspace_id']}")
            permguard_logger.info(f"Policy Store ID: {self.config['policy_store_id']}")

            if not PERMGUARD_AVAILABLE or AZClient is None:
                raise Exception("PermGuard client not available")

            permguard_logger.info("Creating PermGuard endpoint...")

            # Create endpoint
            from permguard.az_client import AZEndpoint
            self.endpoint = AZEndpoint(
                endpoint=self.config['endpoint'],
                port=self.config['port']
            )

            permguard_logger.info("Testing connection to PermGuard...")

            # Test connection with direct authorization_check
            from permguard.internal.az.azreq.grpc.v1.pdp_client import authorization_check
            from permguard.az.azreq.model import AZRequest, Subject, Resource, Action

            # Create a simple test request
            test_request = AZRequest(
                subject=Subject(id="test@example.com"),
                resource=Resource(id="test::resource"),
                action=Action(id="test::action")
            )

            endpoint_url = f"{self.config['endpoint']}:{self.config['port']}"
            test_result = authorization_check(endpoint_url, test_request)
            permguard_logger.info(f"Connection test successful! Result: {test_result}")

            self.client = True  # Mark as connected

            self.connected = True
            permguard_logger.info("✅ PermGuard client initialized successfully")
            logger.info(f"PermGuard connected to {self.config['endpoint']}:{self.config['port']}")

        except Exception as e:
            self.connected = False
            permguard_logger.error(f"❌ Failed to connect to PermGuard: {e}")
            permguard_logger.debug(f"Connection error details: {traceback.format_exc()}")

            logger.warning(f"Failed to connect to PermGuard: {e}")
            if self.config['fallback_allowed']:
                permguard_logger.warning("🔄 Continuing with fallback authorization mode")
                logger.warning("Continuing with fallback authorization")
            else:
                raise

    def _teardown(self, exception):
        """Cleanup resources"""
        pass

    def _before_request(self):
        """Track request start time for traffic monitoring"""
        from flask import g
        g.request_start_time = datetime.now()

    def _after_request(self, response):
        """Log traffic data after request completion"""
        from flask import g, request

        end_time = datetime.now()
        start_time = getattr(g, 'request_start_time', end_time)
        duration = (end_time - start_time).total_seconds()

        # Skip only static files, but track admin and API requests
        if request.endpoint == 'static' or request.path.startswith('/static/'):
            return response

        current_user = self._get_current_user()

        traffic_entry = {
            'id': f"traffic_{len(self.traffic_log)}_{end_time.strftime('%Y%m%d_%H%M%S')}",
            'timestamp': end_time.isoformat(),
            'method': request.method,
            'path': request.path,
            'endpoint': request.endpoint,
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'unknown'),
            'user': current_user,
            'content_length': response.content_length or 0,
            'referrer': request.referrer,
            'args': dict(request.args) if request.args else {},
        }

        self.traffic_log.append(traffic_entry)

        # Log traffic details
        permguard_logger.debug(
            f"🌐 TRAFFIC: {request.method} {request.path} -> {response.status_code} "
            f"({round(duration * 1000, 2)}ms) user: {current_user} IP: {request.remote_addr}"
        )

        # Detailed logging for admin endpoints
        if request.path.startswith('/admin') or request.path.startswith('/api/admin'):
            permguard_logger.info(
                f"🔐 ADMIN ACCESS: {current_user} -> {request.method} {request.path} "
                f"[{response.status_code}] ({round(duration * 1000, 2)}ms)"
            )

        # Keep only last 1000 entries
        if len(self.traffic_log) > 1000:
            removed_entry = self.traffic_log.pop(0)
            permguard_logger.debug(f"🗑️ CLEANED: Removed old traffic entry {removed_entry['id']}")

        return response

    def _get_current_user(self):
        """Safely get current user from session"""
        try:
            if session and hasattr(session, 'get'):
                user_data = session.get('user', {})
                if isinstance(user_data, dict):
                    return user_data.get('email', 'anonymous')
            return 'anonymous'
        except Exception:
            return 'anonymous'

    def add_demo_traffic_data(self):
        """Add demo traffic data for testing purposes"""
        from datetime import datetime, timedelta
        import random

        if len(self.traffic_log) > 0:
            return  # Already has data

        demo_users = ['yuliitezary@gmail.com', 'admin@swaweb.com', 'test@example.com', 'anonymous']
        demo_endpoints = [
            ('GET', '/', 'index', 200),
            ('GET', '/gamelist', 'gamelist', 200),
            ('GET', '/admin', 'admin_dashboard', 200),
            ('GET', '/admin/traffic', 'admin_traffic', 200),
            ('GET', '/admin/users', 'admin_users', 200),
            ('GET', '/api/admin/traffic/stats', 'api_admin_traffic_stats', 200),
            ('GET', '/api/admin/traffic/logs', 'api_admin_traffic_logs', 200),
            ('POST', '/login', 'login', 200),
            ('GET', '/profile', 'profile', 200),
            ('GET', '/premium', 'premium', 200),
            ('GET', '/nonexistent', 'nonexistent', 404),
            ('GET', '/api/games/free', 'api_games_free', 500),
        ]

        base_time = datetime.now() - timedelta(hours=2)

        for i in range(25):
            method, path, endpoint, status = random.choice(demo_endpoints)
            user = random.choice(demo_users)

            # Simulate different response times
            if status == 500:
                duration = random.randint(800, 2000)  # Slow for errors
            elif path.startswith('/api'):
                duration = random.randint(50, 300)    # API calls
            else:
                duration = random.randint(100, 800)   # Regular pages

            timestamp = base_time + timedelta(minutes=random.randint(0, 120))

            traffic_entry = {
                'id': f"demo_traffic_{i}_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                'timestamp': timestamp.isoformat(),
                'method': method,
                'path': path,
                'endpoint': endpoint,
                'status_code': status,
                'duration_ms': duration,
                'ip_address': f'192.168.1.{random.randint(1, 254)}',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'user': user,
                'content_length': random.randint(1024, 50000),
                'referrer': None if random.random() > 0.3 else 'https://google.com',
                'args': {},
            }

            self.traffic_log.append(traffic_entry)

        logger.info(f"Added {len(self.traffic_log)} demo traffic entries")

    def check_permission(self, user: str, action: str, resource: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Check if user has permission to perform action on resource

        Args:
            user: User identifier (e.g., email)
            action: Action to check (e.g., 'game::purchase')
            resource: Resource identifier (e.g., 'game::game-001')
            context: Additional context for authorization

        Returns:
            Dict with 'allowed' boolean and additional info
        """
        start_time = datetime.now()
        context = context or {}

        # Add default context
        context.update({
            'timestamp': start_time.isoformat(),
            'ip_address': request.remote_addr if request else 'unknown',
            'user_agent': request.headers.get('User-Agent', 'unknown') if request else 'unknown'
        })

        # Detailed authorization logging
        permguard_logger.info(f"🛡️ AUTH REQUEST: user={user} action={action} resource={resource}")
        permguard_logger.debug(f"📋 AUTH CONTEXT: {context}")

        try:
            if self.connected and hasattr(self, 'endpoint'):
                # Use PermGuard for authorization
                permguard_logger.debug("🔗 Using PermGuard client for authorization")
                result = self._check_with_permguard(user, action, resource, context)
            else:
                # Fallback authorization
                permguard_logger.debug("⚠️ Using fallback authorization (PermGuard not connected)")
                result = self._fallback_authorization(user, action, resource, context)

        except Exception as e:
            permguard_logger.error(f"❌ Authorization error: {e}")
            permguard_logger.debug(f"🔍 Error details: {traceback.format_exc()}")
            logger.error(f"Authorization error: {e}")
            result = {
                'allowed': False,
                'reason': f'Authorization system error: {str(e)}',
                'fallback': True
            }

        # Calculate duration and log
        duration = (datetime.now() - start_time).total_seconds()

        # Log result
        status_emoji = "✅" if result['allowed'] else "❌"
        permguard_logger.info(
            f"{status_emoji} AUTH RESULT: {user} -> {action} on {resource} = "
            f"{'ALLOWED' if result['allowed'] else 'DENIED'} ({duration*1000:.1f}ms)"
        )

        if not result['allowed']:
            permguard_logger.warning(f"🚫 ACCESS DENIED: {result.get('reason', 'No reason provided')}")

        self._log_authorization(user, action, resource, context, result, duration * 1000)

        return result

    def _check_with_permguard(self, user: str, action: str, resource: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check authorization using PermGuard"""
        try:
            permguard_logger.debug(f"Making authorization request to PermGuard...")
            permguard_logger.debug(f"Principal: {user}, Action: {action}, Resource: {resource}")

            # Import required classes
            from permguard.internal.az.azreq.grpc.v1.pdp_client import authorization_check
            from permguard.az.azreq.model import AZRequest, Subject, Resource as AZResource, Action as AZAction

            # Create authorization request with context
            az_request = AZRequest(
                subject=Subject(id=user),
                resource=AZResource(id=resource),
                action=AZAction(id=action),
                context={
                    'workspace_id': self.config['workspace_id'],
                    'policy_store_id': self.config['policy_store_id']
                }
            )

            # Make authorization request
            endpoint_url = f"{self.config['endpoint']}:{self.config['port']}"
            response = authorization_check(endpoint_url, az_request)

            permguard_logger.debug(f"PermGuard response: {response}")

            # Parse AZResponse
            allowed = getattr(response, 'decision', False)
            request_id = getattr(response, 'request_id', '')

            return {
                'allowed': allowed,
                'reason': f'Policy evaluation completed (RequestID: {request_id})',
                'request_id': request_id,
                'response': str(response),
                'fallback': False
            }

        except Exception as e:
            permguard_logger.error(f"❌ PermGuard error: {e}")
            permguard_logger.debug(f"Error details: {traceback.format_exc()}")
            logger.error(f"PermGuard error: {e}")
            return {
                'allowed': False,
                'reason': f'PermGuard error: {str(e)}',
                'fallback': False
            }

    def _fallback_authorization(self, user: str, action: str, resource: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback authorization logic when PermGuard is unavailable"""

        # Basic fallback rules
        allowed = False
        reason = "Fallback authorization"

        # Admin users have full access
        if 'admin' in user.lower():
            allowed = True
            reason = "Admin user access"

        # Game actions
        elif action.startswith('game::'):
            if action == 'game::view':
                allowed = True
                reason = "Game viewing allowed for all users"
            elif action == 'game::purchase':
                # Check age restrictions
                game_rating = context.get('game_rating', 'E')
                user_age = context.get('age', 18)

                if game_rating in ['M', 'AO'] and user_age < 17:
                    allowed = False
                    reason = "Age restriction: User too young for mature content"
                elif context.get('account_balance', 0) < context.get('game_price', 0):
                    allowed = False
                    reason = "Insufficient account balance"
                else:
                    allowed = True
                    reason = "Purchase authorized"
            elif action in ['game::download', 'game::wishlist']:
                allowed = True
                reason = f"Action {action} allowed"

        # Profile actions
        elif action.startswith('profile::'):
            profile_user = resource.split('::')[-1] if '::' in resource else resource
            if user == profile_user or 'admin' in user.lower():
                allowed = True
                reason = "Profile access authorized"
            else:
                allowed = False
                reason = "Can only access own profile"

        # Default deny
        else:
            allowed = False
            reason = f"No policy found for action {action}"

        return {
            'allowed': allowed,
            'reason': reason,
            'fallback': True
        }

    def _log_authorization(self, user: str, action: str, resource: str, context: Dict[str, Any], result: Dict[str, Any], duration: float):
        """Log authorization attempt"""
        log_entry = {
            'id': f"auth_{len(self.authorization_log)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'user': user,
            'action': action,
            'resource': resource,
            'context': context,
            'result': 'ALLOW' if result['allowed'] else 'DENY',
            'reason': result.get('reason', ''),
            'duration': round(duration, 2),
            'fallback': result.get('fallback', False),
            'policies': result.get('policies', [])
        }

        # Keep only last 1000 entries
        self.authorization_log.append(log_entry)
        if len(self.authorization_log) > 1000:
            self.authorization_log.pop(0)

        logger.info(f"Authorization: {user} {action} {resource} -> {result['allowed']}")

    def get_authorization_logs(self, limit: int = 100, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get authorization logs with optional filtering"""
        logs = self.authorization_log.copy()
        filters = filters or {}

        # Apply filters
        if filters.get('user'):
            logs = [log for log in logs if filters['user'].lower() in log['user'].lower()]

        if filters.get('action'):
            logs = [log for log in logs if filters['action'].lower() in log['action'].lower()]

        if filters.get('result'):
            logs = [log for log in logs if log['result'] == filters['result']]

        # Sort by timestamp (newest first) and limit
        logs = sorted(logs, key=lambda x: x['timestamp'], reverse=True)
        return logs[:limit]

    def get_authorization_stats(self) -> Dict[str, Any]:
        """Get authorization statistics"""
        if not self.authorization_log:
            return {'error': 'No authorization data available'}

        logs = self.authorization_log
        total_requests = len(logs)
        allowed_requests = len([log for log in logs if log['result'] == 'ALLOW'])
        denied_requests = total_requests - allowed_requests
        success_rate = (allowed_requests / total_requests * 100) if total_requests > 0 else 0

        # Top actions
        action_counts = {}
        for log in logs:
            action_counts[log['action']] = action_counts.get(log['action'], 0) + 1

        top_actions = [
            {'action': action, 'count': count}
            for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]

        # Top users
        user_stats = {}
        for log in logs:
            user = log['user']
            if user not in user_stats:
                user_stats[user] = {'requests': 0, 'allowed': 0}
            user_stats[user]['requests'] += 1
            if log['result'] == 'ALLOW':
                user_stats[user]['allowed'] += 1

        top_users = []
        for user, stats in user_stats.items():
            success_rate = (stats['allowed'] / stats['requests'] * 100) if stats['requests'] > 0 else 0
            top_users.append({
                'user': user,
                'requests': stats['requests'],
                'success_rate': success_rate
            })

        top_users = sorted(top_users, key=lambda x: x['requests'], reverse=True)[:10]

        return {
            'total_requests': total_requests,
            'allowed_requests': allowed_requests,
            'denied_requests': denied_requests,
            'success_rate': success_rate,
            'top_actions': top_actions,
            'top_users': top_users
        }

    def get_traffic_logs(self, limit: int = 100, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get traffic logs with optional filtering"""
        logs = self.traffic_log.copy()

        if filters:
            if filters.get('user'):
                logs = [log for log in logs if filters['user'].lower() in log['user'].lower()]
            if filters.get('method'):
                logs = [log for log in logs if log['method'] == filters['method']]
            if filters.get('status_code'):
                logs = [log for log in logs if log['status_code'] == int(filters['status_code'])]
            if filters.get('min_duration'):
                logs = [log for log in logs if log['duration_ms'] >= float(filters['min_duration'])]

        logs = sorted(logs, key=lambda x: x['timestamp'], reverse=True)
        return logs[:limit]

    def get_traffic_stats(self) -> Dict[str, Any]:
        """Get comprehensive traffic statistics"""
        if not self.traffic_log:
            return {'error': 'No traffic data available'}

        logs = self.traffic_log
        total_requests = len(logs)

        # Status code analysis
        status_counts = {}
        for log in logs:
            status = log['status_code']
            status_counts[status] = status_counts.get(status, 0) + 1

        # Method analysis
        method_counts = {}
        for log in logs:
            method = log['method']
            method_counts[method] = method_counts.get(method, 0) + 1

        # Performance analysis
        durations = [log['duration_ms'] for log in logs]
        avg_duration = sum(durations) / len(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        min_duration = min(durations) if durations else 0

        # Top endpoints
        endpoint_counts = {}
        endpoint_durations = {}
        for log in logs:
            endpoint = log['endpoint'] or 'unknown'
            endpoint_counts[endpoint] = endpoint_counts.get(endpoint, 0) + 1
            if endpoint not in endpoint_durations:
                endpoint_durations[endpoint] = []
            endpoint_durations[endpoint].append(log['duration_ms'])

        top_endpoints = []
        for endpoint, count in sorted(endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            avg_duration = sum(endpoint_durations[endpoint]) / len(endpoint_durations[endpoint])
            top_endpoints.append({
                'endpoint': endpoint,
                'count': count,
                'avg_duration': round(avg_duration, 2)
            })

        # User analysis
        user_counts = {}
        for log in logs:
            user = log['user']
            user_counts[user] = user_counts.get(user, 0) + 1

        top_users = [
            {'user': user, 'requests': count}
            for user, count in sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]

        # Error analysis
        error_requests = len([log for log in logs if log['status_code'] >= 400])
        error_rate = (error_requests / total_requests * 100) if total_requests > 0 else 0

        return {
            'total_requests': total_requests,
            'error_requests': error_requests,
            'error_rate': round(error_rate, 2),
            'avg_duration_ms': round(avg_duration, 2),
            'max_duration_ms': max_duration,
            'min_duration_ms': min_duration,
            'status_codes': status_counts,
            'methods': method_counts,
            'top_endpoints': top_endpoints,
            'top_users': top_users
        }

    def get_status(self) -> Dict[str, Any]:
        """Get PermGuard connection status"""
        return {
            'connected': self.connected,
            'endpoint': f"{self.config['endpoint']}:{self.config['port']}",
            'workspace_id': self.config['workspace_id'],
            'policy_store_id': self.config['policy_store_id'],
            'fallback_enabled': self.config['fallback_allowed']
        }

    def test_authorization(self, user: str, action: str, resource: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Test authorization for debugging purposes"""
        result = self.check_permission(user, action, resource, context)

        return {
            'success': True,
            'allowed': result['allowed'],
            'reason': result.get('reason', ''),
            'policies': result.get('policies', []),
            'fallback': result.get('fallback', False),
            'request': {
                'user': user,
                'action': action,
                'resource': resource,
                'context': context or {}
            }
        }

    def require_permission(self, action: str, resource_func=None):
        """
        Decorator to require permission for a route

        Args:
            action: The action to check
            resource_func: Function to determine resource (receives request args)
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Get user from session
                user = session.get('user_email')
                if not user:
                    return jsonify({'error': 'Authentication required'}), 401

                # Determine resource
                if resource_func:
                    resource = resource_func(*args, **kwargs)
                else:
                    resource = f"route::{request.endpoint}"

                # Get context
                context = {
                    'route': request.endpoint,
                    'method': request.method,
                    'args': dict(request.args),
                    'form': dict(request.form) if request.form else {},
                }

                # Add user context if available in session
                if 'user_age' in session:
                    context['age'] = session['user_age']
                if 'account_balance' in session:
                    context['account_balance'] = session['account_balance']

                # Check permission
                result = self.check_permission(user, action, resource, context)

                if not result['allowed']:
                    return jsonify({
                        'error': 'Permission denied',
                        'reason': result.get('reason', 'Access not authorized')
                    }), 403

                # Store authorization result for use in route
                g.auth_result = result

                return f(*args, **kwargs)

            return decorated_function
        return decorator

# Global instance
permguard_auth = PermGuardAuth()

# Convenience functions
def check_permission(user: str, action: str, resource: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Check permission using global instance"""
    return permguard_auth.check_permission(user, action, resource, context)

def require_permission(action: str, resource_func=None):
    """Require permission decorator using global instance"""
    return permguard_auth.require_permission(action, resource_func)

def get_auth_stats():
    """Get authorization statistics"""
    return permguard_auth.get_authorization_stats()

def get_auth_logs(limit: int = 100, filters: Dict[str, Any] = None):
    """Get authorization logs"""
    return permguard_auth.get_authorization_logs(limit, filters)

def get_permguard_status():
    """Get PermGuard status"""
    return permguard_auth.get_status()

def get_traffic_stats():
    """Get traffic statistics"""
    return permguard_auth.get_traffic_stats()

def get_traffic_logs(limit: int = 100, filters: Dict[str, Any] = None):
    """Get traffic logs"""
    return permguard_auth.get_traffic_logs(limit, filters)