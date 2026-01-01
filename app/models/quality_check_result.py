import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class QualityCheckResult(Base):
    __tablename__ = "quality_check_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    table_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tables_monitored.id"),
        nullable=False
    )

    check_type = Column(String(100), nullable=False)   # row_count
    status = Column(String(20), nullable=False)        # pass / fail
    details = Column(String(255))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
