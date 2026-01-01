from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from app.scheduler.jobs import run_scheduled_row_count_checks
from app.dashboard.routes import router as dashboard_router

from app.database import engine, Base
from app.models import Company, User
from app.auth.routes import router as auth_router
from app.datasource.routes import router as datasource_router
from app.tables.routes import router as table_router
from app.quality.routes import router as quality_router


app = FastAPI()
scheduler = BackgroundScheduler()

@app.on_event("startup")
def start_scheduler():
    print("🚀 Scheduler starting...")
    
    scheduler.add_job(
        run_scheduled_row_count_checks,
        trigger="interval",
        minutes=1   # change to 1 minute for testing
    )

    scheduler.start()
    print("📋 Jobs registered:", scheduler.get_jobs())
    print("✅ Scheduler started")

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(datasource_router)
app.include_router(table_router)
app.include_router(quality_router)
app.include_router(dashboard_router)






@app.get("/")
def root():
    return {"status": "scheduler running ✅"}
