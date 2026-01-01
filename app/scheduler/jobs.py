from sqlalchemy import create_engine, text
from app.database import SessionLocal
from app.models.table_monitored import TableMonitored
from app.models.data_source import DataSource
from app.models.quality_check_result import QualityCheckResult

import asyncio
import os
from app.alerts.email import send_alert_email


def run_scheduled_row_count_checks():
    print("⏰ JOB TRIGGERED: Running scheduled row count checks")

    db = SessionLocal()
    tables = db.query(TableMonitored).all()

    for table in tables:
        source = db.query(DataSource).filter(
            DataSource.id == table.data_source_id
        ).first()

        if not source:
            continue

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
            print("DB error:", e)
            continue

        # ✅ Decide pass/fail
        status = "pass" if row_count > 0 else "fail"

        # ✅ SAVE RESULT
        result = QualityCheckResult(
            table_id=table.id,
            check_type="row_count",
            status=status,
            details=f"Row count = {row_count}"
        )
        db.add(result)

        # ✅ SEND EMAIL ALERT (THIS IS YOUR CODE)
        if status == "fail":
            asyncio.run(
                send_alert_email(
                    subject="❌ Data Quality Alert",
                    body=f"Table {table.table_name} has ZERO rows",
                    to_email=os.getenv("ALERT_EMAIL")
                )
            )

    db.commit()
    db.close()

    print("✅ Scheduled checks completed")
