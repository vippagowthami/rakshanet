FROM python:3.10-slim
WORKDIR /app/RakshaNet
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY . /app
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt
ENV PORT=8000
EXPOSE 8000
# Collect static files and run via gunicorn
RUN python manage.py collectstatic --noinput || true
CMD ["sh", "-c", "python manage.py migrate && gunicorn django_start.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3"]
