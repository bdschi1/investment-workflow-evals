"""Task model for work assignments."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import uuid

from .user import Expertise, UserTier


class TaskType(Enum):
    """Types of tasks available on the platform."""

    # Content Creation
    SCENARIO_CREATION = "scenario_creation"
    GOLDEN_ANSWER = "golden_answer"
    RUBRIC_DEVELOPMENT = "rubric_development"
    ADVERSARIAL_TEST = "adversarial_test"

    # Review & QA
    SUBMISSION_REVIEW = "submission_review"
    PEER_REVIEW = "peer_review"
    EXPERT_AUDIT = "expert_audit"

    # Evaluation
    EVAL_EXECUTION = "eval_execution"
    COMPARATIVE_EVAL = "comparative_eval"

    # Special
    QUALIFICATION_TEST = "qualification_test"
    TRAINING_TASK = "training_task"

    @property
    def base_payment(self) -> float:
        """Base payment amount in USD for this task type."""
        payments = {
            TaskType.SCENARIO_CREATION: 100.0,
            TaskType.GOLDEN_ANSWER: 125.0,
            TaskType.RUBRIC_DEVELOPMENT: 75.0,
            TaskType.ADVERSARIAL_TEST: 50.0,
            TaskType.SUBMISSION_REVIEW: 35.0,
            TaskType.PEER_REVIEW: 25.0,
            TaskType.EXPERT_AUDIT: 75.0,
            TaskType.EVAL_EXECUTION: 50.0,
            TaskType.COMPARATIVE_EVAL: 60.0,
            TaskType.QUALIFICATION_TEST: 0.0,
            TaskType.TRAINING_TASK: 15.0,
        }
        return payments[self]

    @property
    def estimated_hours(self) -> float:
        """Estimated hours to complete this task type."""
        hours = {
            TaskType.SCENARIO_CREATION: 2.0,
            TaskType.GOLDEN_ANSWER: 3.0,
            TaskType.RUBRIC_DEVELOPMENT: 1.5,
            TaskType.ADVERSARIAL_TEST: 1.0,
            TaskType.SUBMISSION_REVIEW: 0.75,
            TaskType.PEER_REVIEW: 0.5,
            TaskType.EXPERT_AUDIT: 1.5,
            TaskType.EVAL_EXECUTION: 1.0,
            TaskType.COMPARATIVE_EVAL: 1.25,
            TaskType.QUALIFICATION_TEST: 0.5,
            TaskType.TRAINING_TASK: 0.5,
        }
        return hours[self]

    @property
    def min_tier_required(self) -> UserTier:
        """Minimum user tier required to claim this task type."""
        tiers = {
            TaskType.SCENARIO_CREATION: UserTier.STANDARD,
            TaskType.GOLDEN_ANSWER: UserTier.SENIOR,
            TaskType.RUBRIC_DEVELOPMENT: UserTier.SENIOR,
            TaskType.ADVERSARIAL_TEST: UserTier.STANDARD,
            TaskType.SUBMISSION_REVIEW: UserTier.SENIOR,
            TaskType.PEER_REVIEW: UserTier.SENIOR,
            TaskType.EXPERT_AUDIT: UserTier.EXPERT,
            TaskType.EVAL_EXECUTION: UserTier.STANDARD,
            TaskType.COMPARATIVE_EVAL: UserTier.STANDARD,
            TaskType.QUALIFICATION_TEST: UserTier.TRAINEE,
            TaskType.TRAINING_TASK: UserTier.TRAINEE,
        }
        return tiers[self]


class TaskStatus(Enum):
    """Task lifecycle status."""

    DRAFT = "draft"              # Being created, not visible
    OPEN = "open"                # Available for claiming
    CLAIMED = "claimed"          # Assigned to contributor
    IN_PROGRESS = "in_progress"  # Work has started
    SUBMITTED = "submitted"      # Work submitted for review
    IN_REVIEW = "in_review"      # Under review
    REVISION = "revision"        # Needs changes
    APPROVED = "approved"        # Passed QA
    REJECTED = "rejected"        # Failed QA, not salvageable
    CANCELLED = "cancelled"      # Cancelled by admin
    PAID = "paid"                # Payment processed


class TaskPriority(Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

    @property
    def priority_bonus(self) -> float:
        """Payment bonus multiplier for priority."""
        bonuses = {
            TaskPriority.LOW: 1.0,
            TaskPriority.MEDIUM: 1.0,
            TaskPriority.HIGH: 1.15,
            TaskPriority.URGENT: 1.30,
        }
        return bonuses[self]


@dataclass
class Task:
    """A work task for domain expert contributors."""

    # Identity
    id: str = field(default_factory=lambda: f"TASK-{uuid.uuid4().hex[:8].upper()}")
    title: str = ""
    description: str = ""

    # Classification
    task_type: TaskType = TaskType.TRAINING_TASK
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.DRAFT

    # Module Association
    eval_module: str = ""  # e.g., "01_equity_thesis"
    scenario_name: Optional[str] = None  # If task is for a specific scenario

    # Requirements
    required_expertise: list[Expertise] = field(default_factory=list)
    min_tier: UserTier = UserTier.TRAINEE
    estimated_hours: float = 1.0

    # Assignment
    created_by: Optional[str] = None  # User ID
    assigned_to: Optional[str] = None  # User ID
    reviewer_id: Optional[str] = None  # User ID

    # Payment
    base_payment: float = 0.0
    bonus_payment: float = 0.0
    final_payment: Optional[float] = None

    # Deadlines
    deadline: Optional[datetime] = None
    claimed_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None

    # Content
    instructions: str = ""
    resources: list[str] = field(default_factory=list)  # URLs or file paths
    deliverables: list[str] = field(default_factory=list)  # Expected outputs
    acceptance_criteria: list[str] = field(default_factory=list)

    # Submission
    submission_file: Optional[str] = None
    submission_notes: Optional[str] = None

    # Review
    review_score: Optional[float] = None
    review_feedback: Optional[str] = None
    revision_count: int = 0
    max_revisions: int = 2

    # Metadata
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Set defaults based on task type."""
        if self.base_payment == 0.0:
            self.base_payment = self.task_type.base_payment
        if self.estimated_hours == 1.0:
            self.estimated_hours = self.task_type.estimated_hours
        if self.min_tier == UserTier.TRAINEE:
            self.min_tier = self.task_type.min_tier_required

    @property
    def is_claimable(self) -> bool:
        """Check if task can be claimed."""
        return self.status == TaskStatus.OPEN

    @property
    def is_overdue(self) -> bool:
        """Check if task is past deadline."""
        if self.deadline is None:
            return False
        return datetime.utcnow() > self.deadline

    @property
    def time_remaining(self) -> Optional[timedelta]:
        """Get time remaining until deadline."""
        if self.deadline is None:
            return None
        remaining = self.deadline - datetime.utcnow()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)

    @property
    def can_revise(self) -> bool:
        """Check if task can be revised again."""
        return self.revision_count < self.max_revisions

    def calculate_payment(self, user_tier: UserTier) -> float:
        """Calculate total payment for this task."""
        base = self.base_payment
        tier_multiplier = user_tier.rate_multiplier
        priority_bonus = self.priority.priority_bonus
        bonus = self.bonus_payment

        return (base * tier_multiplier * priority_bonus) + bonus

    def claim(self, user_id: str) -> bool:
        """Claim the task for a user."""
        if not self.is_claimable:
            return False

        self.assigned_to = user_id
        self.status = TaskStatus.CLAIMED
        self.claimed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        # Set default deadline if not set (7 days from claim)
        if self.deadline is None:
            self.deadline = datetime.utcnow() + timedelta(days=7)

        return True

    def start(self) -> bool:
        """Mark task as in progress."""
        if self.status != TaskStatus.CLAIMED:
            return False

        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow()
        return True

    def submit(self, file_path: str, notes: Optional[str] = None) -> bool:
        """Submit completed work."""
        if self.status not in (TaskStatus.IN_PROGRESS, TaskStatus.REVISION):
            return False

        self.submission_file = file_path
        self.submission_notes = notes
        self.status = TaskStatus.SUBMITTED
        self.submitted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return True

    def assign_reviewer(self, reviewer_id: str) -> bool:
        """Assign a reviewer to the task."""
        if self.status != TaskStatus.SUBMITTED:
            return False

        self.reviewer_id = reviewer_id
        self.status = TaskStatus.IN_REVIEW
        self.updated_at = datetime.utcnow()
        return True

    def approve(self, score: float, feedback: str) -> bool:
        """Approve the submission."""
        if self.status != TaskStatus.IN_REVIEW:
            return False

        self.review_score = score
        self.review_feedback = feedback
        self.status = TaskStatus.APPROVED
        self.reviewed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return True

    def request_revision(self, feedback: str) -> bool:
        """Request revisions to the submission."""
        if self.status != TaskStatus.IN_REVIEW:
            return False

        if not self.can_revise:
            return False

        self.review_feedback = feedback
        self.status = TaskStatus.REVISION
        self.revision_count += 1
        self.updated_at = datetime.utcnow()
        return True

    def reject(self, feedback: str) -> bool:
        """Reject the submission."""
        if self.status != TaskStatus.IN_REVIEW:
            return False

        self.review_feedback = feedback
        self.status = TaskStatus.REJECTED
        self.reviewed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return True

    def release(self) -> bool:
        """Release a claimed task back to the pool."""
        if self.status not in (TaskStatus.CLAIMED, TaskStatus.IN_PROGRESS):
            return False

        self.assigned_to = None
        self.status = TaskStatus.OPEN
        self.claimed_at = None
        self.deadline = None
        self.updated_at = datetime.utcnow()
        return True

    def to_dict(self) -> dict:
        """Serialize task to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "eval_module": self.eval_module,
            "scenario_name": self.scenario_name,
            "required_expertise": [e.value for e in self.required_expertise],
            "min_tier": self.min_tier.value,
            "estimated_hours": self.estimated_hours,
            "created_by": self.created_by,
            "assigned_to": self.assigned_to,
            "reviewer_id": self.reviewer_id,
            "base_payment": self.base_payment,
            "bonus_payment": self.bonus_payment,
            "final_payment": self.final_payment,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "claimed_at": self.claimed_at.isoformat() if self.claimed_at else None,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "instructions": self.instructions,
            "resources": self.resources,
            "deliverables": self.deliverables,
            "acceptance_criteria": self.acceptance_criteria,
            "submission_file": self.submission_file,
            "submission_notes": self.submission_notes,
            "review_score": self.review_score,
            "review_feedback": self.review_feedback,
            "revision_count": self.revision_count,
            "max_revisions": self.max_revisions,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_claimable": self.is_claimable,
            "is_overdue": self.is_overdue,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Deserialize task from dictionary."""
        task = cls(
            id=data.get("id", f"TASK-{uuid.uuid4().hex[:8].upper()}"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            task_type=TaskType(data.get("task_type", "training_task")),
            priority=TaskPriority(data.get("priority", "medium")),
            status=TaskStatus(data.get("status", "draft")),
            eval_module=data.get("eval_module", ""),
            scenario_name=data.get("scenario_name"),
            required_expertise=[Expertise(e) for e in data.get("required_expertise", [])],
            min_tier=UserTier(data.get("min_tier", "trainee")),
            estimated_hours=data.get("estimated_hours", 1.0),
            created_by=data.get("created_by"),
            assigned_to=data.get("assigned_to"),
            reviewer_id=data.get("reviewer_id"),
            base_payment=data.get("base_payment", 0.0),
            bonus_payment=data.get("bonus_payment", 0.0),
            final_payment=data.get("final_payment"),
            instructions=data.get("instructions", ""),
            resources=data.get("resources", []),
            deliverables=data.get("deliverables", []),
            acceptance_criteria=data.get("acceptance_criteria", []),
            submission_file=data.get("submission_file"),
            submission_notes=data.get("submission_notes"),
            review_score=data.get("review_score"),
            review_feedback=data.get("review_feedback"),
            revision_count=data.get("revision_count", 0),
            max_revisions=data.get("max_revisions", 2),
            tags=data.get("tags", []),
        )

        # Parse datetime fields
        for field_name in ["deadline", "claimed_at", "submitted_at", "reviewed_at", "created_at", "updated_at"]:
            if data.get(field_name):
                setattr(task, field_name, datetime.fromisoformat(data[field_name]))

        return task
