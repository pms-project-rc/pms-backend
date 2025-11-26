from sqlalchemy import Column, Integer, String
from app.infrastructure.db.base import Base


class Washer(Base):
    __tablename__ = "washers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    status = Column(String, default="available")
