#!/bin/bash

# Skiller Multi-Tenant Job Interview Platform Setup Script

set -e

echo "🚀 Setting up Skiller Multi-Tenant Job Interview Platform"
echo "========================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please update it with your configuration."
fi

# Build and start services
echo "🔧 Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Run Django migrations
echo "🗄️  Running database migrations..."
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

# Create superuser (optional)
echo "👤 Creating Django superuser..."
echo "You can skip this step by pressing Ctrl+C"
docker-compose exec backend python manage.py createsuperuser || echo "Skipped superuser creation"

# Setup Kafka topics
echo "📬 Setting up Kafka topics..."
chmod +x kafka-services/topic-manager.sh
./kafka-services/topic-manager.sh setup

# Install frontend dependencies and start
echo "📦 Installing frontend dependencies..."
docker-compose exec frontend npm install

echo "✅ Setup complete!"
echo ""
echo "🌐 Services are running at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   AI Grading Service: http://localhost:8001"
echo "   API Documentation: http://localhost:8000/api/docs/"
echo ""
echo "🛠️  To stop services: docker-compose down"
echo "🔧 To view logs: docker-compose logs -f [service_name]"
echo "🐛 To debug: docker-compose exec [service_name] bash"
