from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text

from app.database import get_db
from app.models.table_monitored import TableMonitored
from app.models.data_source import DataSource
from app.models.quality_check_result import QualityCheckResult

router = APIRouter(prefix="/quality", tags=["Quality Checks"])

@router.post("/run/{table_id}")
def run_row_count_check(
    table_id: str,
    db: Session = Depends(get_db)
):
    # 1️⃣ Fetch table
    table = db.query(TableMonitored).filter(TableMonitored.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    # 2️⃣ Fetch data source
    source = db.query(DataSource).filter(
        DataSource.id == table.data_source_id
    ).first()

    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")

    # 3️⃣ Connect to customer DB
    db_url = (
        f"postgresql://{source.username}:{source.password}"
        f"@{source.host}:{source.port}/{source.database_name}"
    )

    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            row_count = conn.execute(
                text(f"SELECT COUNT(*) FROM {table.table_name}")
            ).scalar()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 4️⃣ Decide pass/fail
    status = "pass" if row_count > 0 else "fail"

    # 5️⃣ Save result
    result = QualityCheckResult(
        table_id=table.id,
        check_type="row_count",
        status=status,
        details=f"Row count = {row_count}"
    )

    db.add(result)
    db.commit()
    db.refresh(result)

    return {
        "table": table.table_name,
        "row_count": row_count,
        "status": status
    }
