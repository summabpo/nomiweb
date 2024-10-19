# Use the official Python image from the Docker Hub
FROM amd64/python:3.11.5

# Set environment variables to prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    locales \
    python3-dev \
    && sed -i '/es_ES.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen es_ES.UTF-8 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set locale environment variables
ENV LANG=es_ES.UTF-8 
ENV LANGUAGE=es_ES:es
ENV LC_ALL=es_ES.UTF-8

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn
RUN pip install gunicorn

# Copy the rest of the application code
COPY . /app/

# Expose port 8000
EXPOSE 8000

# Copy el script de entrada
COPY ./entrypoint.sh  /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh



# Establecer el script de entrada como el punto de entrada del contenedor
ENTRYPOINT ["/app/entrypoint.sh"]