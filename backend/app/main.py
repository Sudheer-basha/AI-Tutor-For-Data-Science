from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, AsyncSessionLocal
from app.models import Base
from app.seed import seed_data
from app.routers import auth, lessons, assignments, quizzes, tutor, progress, certificates

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    print("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    print("Database tables initialized. Seeding curriculum...")
    async with AsyncSessionLocal() as session:
        await seed_data(session)
        
    yield
    # Shutdown actions
    await engine.dispose()

app = FastAPI(
    title="AI Data Science Tutor API",
    description="Backend API powering the Personalized 3-Month Data Science Learning Path.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS Middleware
# Allows request from Vite dev server and production origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, lock this down to the frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router, prefix="/api")
app.include_router(lessons.router, prefix="/api")
app.include_router(assignments.router, prefix="/api")
app.include_router(quizzes.router, prefix="/api")
app.include_router(tutor.router, prefix="/api")
app.include_router(progress.router, prefix="/api")
app.include_router(certificates.router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the AI Data Science Tutor API!",
        "docs_url": "/docs"
    }
