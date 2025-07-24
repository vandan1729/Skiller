# Development Guide

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Git
- VS Code (recommended)

### Quick Setup
```bash
# Clone the repository
git clone <repository-url>
cd skiller

# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

## Architecture Overview

### Backend (Django)
- **Multi-tenant architecture** with tenant isolation
- **JWT authentication** with role-based access
- **REST API** with DRF and automatic documentation
- **Kafka integration** for async processing
- **PostgreSQL** for data persistence
- **Redis** for caching and sessions

### Frontend (React)
- **TypeScript** for type safety
- **Material-UI** for components
- **Redux Toolkit** for state management
- **React Query** for API management
- **Monaco Editor** for code editing

### AI Grading Service (FastAPI)
- **FastAPI** for high-performance API
- **OpenAI integration** for AI-powered grading
- **Multiple solution analysis** engine
- **Kafka consumer** for processing submissions
- **Code execution** and validation

### Message Queue (Kafka)
- **Async processing** of submissions
- **Real-time notifications**
- **Event-driven architecture**
- **Scalable message handling**

## Development Workflow

### 1. Backend Development
```bash
# Access Django shell
docker-compose exec backend python manage.py shell

# Run migrations
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

# Create app
docker-compose exec backend python manage.py startapp newapp

# Run tests
docker-compose exec backend python manage.py test
```

### 2. Frontend Development
```bash
# Install new package
docker-compose exec frontend npm install package-name

# Run tests
docker-compose exec frontend npm test

# Build for production
docker-compose exec frontend npm run build
```

### 3. AI Service Development
```bash
# Access AI service
docker-compose exec ai-service bash

# Install new Python package
docker-compose exec ai-service pip install package-name

# View logs
docker-compose logs -f ai-service
```

## Key Features Implementation

### 1. Multi-Tenancy
- Tenant isolation at database level
- Subdomain-based tenant resolution
- Tenant-specific configurations
- Role-based access control within tenants

### 2. Question Management
- Multiple question types (coding, MCQ, text, system design)
- Question sets and categories
- Version control for questions
- Analytics and usage tracking

### 3. Interview Process
- Unique invitation links for candidates
- Time-limited sessions
- Auto-save functionality
- Real-time monitoring (optional)

### 4. AI-Powered Grading
- Automated code evaluation
- Natural language processing for text answers
- Multiple solution strategy analysis
- Plagiarism detection
- Confidence scoring

### 5. Multiple Solution Strategies
- Algorithm complexity analysis
- Code pattern recognition
- Alternative approach suggestions
- Performance comparison
- Best practices recommendations

## Database Schema

### Core Models
- **Tenant**: Company/organization
- **TenantUser**: Users within a tenant
- **Question**: Interview questions
- **Interview**: Interview sessions
- **Submission**: Candidate responses
- **GradingResult**: AI evaluation results

### Multi-Tenancy Implementation
- Foreign key to Tenant in all relevant models
- Middleware for tenant context
- Database-level isolation
- Shared public resources (optional)

## API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration
- `POST /api/auth/refresh/` - Token refresh
- `GET /api/auth/profile/` - User profile

### Tenants
- `GET /api/tenants/` - List tenants
- `GET /api/tenants/{id}/stats/` - Tenant statistics
- `PUT /api/tenants/{id}/settings/` - Update settings

### Questions
- `GET /api/questions/` - List questions
- `POST /api/questions/` - Create question
- `GET /api/questions/{id}/` - Get question details
- `PUT /api/questions/{id}/` - Update question

### Interviews
- `GET /api/interviews/` - List interviews
- `POST /api/interviews/` - Create interview
- `GET /api/interviews/{id}/start/` - Start interview session

## Environment Variables

### Required
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection
- `KAFKA_BOOTSTRAP_SERVERS` - Kafka brokers
- `SECRET_KEY` - Django secret key
- `JWT_SECRET` - JWT signing key

### AI Service
- `OPENAI_API_KEY` - OpenAI API key
- `AI_SERVICE_URL` - AI service endpoint

### Email (Optional)
- `EMAIL_HOST` - SMTP server
- `EMAIL_HOST_USER` - Email username
- `EMAIL_HOST_PASSWORD` - Email password

## Testing

### Backend Tests
```bash
# Run all tests
docker-compose exec backend python manage.py test

# Run specific app tests
docker-compose exec backend python manage.py test tenants

# Run with coverage
docker-compose exec backend coverage run --source='.' manage.py test
docker-compose exec backend coverage report
```

### Frontend Tests
```bash
# Run tests
docker-compose exec frontend npm test

# Run tests with coverage
docker-compose exec frontend npm test -- --coverage
```

## Deployment

### Production Checklist
- [ ] Update environment variables
- [ ] Configure proper database
- [ ] Set up Redis cluster
- [ ] Configure Kafka cluster
- [ ] Set up load balancer
- [ ] Configure SSL certificates
- [ ] Set up monitoring
- [ ] Configure backups

### Docker Production
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

## Monitoring & Debugging

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f ai-service
```

### Database Access
```bash
# PostgreSQL shell
docker-compose exec postgres psql -U skiller_user -d skiller_db
```

### Redis Access
```bash
# Redis CLI
docker-compose exec redis redis-cli
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Run the test suite
5. Submit a pull request

## Support

For issues and questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with details
4. Join our Discord community
