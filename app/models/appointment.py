from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from app.dependencies.database import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    mechanic_id = Column(Integer, ForeignKey("mechanics.id", ondelete="SET NULL"), nullable=True)
    appointment_date = Column(DateTime, nullable=False)
    status = Column(String, default="scheduled")

    user = relationship("User", backref="appointments")
    car = relationship("Car", backref="appointments")
    service = relationship("Service", backref="appointments")
    mechanic = relationship("Mechanic", backref="appointments")
