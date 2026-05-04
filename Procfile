web: gunicorn api.main:app --workers 1 --threads 1 --timeout 120 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
