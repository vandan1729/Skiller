#!/bin/bash

# Kafka Topic Management Script

KAFKA_CONTAINER="skiller-kafka-1"
BOOTSTRAP_SERVERS="localhost:9092"

# Function to create topic
create_topic() {
    local topic_name=$1
    local partitions=${2:-3}
    local replication_factor=${3:-1}
    
    echo "Creating topic: $topic_name"
    docker exec $KAFKA_CONTAINER kafka-topics --create \
        --bootstrap-server $BOOTSTRAP_SERVERS \
        --topic $topic_name \
        --partitions $partitions \
        --replication-factor $replication_factor \
        --if-not-exists
}

# Function to list topics
list_topics() {
    echo "Listing all topics:"
    docker exec $KAFKA_CONTAINER kafka-topics --list \
        --bootstrap-server $BOOTSTRAP_SERVERS
}

# Function to describe topic
describe_topic() {
    local topic_name=$1
    echo "Describing topic: $topic_name"
    docker exec $KAFKA_CONTAINER kafka-topics --describe \
        --bootstrap-server $BOOTSTRAP_SERVERS \
        --topic $topic_name
}

# Function to delete topic
delete_topic() {
    local topic_name=$1
    echo "Deleting topic: $topic_name"
    docker exec $KAFKA_CONTAINER kafka-topics --delete \
        --bootstrap-server $BOOTSTRAP_SERVERS \
        --topic $topic_name
}

# Create required topics
create_required_topics() {
    echo "Creating required topics for Skiller platform..."
    
    create_topic "interview-submissions" 3 1
    create_topic "grading-results" 3 1
    create_topic "notifications" 2 1
    create_topic "analytics-events" 5 1
    create_topic "candidate-events" 2 1
    create_topic "system-logs" 1 1
    
    echo "All topics created successfully!"
}

# Main script logic
case "$1" in
    "create")
        if [ -z "$2" ]; then
            echo "Usage: $0 create <topic_name> [partitions] [replication_factor]"
            exit 1
        fi
        create_topic "$2" "$3" "$4"
        ;;
    "list")
        list_topics
        ;;
    "describe")
        if [ -z "$2" ]; then
            echo "Usage: $0 describe <topic_name>"
            exit 1
        fi
        describe_topic "$2"
        ;;
    "delete")
        if [ -z "$2" ]; then
            echo "Usage: $0 delete <topic_name>"
            exit 1
        fi
        delete_topic "$2"
        ;;
    "setup")
        create_required_topics
        ;;
    *)
        echo "Usage: $0 {create|list|describe|delete|setup}"
        echo ""
        echo "Commands:"
        echo "  create <topic> [partitions] [replication]  - Create a new topic"
        echo "  list                                      - List all topics"
        echo "  describe <topic>                          - Describe a topic"
        echo "  delete <topic>                            - Delete a topic"
        echo "  setup                                     - Create all required topics"
        exit 1
        ;;
esac
