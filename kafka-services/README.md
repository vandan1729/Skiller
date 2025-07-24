# Kafka Services Configuration

This directory contains Kafka-related services and configurations for the Skiller platform.

## Services

### Topic Management
- **interview-submissions**: Submissions from candidates
- **grading-results**: Results from AI grading service
- **notifications**: System notifications
- **analytics-events**: Analytics and tracking events

### Producers
- Django backend produces submission events
- AI service produces grading results

### Consumers
- AI grading service consumes submissions
- Django backend consumes grading results
- Notification service consumes notification events

## Configuration

Topics are automatically created with the following settings:
- Partitions: 3
- Replication Factor: 1 (development)
- Retention: 7 days

## Usage

The Kafka services are managed through Docker Compose. Topics are created automatically when the first message is published.
