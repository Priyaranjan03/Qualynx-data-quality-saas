from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect

from app.database import get_db
from app.models.data_source import DataSource
from app.models.table_monitored import TableMonitored

router = APIRouter(prefix="/tables", tags=["Tables"])

@router.post("/")
def register_table(
    data_source_id: str,
    table_name: str,
    db: Session = Depends(get_db)
):
    # 1️⃣ Fetch data source
    source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")

    # 2️⃣ Build customer DB URL
    db_url = (
        f"postgresql://{source.username}:{source.password}"
        f"@{source.host}:{source.port}/{source.database_name}"
    )

    # 3️⃣ Validate table exists
    try:
        engine = create_engine(db_url)
        inspector = inspect(engine)
        if table_name not in inspector.get_table_names():
            raise HTTPException(status_code=400, detail="Table not found in source DB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 4️⃣ Save monitored table
    monitored = TableMonitored(
        data_source_id=data_source_id,
        table_name=table_name
    )

    db.add(monitored)
    db.commit()
    db.refresh(monitored)

    return {
        "message": "Table registered successfully",
        "table_id": monitored.id
    }
