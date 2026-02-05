"""
Project model for client engagements.

Enables enterprise clients (AI labs, hedge funds) to manage large-scale
evaluation and training data projects with multiple experts.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class ProjectStatus(Enum):
    """Project lifecycle status."""
    DRAFT = "draft"              # Being scoped
    ACTIVE = "active"            # In progress
    PAUSED = "paused"            # Temporarily halted
    COMPLETED = "completed"      # All deliverables done
    CANCELLED = "cancelled"      # Project cancelled


class ProjectType(Enum):
    """Types of AI training projects."""
    RLHF_DATA = "rlhf_data"                    # Preference data for RLHF
    DPO_PAIRS = "dpo_pairs"                    # Direct preference pairs
    SFT_DATA = "sft_data"                      # Supervised fine-tuning data
    EVALUATION_FRAMEWORK = "eval_framework"    # Eval scenarios + rubrics
    MODEL_EVALUATION = "model_eval"            # Evaluate model outputs
    RED_TEAMING = "red_teaming"                # Adversarial testing
    DOMAIN_BENCHMARK = "domain_benchmark"      # Domain-specific benchmarks


@dataclass
class ProjectRequirements:
    """Requirements for expert matching."""
    min_years_experience: int = 0
    required_credentials: list[str] = field(default_factory=list)
    required_sectors: list[str] = field(default_factory=list)
    required_skills: list[str] = field(default_factory=list)
    require_buy_side: bool = False
    require_verified: bool = True
    min_quality_score: float = 80.0


@dataclass
class ProjectMilestone:
    """Project milestone for tracking progress."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    deliverables: list[str] = field(default_factory=list)
    due_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    is_completed: bool = False
    tasks_required: int = 0
    tasks_completed: int = 0


@dataclass
class Project:
    """
    Client project for AI training data or evaluation work.

    Supports enterprise-scale engagements with multiple experts,
    milestones, and deliverables.
    """

    # Identity
    id: str = field(default_factory=lambda: f"PROJ-{uuid.uuid4().hex[:8].upper()}")
    name: str = ""
    description: str = ""

    # Client
    client_name: str = ""
    client_contact_email: str = ""
    client_id: Optional[str] = None

    # Classification
    project_type: ProjectType = ProjectType.EVALUATION_FRAMEWORK
    status: ProjectStatus = ProjectStatus.DRAFT

    # Scope
    target_deliverables: int = 0  # Number of scenarios, golden answers, etc.
    current_deliverables: int = 0
    target_hours: float = 0.0
    current_hours: float = 0.0

    # Budget
    budget_total: float = 0.0
    budget_spent: float = 0.0
    hourly_rate_cap: float = 200.0

    # Requirements
    requirements: ProjectRequirements = field(default_factory=ProjectRequirements)

    # Team
    assigned_experts: list[str] = field(default_factory=list)  # Expert IDs
    project_manager_id: Optional[str] = None
    max_experts: int = 10

    # Modules (which eval modules this project covers)
    eval_modules: list[str] = field(default_factory=list)

    # Milestones
    milestones: list[ProjectMilestone] = field(default_factory=list)

    # Tasks
    task_ids: list[str] = field(default_factory=list)

    # Timeline
    start_date: Optional[datetime] = None
    target_end_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None

    # Quality
    quality_threshold: float = 85.0  # Min acceptable quality score
    current_avg_quality: float = 0.0

    # Metadata
    tags: list[str] = field(default_factory=list)
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def completion_percentage(self) -> float:
        """Calculate overall completion percentage."""
        if self.target_deliverables == 0:
            return 0.0
        return (self.current_deliverables / self.target_deliverables) * 100

    @property
    def budget_utilization(self) -> float:
        """Calculate budget utilization percentage."""
        if self.budget_total == 0:
            return 0.0
        return (self.budget_spent / self.budget_total) * 100

    @property
    def is_on_track(self) -> bool:
        """Check if project is on track for deadline."""
        if not self.target_end_date or not self.start_date:
            return True

        now = datetime.utcnow()
        total_duration = (self.target_end_date - self.start_date).days
        elapsed = (now - self.start_date).days

        if total_duration == 0:
            return True

        expected_progress = (elapsed / total_duration) * 100
        return self.completion_percentage >= expected_progress * 0.8  # 80% buffer

    def add_expert(self, expert_id: str) -> bool:
        """Add an expert to the project."""
        if len(self.assigned_experts) >= self.max_experts:
            return False
        if expert_id in self.assigned_experts:
            return False

        self.assigned_experts.append(expert_id)
        self.updated_at = datetime.utcnow()
        return True

    def remove_expert(self, expert_id: str) -> bool:
        """Remove an expert from the project."""
        if expert_id not in self.assigned_experts:
            return False

        self.assigned_experts.remove(expert_id)
        self.updated_at = datetime.utcnow()
        return True

    def add_milestone(self, milestone: ProjectMilestone) -> None:
        """Add a milestone to the project."""
        self.milestones.append(milestone)
        self.updated_at = datetime.utcnow()

    def complete_milestone(self, milestone_id: str) -> bool:
        """Mark a milestone as complete."""
        for milestone in self.milestones:
            if milestone.id == milestone_id:
                milestone.is_completed = True
                milestone.completed_date = datetime.utcnow()
                self.updated_at = datetime.utcnow()
                return True
        return False

    def update_progress(
        self,
        deliverables_added: int = 0,
        hours_added: float = 0.0,
        budget_spent: float = 0.0,
    ) -> None:
        """Update project progress metrics."""
        self.current_deliverables += deliverables_added
        self.current_hours += hours_added
        self.budget_spent += budget_spent
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Serialize project to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "client_name": self.client_name,
            "client_contact_email": self.client_contact_email,
            "project_type": self.project_type.value,
            "status": self.status.value,
            "target_deliverables": self.target_deliverables,
            "current_deliverables": self.current_deliverables,
            "completion_percentage": self.completion_percentage,
            "target_hours": self.target_hours,
            "current_hours": self.current_hours,
            "budget_total": self.budget_total,
            "budget_spent": self.budget_spent,
            "budget_utilization": self.budget_utilization,
            "assigned_experts": self.assigned_experts,
            "max_experts": self.max_experts,
            "eval_modules": self.eval_modules,
            "milestones": [
                {
                    "id": m.id,
                    "name": m.name,
                    "is_completed": m.is_completed,
                    "tasks_required": m.tasks_required,
                    "tasks_completed": m.tasks_completed,
                }
                for m in self.milestones
            ],
            "quality_threshold": self.quality_threshold,
            "current_avg_quality": self.current_avg_quality,
            "is_on_track": self.is_on_track,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "target_end_date": self.target_end_date.isoformat() if self.target_end_date else None,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class ClientDashboard:
    """
    Dashboard view for enterprise clients.

    Provides project management, expert oversight, and quality metrics.
    """

    client_id: str = ""
    client_name: str = ""

    # Active Projects
    active_projects: list[Project] = field(default_factory=list)

    # Aggregate Metrics
    total_projects: int = 0
    total_deliverables: int = 0
    total_hours: float = 0.0
    total_spend: float = 0.0
    avg_quality_score: float = 0.0

    # Expert Pool
    active_experts: int = 0
    total_experts_used: int = 0

    def summary(self) -> dict:
        """Get dashboard summary."""
        return {
            "client_id": self.client_id,
            "client_name": self.client_name,
            "active_projects": len(self.active_projects),
            "total_deliverables": self.total_deliverables,
            "total_hours": self.total_hours,
            "total_spend": self.total_spend,
            "avg_quality_score": self.avg_quality_score,
            "active_experts": self.active_experts,
        }
