from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from datetime import datetime
from agent import get_agent
from cache import cache
from logger import logger

app = FastAPI(
    title="AI Research API",
    description="Autonomous research agent with caching",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    topic: str
    background: bool = False

class ResearchResponse(BaseModel):
    success: bool
    report: Optional[dict] = None
    topic: str
    timestamp: str
    from_cache: bool = False
    error: Optional[str] = None

@app.get("/")
async def root():
    return {"status": "healthy", "service": "AI Research API"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_enabled": cache.enabled
    }

@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """Research a topic and return a report."""
    logger.info(f"API request: {request.topic[:50]}...")
    
    # Check cache
    cached = cache.get(request.topic)
    if cached:
        return ResearchResponse(
            success=True,
            report=cached.get('report'),
            topic=request.topic,
            timestamp=datetime.now().isoformat(),
            from_cache=True
        )
    
    try:
        agent = get_agent()
        result = agent.research(request.topic)
        
        if result.get('success'):
            # Cache the result
            cache.set(request.topic, result)
            
            return ResearchResponse(
                success=True,
                report=result.get('report'),
                topic=request.topic,
                timestamp=datetime.now().isoformat(),
                from_cache=False
            )
        else:
            return ResearchResponse(
                success=False,
                topic=request.topic,
                timestamp=datetime.now().isoformat(),
                error=result.get('error')
            )
    
    except Exception as e:
        logger.error(f"API error: {e}")
        return ResearchResponse(
            success=False,
            topic=request.topic,
            timestamp=datetime.now().isoformat(),
            error=str(e)
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)