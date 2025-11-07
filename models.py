"""
Database models for Flow Forecaster
SQLAlchemy models for persisting forecasts, projects, and actuals
"""
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

Base = declarative_base()


class User(Base, UserMixin):
    """User entity for authentication and multi-tenancy"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)
    name = Column(String(200), nullable=False)
    role = Column(String(20), default='student')  # student, instructor, admin
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    access_expires_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.utcnow() + timedelta(days=365)
    )

    # Relationships
    projects = relationship('Project', back_populates='user', cascade='all, delete-orphan')
    forecasts = relationship('Forecast', back_populates='user', cascade='all, delete-orphan')
    cod_datasets = relationship('CoDTrainingDataset', back_populates='user', cascade='all, delete-orphan')
    cod_model = relationship('CoDModel', back_populates='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'access_expires_at': self.access_expires_at.isoformat() if self.access_expires_at else None,
        }


class Project(Base):
    """Project/Team entity"""
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)  # Owner of the project
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    team_size = Column(Integer, default=1)

    # Portfolio management fields
    status = Column(String(50), default='active')  # active, on_hold, completed, cancelled
    priority = Column(Integer, default=3)  # 1 (highest) to 5 (lowest)
    business_value = Column(Integer, default=50)  # 0-100 scale
    risk_level = Column(String(20), default='medium')  # low, medium, high, critical
    capacity_allocated = Column(Float, default=1.0)  # FTE (Full-Time Equivalent)
    strategic_importance = Column(String(20), default='medium')  # low, medium, high, critical

    # Project dates
    start_date = Column(String(20), nullable=True)  # DD/MM/YYYY
    target_end_date = Column(String(20), nullable=True)  # DD/MM/YYYY

    # Project owner/stakeholder
    owner = Column(String(200), nullable=True)
    stakeholder = Column(String(200), nullable=True)

    # Tags for categorization
    tags = Column(Text, nullable=True)  # JSON array of tags

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='projects')
    forecasts = relationship('Forecast', back_populates='project', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'team_size': self.team_size,
            'status': self.status,
            'priority': self.priority,
            'business_value': self.business_value,
            'risk_level': self.risk_level,
            'capacity_allocated': self.capacity_allocated,
            'strategic_importance': self.strategic_importance,
            'start_date': self.start_date,
            'target_end_date': self.target_end_date,
            'owner': self.owner,
            'stakeholder': self.stakeholder,
            'tags': json.loads(self.tags) if self.tags else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'forecasts_count': len(self.forecasts) if self.forecasts else 0
        }


class Forecast(Base):
    """Saved forecast/analysis"""
    __tablename__ = 'forecasts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)  # Owner of the forecast
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
    user = relationship('User', back_populates='forecasts')
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


class Portfolio(Base):
    """Portfolio entity - collection of related projects"""
    __tablename__ = 'portfolios'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Portfolio management
    status = Column(String(50), default='active')  # active, planning, on_hold, completed
    portfolio_type = Column(String(50), default='standard')  # standard, strategic, tactical

    # Budget and resources
    total_budget = Column(Float, nullable=True)  # Total budget in currency
    total_capacity = Column(Float, nullable=True)  # Total FTE capacity

    # Dates
    start_date = Column(String(20), nullable=True)  # DD/MM/YYYY
    target_end_date = Column(String(20), nullable=True)  # DD/MM/YYYY

    # Owner/stakeholder
    owner = Column(String(200), nullable=True)
    sponsor = Column(String(200), nullable=True)

    # Metadata
    tags = Column(Text, nullable=True)  # JSON array of tags
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('User', backref='portfolios')
    portfolio_projects = relationship('PortfolioProject', back_populates='portfolio', cascade='all, delete-orphan')
    simulation_runs = relationship('SimulationRun', back_populates='portfolio', cascade='all, delete-orphan')

    def to_dict(self, include_projects=False):
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'portfolio_type': self.portfolio_type,
            'total_budget': self.total_budget,
            'total_capacity': self.total_capacity,
            'start_date': self.start_date,
            'target_end_date': self.target_end_date,
            'owner': self.owner,
            'sponsor': self.sponsor,
            'tags': json.loads(self.tags) if self.tags else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'projects_count': len(self.portfolio_projects) if self.portfolio_projects else 0
        }

        if include_projects and self.portfolio_projects:
            result['projects'] = [pp.to_dict() for pp in self.portfolio_projects]

        return result


class PortfolioProject(Base):
    """Many-to-many relationship between Portfolio and Project with additional metadata"""
    __tablename__ = 'portfolio_projects'

    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, index=True)

    # Project-specific portfolio metadata
    portfolio_priority = Column(Integer, default=3)  # Priority within this portfolio (1-5)
    budget_allocated = Column(Float, nullable=True)  # Budget allocated from portfolio
    capacity_allocated = Column(Float, nullable=True)  # FTE allocated from portfolio

    # Cost of Delay metrics
    cod_weekly = Column(Float, nullable=True)  # Weekly cost of delay (R$/week)
    business_value_score = Column(Integer, default=50)  # 0-100
    time_criticality_score = Column(Integer, default=50)  # 0-100
    risk_reduction_score = Column(Integer, default=50)  # 0-100
    wsjf_score = Column(Float, nullable=True)  # Weighted Shortest Job First score

    # Dependencies
    depends_on = Column(Text, nullable=True)  # JSON array of project_ids that this depends on
    blocks = Column(Text, nullable=True)  # JSON array of project_ids that this blocks

    # Dates
    added_at = Column(DateTime, default=datetime.utcnow)
    removed_at = Column(DateTime, nullable=True)  # If project removed from portfolio
    is_active = Column(Boolean, default=True)

    # Relationships
    portfolio = relationship('Portfolio', back_populates='portfolio_projects')
    project = relationship('Project', backref='portfolio_memberships')
class CoDTrainingDataset(Base):
    """Persisted Cost of Delay training datasets per user."""
    __tablename__ = 'cod_training_datasets'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    name = Column(String(200), nullable=True)
    original_filename = Column(String(255), nullable=False)
    data = Column(Text, nullable=False)  # JSON array of records
    column_names = Column(Text, nullable=False)  # JSON array of column names
    row_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='cod_datasets')

    def to_dict(self):
        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'portfolio_priority': self.portfolio_priority,
            'budget_allocated': self.budget_allocated,
            'capacity_allocated': self.capacity_allocated,
            'cod_weekly': self.cod_weekly,
            'business_value_score': self.business_value_score,
            'time_criticality_score': self.time_criticality_score,
            'risk_reduction_score': self.risk_reduction_score,
            'wsjf_score': self.wsjf_score,
            'depends_on': json.loads(self.depends_on) if self.depends_on else [],
            'blocks': json.loads(self.blocks) if self.blocks else [],
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'removed_at': self.removed_at.isoformat() if self.removed_at else None,
            'is_active': self.is_active,
            'project': self.project.to_dict() if self.project else None
        }


class SimulationRun(Base):
    """Stores portfolio-level Monte Carlo simulation results"""
    __tablename__ = 'simulation_runs'

    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

    # Simulation metadata
    simulation_name = Column(String(200), nullable=False)
    simulation_type = Column(String(50), default='portfolio_completion')  # portfolio_completion, capacity_planning, risk_analysis
    description = Column(Text, nullable=True)

    # Simulation parameters
    n_simulations = Column(Integer, default=10000)
    confidence_level = Column(String(10), default='P85')  # P50, P85, P95

    # Input data snapshot
    input_data = Column(Text, nullable=False)  # JSON with all inputs (projects, throughputs, etc.)

    # Results
    results_data = Column(Text, nullable=False)  # JSON with full simulation results

    # Key metrics (denormalized for quick access)
    portfolio_completion_p50 = Column(Float, nullable=True)  # Weeks to complete portfolio at P50
    portfolio_completion_p85 = Column(Float, nullable=True)  # Weeks to complete portfolio at P85
    portfolio_completion_p95 = Column(Float, nullable=True)  # Weeks to complete portfolio at P95

    total_cost_of_delay = Column(Float, nullable=True)  # Total CoD for portfolio
    critical_path_projects = Column(Text, nullable=True)  # JSON array of critical project IDs

    # Risk metrics
    risk_score = Column(Float, nullable=True)  # Overall portfolio risk (0-100)
    high_risk_projects_count = Column(Integer, nullable=True)

    # Status
    status = Column(String(50), default='completed')  # running, completed, failed

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), nullable=True)

    # Relationships
    portfolio = relationship('Portfolio', back_populates='simulation_runs')
    user = relationship('User', backref='simulation_runs')

    def to_dict(self, include_full_data=False):
        result = {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'portfolio_name': self.portfolio.name if self.portfolio else None,
            'user_id': self.user_id,
            'simulation_name': self.simulation_name,
            'simulation_type': self.simulation_type,
            'description': self.description,
            'n_simulations': self.n_simulations,
            'confidence_level': self.confidence_level,
            'portfolio_completion_p50': self.portfolio_completion_p50,
            'portfolio_completion_p85': self.portfolio_completion_p85,
            'portfolio_completion_p95': self.portfolio_completion_p95,
            'total_cost_of_delay': self.total_cost_of_delay,
            'critical_path_projects': json.loads(self.critical_path_projects) if self.critical_path_projects else [],
            'risk_score': self.risk_score,
            'high_risk_projects_count': self.high_risk_projects_count,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by
        }

        if include_full_data:
            result['input_data'] = json.loads(self.input_data) if self.input_data else None
            result['results_data'] = json.loads(self.results_data) if self.results_data else None

        return result


class CoDTrainingDataset(Base):
    """Persisted CoD training datasets per user."""
    __tablename__ = 'cod_training_datasets'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    name = Column(String(200), nullable=True)
    original_filename = Column(String(255), nullable=False)
    data = Column(Text, nullable=False)  # JSON array of records
    column_names = Column(Text, nullable=False)  # JSON array of column names
    row_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='cod_datasets')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'original_filename': self.original_filename,
            'row_count': self.row_count,
            'column_names': json.loads(self.column_names) if self.column_names else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class CoDModel(Base):
    """Persisted Cost of Delay models per user."""
    __tablename__ = 'cod_models'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True, index=True)
    model_blob = Column(LargeBinary, nullable=False)
    scaler_blob = Column(LargeBinary, nullable=True)
    feature_names = Column(Text, nullable=True)  # JSON array
    project_types = Column(Text, nullable=True)  # JSON array
    metrics = Column(Text, nullable=True)  # JSON summary
    sample_count = Column(Integer, nullable=True)
    trained_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='cod_model')

    def get_metrics(self):
        return json.loads(self.metrics) if self.metrics else None
