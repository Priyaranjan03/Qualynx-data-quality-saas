import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class TableMonitored(Base):
    __tablename__ = "tables_monitored"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    data_source_id = Column(
        UUID(as_uuid=True),
        ForeignKey("data_sources.id"),
        nullable=False
    )

    table_name = Column(String(255), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
