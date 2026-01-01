from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from app.database import get_db
from app.models.data_source import DataSource

router = APIRouter(prefix="/datasource", tags=["Data Source"])

@router.post("/")
def add_data_source(
    company_id: str,
    db_type: str,
    host: str,
    port: int,
    database_name: str,
    username: str,
    password: str,
    db: Session = Depends(get_db)
):
    if db_type != "postgres":
        raise HTTPException(status_code=400, detail="Only postgres supported")

    db_url = f"postgresql://{username}:{password}@{host}:{port}/{database_name}"

    # 1️⃣ Test DB connection
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {e}")

    # 2️⃣ Save data source
    source = DataSource(
        company_id=company_id,
        db_type=db_type,
        host=host,
        port=port,
        database_name=database_name,
        username=username,
        password=password
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return {
        "message": "Data source added successfully",
        "data_source_id": source.id
    }
