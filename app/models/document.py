from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.dependencies.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    mechanic_id = Column(Integer, ForeignKey("mechanics.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)

    mechanic = relationship("Mechanic", backref="documents")
