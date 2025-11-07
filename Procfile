web: sh -c 'gunicorn wsgi:application --bind 0.0.0.0:${PORT:-8080} --timeout ${GUNICORN_TIMEOUT:-120} --workers ${WEB_CONCURRENCY:-2} --log-level info --access-logfile - --error-logfile -'
worker: sh -c 'celery -A celery_app worker --loglevel=${CELERY_LOGLEVEL:-info} --concurrency ${CELERY_CONCURRENCY:-2} --max-tasks-per-child=100'
flower: sh -c 'celery -A celery_app flower --port=${PORT:-5555} --broker=${CELERY_BROKER_URL}'
