from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Exposure(Base):
    __tablename__ = "exposures"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(String, unique=True, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    building_type = Column(String)
    tiv = Column(Float)
    deductible = Column(Float)
    policy_limit = Column(Float)

class SimulationRun(Base):
    __tablename__ = "simulation_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Config
    sims = Column(Integer)
    hazard_type = Column(String)
    severity = Column(String)
    seed = Column(Integer)
    
    # Results
    aal = Column(Float)
    pml100 = Column(Float)
    pml250 = Column(Float)
    runtime_sec = Column(Float)
