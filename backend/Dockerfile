# Dockerfile

# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full backend folder into container
COPY . .

# Set Django settings module path (very important!)
ENV DJANGO_SETTINGS_MODULE=settings

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port 8000
EXPOSE 8000

# Start Gunicorn
CMD ["gunicorn", "wsgi:application", "--bind", "0.0.0.0:8000"]
