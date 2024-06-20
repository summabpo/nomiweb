# Use the official Python image from the Docker Hub
FROM python:3.9

# Set environment variables to prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install locales package and generate es_ES.UTF-8 locale
RUN apt-get update && apt-get install -y locales && \
    sed -i '/es_ES.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen es_ES.UTF-8

# Set locale environment variables
ENV LANG es_ES.UTF-8
ENV LANGUAGE es_ES:es
ENV LC_ALL es_ES.UTF-8

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Install Gunicorn for serving Django application


# Expose port 8000
EXPOSE 8000

# Command to run the application using Gunicorn server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
