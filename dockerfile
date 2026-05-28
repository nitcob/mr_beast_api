# Define Airflow version to use - allows easy version management
ARG AIRFLOW_VERSION=2.9.2
# Define Python version - ensures consistency across environments
ARG PYTHON_VERSION=3.10

# Use official Apache Airflow image as base
# This provides a pre-configured Airflow environment with all dependencies
FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}

# Set Airflow home directory - standard location for Airflow files
ENV AIRFLOW_HOME=/opt/airflow

# Copy requirements file first for better Docker layer caching
# Docker will only rebuild this layer if requirements.txt changes
COPY requirements.txt /

# Install additional Python packages
# --no-cache-dir prevents pip from caching, reducing image size
# -r installs from requirements file
# /requirements.txt is the path we copied the file to
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt

