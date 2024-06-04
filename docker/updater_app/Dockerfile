# Use Python base image
FROM python:3.9

# Set working directory in the container
WORKDIR /app

# Install Git
RUN apt-get update && apt-get install -y git

# Copy update script
COPY update.sh /app/update.sh

# Make the script executable
RUN chmod +x /app/update.sh

# Run update script
CMD ["/bin/bash", "/app/update.sh"]
