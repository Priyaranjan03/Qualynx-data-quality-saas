from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db
from app.models.table_monitored import TableMonitored
from app.models.quality_check_result import QualityCheckResult

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# 1️⃣ Summary metrics
@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    total_tables = db.query(TableMonitored).count()
    total_checks = db.query(QualityCheckResult).count()
    failed_checks = (
        db.query(QualityCheckResult)
        .filter(QualityCheckResult.status == "fail")
        .count()
    )

    return {
        "total_tables": total_tables,
        "total_checks": total_checks,
        "failed_checks": failed_checks
    }


# 2️⃣ Recent failures (latest 10)
@router.get("/recent-failures")
def recent_failures(db: Session = Depends(get_db)):
    failures = (
        db.query(QualityCheckResult)
        .filter(QualityCheckResult.status == "fail")
        .order_by(QualityCheckResult.created_at.desc())
        .limit(10)
        .all()
    )

    return [
        {
            "table_id": f.table_id,
            "check_type": f.check_type,
            "details": f.details,
            "time": f.created_at
        }
        for f in failures
    ]


# 3️⃣ Trend (last 7 days)
@router.get("/trend")
def daily_trend(db: Session = Depends(get_db)):
    start_date = datetime.utcnow() - timedelta(days=7)

    data = (
        db.query(
            func.date(QualityCheckResult.created_at).label("date"),
            func.count(QualityCheckResult.id).label("count")
        )
        .filter(QualityCheckResult.created_at >= start_date)
        .group_by(func.date(QualityCheckResult.created_at))
        .order_by(func.date(QualityCheckResult.created_at))
        .all()
    )

    return [
        {
            "date": str(row.date),
            "checks": row.count
        }
        for row in data
    ]
