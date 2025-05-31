"""
Database utilities for the CrewAI application
"""
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config.config import Config

# Create SQLAlchemy engine from environment DATABASE_URL
engine = create_engine(Config.DATABASE_URL) if Config.DATABASE_URL else None
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None
Base = declarative_base()

class Execution(Base):
    """Model for storing CrewAI execution records"""
    __tablename__ = "executions"
    
    id = Column(Integer, primary_key=True, index=True)
    crew_type = Column(String(100), nullable=False)
    inputs = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)
    status = Column(String(50), default="completed")
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationship to results
    results = relationship("ExecutionResult", back_populates="execution", cascade="all, delete-orphan")

class ExecutionResult(Base):
    """Model for storing results from CrewAI executions"""
    __tablename__ = "execution_results"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("executions.id"))
    agent_role = Column(String(100), nullable=True)
    task_description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationship to execution
    execution = relationship("Execution", back_populates="results")

def init_db():
    """Initialize the database if engine is available"""
    if engine:
        Base.metadata.create_all(bind=engine)
        return True
    return False

def get_db():
    """Get a database session"""
    if SessionLocal:
        db = SessionLocal()
        try:
            return db
        finally:
            db.close()
    return None

def store_execution(crew_type: str, inputs: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Optional[int]:
    """
    Store a new execution record
    
    Args:
        crew_type: Type of crew executed
        inputs: Input parameters provided to the crew
        metadata: Additional metadata about the execution
        
    Returns:
        ID of the created execution record, or None if database is not available
    """
    if not SessionLocal:
        return None
    
    db = get_db()
    if not db:
        return None
    
    try:
        execution = Execution(
            crew_type=crew_type,
            inputs=inputs,
            metadata=metadata,
            status="in_progress"
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)
        return execution.id
    except Exception as e:
        print(f"Error storing execution: {str(e)}")
        return None
    finally:
        db.close()

def update_execution_status(execution_id: int, status: str) -> bool:
    """
    Update the status of an execution
    
    Args:
        execution_id: ID of the execution to update
        status: New status value
        
    Returns:
        True if update was successful, False otherwise
    """
    if not SessionLocal:
        return False
    
    db = get_db()
    if not db:
        return False
    
    try:
        execution = db.query(Execution).filter(Execution.id == execution_id).first()
        if execution:
            execution.status = status
            db.commit()
            return True
        return False
    except Exception as e:
        print(f"Error updating execution status: {str(e)}")
        return False
    finally:
        db.close()

def store_execution_result(
    execution_id: int, 
    content: str, 
    agent_role: Optional[str] = None,
    task_description: Optional[str] = None
) -> Optional[int]:
    """
    Store an execution result
    
    Args:
        execution_id: ID of the associated execution
        content: Result content
        agent_role: Role of the agent that produced the result
        task_description: Description of the task
        
    Returns:
        ID of the created result record, or None if database is not available
    """
    if not SessionLocal:
        return None
    
    db = get_db()
    if not db:
        return None
    
    try:
        result = ExecutionResult(
            execution_id=execution_id,
            agent_role=agent_role,
            task_description=task_description,
            content=content
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        return result.id
    except Exception as e:
        print(f"Error storing execution result: {str(e)}")
        return None
    finally:
        db.close()
