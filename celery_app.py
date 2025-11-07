"""
Celery Application for Flow Forecaster
Handles background task processing for long-running simulations
"""
import os
from celery import Celery

# Celery configuration from environment
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Create Celery app
celery_app = Celery(
    'forecaster',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['tasks.simulation_tasks']  # Auto-discover tasks
)

# Celery configuration
celery_app.conf.update(
    # Serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',

    # Timezone
    timezone='UTC',
    enable_utc=True,

    # Task tracking
    task_track_started=True,
    task_send_sent_event=True,

    # Task time limits
    task_time_limit=600,  # 10 minutes hard limit
    task_soft_time_limit=540,  # 9 minutes soft limit (warning)

    # Worker configuration
    worker_prefetch_multiplier=1,  # Process one task at a time per worker
    worker_max_tasks_per_child=100,  # Recycle worker after 100 tasks (prevent memory leaks)
    worker_disable_rate_limits=False,

    # Result backend
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        'master_name': 'mymaster',
        'visibility_timeout': 3600,
    },

    # Broker settings
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,

    # Task routing (future enhancement)
    task_routes={
        'tasks.simulation_tasks.run_monte_carlo_async': {'queue': 'simulations'},
        'tasks.simulation_tasks.run_ml_deadline_async': {'queue': 'ml_tasks'},
        'tasks.simulation_tasks.run_backtest_async': {'queue': 'backtests'},
    },

    # Task annotations for monitoring
    task_annotations={
        '*': {
            'rate_limit': '100/m',  # Global rate limit: 100 tasks per minute
        },
        'tasks.simulation_tasks.run_backtest_async': {
            'rate_limit': '10/m',  # Backtests are expensive: 10 per minute
            'time_limit': 600,
        }
    },
)

# Celery events for monitoring
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery configuration"""
    print(f'Request: {self.request!r}')
    return {
        'broker': CELERY_BROKER_URL,
        'backend': CELERY_RESULT_BACKEND,
        'task_id': self.request.id
    }


if __name__ == '__main__':
    celery_app.start()
