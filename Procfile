web: gunicorn wsgi:application --bind 0.0.0.0:$PORT --timeout 120 --workers 4 --log-level info --access-logfile - --error-logfile -
worker: celery -A celery_app worker --loglevel=info --concurrency=4 --max-tasks-per-child=100
flower: celery -A celery_app flower --port=$PORT --broker=$CELERY_BROKER_URL
