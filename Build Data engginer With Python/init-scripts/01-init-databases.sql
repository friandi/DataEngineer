-- Create additional databases for NiFi and Elasticsearch
CREATE DATABASE nifi;
CREATE DATABASE elasticsearch;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE nifi TO airflow;
GRANT ALL PRIVILEGES ON DATABASE elasticsearch TO airflow;
