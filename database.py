from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timedelta

# Using SQLite for instant, zero-config local development
SQLALCHEMY_DATABASE_URL = "sqlite:///./bosch_gdpr.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Add this class to database.py
class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    password = Column(String) # Plaintext is fine for a hackathon!
    department = Column(String)
    location = Column(String)

class FileMetadata(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, unique=True, index=True)
    owner_employee_id = Column(String, index=True)
    size_bytes = Column(Integer)
    last_modified = Column(DateTime)
    file_hash = Column(String) # Crucial for the Delta Scan
    retention_deadline = Column(DateTime)

class Finding(Base):
    __tablename__ = "findings"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, index=True)
    category = Column(String) # e.g., "Passport Number"
    confidence_score = Column(Float)
    flagged_snippet = Column(String)
    reasoning = Column(String)
    status = Column(String, default="Pending") # Options: Pending, Deleted, False_Positive

# Create the tables in the database
Base.metadata.create_all(bind=engine)