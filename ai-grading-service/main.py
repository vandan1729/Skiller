from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import asyncio
from datetime import datetime

from .services.grading_engine import GradingEngine
from .services.kafka_consumer import KafkaConsumerService
from .services.multiple_solutions import MultipleSolutionEngine
from .models.grading_models import (
    SubmissionData, GradingResult, CodeSubmission,
    TextSubmission, MultipleChoiceSubmission
)

app = FastAPI(
    title="Skiller AI Grading Service",
    description="AI-powered grading engine for job interview assessments",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
grading_engine = GradingEngine()
multiple_solution_engine = MultipleSolutionEngine()
kafka_consumer = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global kafka_consumer
    
    # Initialize Kafka consumer
    kafka_consumer = KafkaConsumerService(
        topic="interview-submissions",
        group_id="ai-grading-service"
    )
    
    # Start background Kafka consumer
    asyncio.create_task(kafka_consumer.start_consuming())
    
    # Initialize AI models
    await grading_engine.initialize()
    await multiple_solution_engine.initialize()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if kafka_consumer:
        await kafka_consumer.stop()


@app.get("/")
async def root():
    return {
        "message": "Skiller AI Grading Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "grading_engine": grading_engine.is_ready(),
            "multiple_solution_engine": multiple_solution_engine.is_ready(),
            "kafka_consumer": kafka_consumer.is_running() if kafka_consumer else False
        }
    }


@app.post("/grade/code", response_model=GradingResult)
async def grade_code_submission(submission: CodeSubmission):
    """Grade a code submission"""
    try:
        result = await grading_engine.grade_code(submission)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/grade/text", response_model=GradingResult)
async def grade_text_submission(submission: TextSubmission):
    """Grade a text-based submission"""
    try:
        result = await grading_engine.grade_text(submission)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/grade/multiple-choice", response_model=GradingResult)
async def grade_multiple_choice(submission: MultipleChoiceSubmission):
    """Grade a multiple choice submission"""
    try:
        result = await grading_engine.grade_multiple_choice(submission)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/solutions")
async def analyze_multiple_solutions(
    code: str,
    problem_description: str,
    language: str = "python"
):
    """Analyze multiple solution strategies for a coding problem"""
    try:
        analysis = await multiple_solution_engine.analyze_solutions(
            code, problem_description, language
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare/solutions")
async def compare_solutions(
    solution1: str,
    solution2: str,
    problem_description: str,
    language: str = "python"
):
    """Compare two different solutions to the same problem"""
    try:
        comparison = await multiple_solution_engine.compare_solutions(
            solution1, solution2, problem_description, language
        )
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/grade/batch")
async def grade_batch_submissions(
    submissions: List[SubmissionData],
    background_tasks: BackgroundTasks
):
    """Grade multiple submissions in batch"""
    try:
        # Add batch grading task to background
        background_tasks.add_task(
            grading_engine.grade_batch,
            submissions
        )
        
        return {
            "message": f"Batch grading started for {len(submissions)} submissions",
            "batch_id": f"batch_{datetime.utcnow().timestamp()}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models/status")
async def get_model_status():
    """Get status of all AI models"""
    return {
        "grading_models": await grading_engine.get_model_status(),
        "solution_models": await multiple_solution_engine.get_model_status()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
