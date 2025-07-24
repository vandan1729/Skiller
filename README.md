# Skiller - Multi-Tenant Job Interview Platform

A comprehensive platform for companies to conduct job interviews with AI-powered evaluation and multiple solution strategies.

## Features

- **Multi-Tenant Architecture**: Separate workspaces for different companies/recruiters
- **Custom Question Sets**: Companies can create and manage their own interview questions
- **Candidate Invitations**: Unique links for candidate access
- **AI-Powered Grading**: Automated evaluation using Python microservices
- **Async Processing**: Kafka-based job submission and grading pipeline
- **Multiple Solution Strategies**: Support for various problem-solving approaches

## Tech Stack

- **Backend**: Django REST Framework
- **Frontend**: React.js with TypeScript
- **Database**: PostgreSQL
- **Message Queue**: Apache Kafka
- **AI Service**: Python FastAPI microservice
- **Containerization**: Docker & Docker Compose
- **Authentication**: JWT with tenant isolation

## Project Structure

```
skiller/
├── backend/                 # Django backend
├── frontend/               # React frontend
├── ai-grading-service/     # Python microservice for AI evaluation
├── kafka-services/         # Kafka configuration and services
├── docker-compose.yml      # Container orchestration
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Run `docker-compose up --build`
4. Access the platform at `http://localhost:3000`

## Development

See individual service README files for detailed development instructions.
