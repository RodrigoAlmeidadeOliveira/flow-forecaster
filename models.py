"""
Database models for Flow Forecaster
SQLAlchemy models for persisting forecasts, projects, and actuals
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import json

Base = declarative_base()


class Project(Base):
    """Project/Team entity"""
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    team_size = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    forecasts = relationship('Forecast', back_populates='project', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'team_size': self.team_size,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'forecasts_count': len(self.forecasts) if self.forecasts else 0
        }


class Forecast(Base):
    """Saved forecast/analysis"""
    __tablename__ = 'forecasts'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    forecast_type = Column(String(50), default='deadline')  # deadline, throughput, cost, etc.

    # Snapshot of the forecast at save time
    forecast_data = Column(Text, nullable=False)  # JSON blob with all forecast results
    input_data = Column(Text, nullable=False)  # JSON blob with all inputs (tp_samples, backlog, etc.)

    # Key metrics for quick access (denormalized for performance)
    backlog = Column(Integer, nullable=True)
    deadline_date = Column(String(20), nullable=True)  # DD/MM/YYYY
    start_date = Column(String(20), nullable=True)  # DD/MM/YYYY
    weeks_to_deadline = Column(Float, nullable=True)
    projected_weeks_p85 = Column(Float, nullable=True)
    can_meet_deadline = Column(Boolean, nullable=True)
    scope_completion_pct = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), nullable=True)  # For future multi-user support

    # For versioning
    version = Column(Integer, default=1)
    parent_forecast_id = Column(Integer, ForeignKey('forecasts.id'), nullable=True)

    # Relationships
    project = relationship('Project', back_populates='forecasts')
    actuals = relationship('Actual', back_populates='forecast', cascade='all, delete-orphan')
    parent = relationship('Forecast', remote_side=[id], backref='versions')

    def to_dict(self, include_data=True):
        result = {
            'id': self.id,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'name': self.name,
            'description': self.description,
            'forecast_type': self.forecast_type,
            'backlog': self.backlog,
            'deadline_date': self.deadline_date,
            'start_date': self.start_date,
            'weeks_to_deadline': self.weeks_to_deadline,
            'projected_weeks_p85': self.projected_weeks_p85,
            'can_meet_deadline': self.can_meet_deadline,
            'scope_completion_pct': self.scope_completion_pct,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'version': self.version,
            'parent_forecast_id': self.parent_forecast_id
        }

        if include_data:
            result['forecast_data'] = json.loads(self.forecast_data) if self.forecast_data else None
            result['input_data'] = json.loads(self.input_data) if self.input_data else None

        return result

    def to_summary(self):
        """Lightweight version without full data blobs"""
        return self.to_dict(include_data=False)


class Actual(Base):
    """Actual results for comparison with forecasts"""
    __tablename__ = 'actuals'

    id = Column(Integer, primary_key=True)
    forecast_id = Column(Integer, ForeignKey('forecasts.id'), nullable=False)

    # Actual results
    actual_completion_date = Column(String(20), nullable=True)  # DD/MM/YYYY
    actual_weeks_taken = Column(Float, nullable=True)
    actual_items_completed = Column(Integer, nullable=True)
    actual_scope_delivered_pct = Column(Float, nullable=True)

    # Accuracy metrics
    weeks_error = Column(Float, nullable=True)  # actual - projected
    weeks_error_pct = Column(Float, nullable=True)  # (actual - projected) / projected * 100
    scope_error_pct = Column(Float, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    recorded_at = Column(DateTime, default=datetime.utcnow)
    recorded_by = Column(String(100), nullable=True)

    # Relationship
    forecast = relationship('Forecast', back_populates='actuals')

    def to_dict(self):
        return {
            'id': self.id,
            'forecast_id': self.forecast_id,
            'actual_completion_date': self.actual_completion_date,
            'actual_weeks_taken': self.actual_weeks_taken,
            'actual_items_completed': self.actual_items_completed,
            'actual_scope_delivered_pct': self.actual_scope_delivered_pct,
            'weeks_error': self.weeks_error,
            'weeks_error_pct': self.weeks_error_pct,
            'scope_error_pct': self.scope_error_pct,
            'notes': self.notes,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'recorded_by': self.recorded_by
        }
