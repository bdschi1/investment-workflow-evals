"""Submission and Review models for work products."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class SubmissionStatus(Enum):
    """Status of a submission."""

    DRAFT = "draft"              # Being prepared
    SUBMITTED = "submitted"      # Awaiting review
    IN_REVIEW = "in_review"      # Under review
    APPROVED = "approved"        # Passed QA
    REVISION_REQUESTED = "revision_requested"  # Needs changes
    REVISED = "revised"          # Revised and resubmitted
    REJECTED = "rejected"        # Failed QA


@dataclass
class Review:
    """A review of a submission."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    submission_id: str = ""
    reviewer_id: str = ""

    # Scoring (0-100 scale)
    overall_score: float = 0.0

    # Dimension Scores (for evaluation content)
    factual_accuracy_score: Optional[float] = None
    analytical_rigor_score: Optional[float] = None
    completeness_score: Optional[float] = None
    clarity_score: Optional[float] = None
    format_compliance_score: Optional[float] = None

    # Feedback
    summary_feedback: str = ""
    detailed_feedback: str = ""
    improvement_suggestions: list[str] = field(default_factory=list)

    # Flags
    has_critical_errors: bool = False
    critical_error_details: Optional[str] = None
    recommended_action: str = "approve"  # approve, revise, reject

    # Timestamps
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    # Time tracking
    review_duration_minutes: Optional[int] = None

    def complete(self) -> None:
        """Mark review as complete."""
        self.completed_at = datetime.utcnow()
        if self.started_at:
            duration = self.completed_at - self.started_at
            self.review_duration_minutes = int(duration.total_seconds() / 60)

    def to_dict(self) -> dict:
        """Serialize review to dictionary."""
        return {
            "id": self.id,
            "submission_id": self.submission_id,
            "reviewer_id": self.reviewer_id,
            "overall_score": self.overall_score,
            "factual_accuracy_score": self.factual_accuracy_score,
            "analytical_rigor_score": self.analytical_rigor_score,
            "completeness_score": self.completeness_score,
            "clarity_score": self.clarity_score,
            "format_compliance_score": self.format_compliance_score,
            "summary_feedback": self.summary_feedback,
            "detailed_feedback": self.detailed_feedback,
            "improvement_suggestions": self.improvement_suggestions,
            "has_critical_errors": self.has_critical_errors,
            "critical_error_details": self.critical_error_details,
            "recommended_action": self.recommended_action,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "review_duration_minutes": self.review_duration_minutes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Review":
        """Deserialize review from dictionary."""
        review = cls(
            id=data.get("id", str(uuid.uuid4())),
            submission_id=data.get("submission_id", ""),
            reviewer_id=data.get("reviewer_id", ""),
            overall_score=data.get("overall_score", 0.0),
            factual_accuracy_score=data.get("factual_accuracy_score"),
            analytical_rigor_score=data.get("analytical_rigor_score"),
            completeness_score=data.get("completeness_score"),
            clarity_score=data.get("clarity_score"),
            format_compliance_score=data.get("format_compliance_score"),
            summary_feedback=data.get("summary_feedback", ""),
            detailed_feedback=data.get("detailed_feedback", ""),
            improvement_suggestions=data.get("improvement_suggestions", []),
            has_critical_errors=data.get("has_critical_errors", False),
            critical_error_details=data.get("critical_error_details"),
            recommended_action=data.get("recommended_action", "approve"),
            review_duration_minutes=data.get("review_duration_minutes"),
        )

        if data.get("started_at"):
            review.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            review.completed_at = datetime.fromisoformat(data["completed_at"])

        return review


@dataclass
class Submission:
    """A work product submitted by a contributor."""

    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""
    contributor_id: str = ""

    # Status
    status: SubmissionStatus = SubmissionStatus.DRAFT
    version: int = 1  # Increments on revision

    # Content
    content_type: str = ""  # scenario, golden_answer, rubric, etc.
    file_path: str = ""
    content_hash: Optional[str] = None  # SHA256 of content for integrity

    # Metadata
    title: str = ""
    description: str = ""
    notes: str = ""

    # Module Association
    eval_module: str = ""
    scenario_name: Optional[str] = None

    # Quality
    final_score: Optional[float] = None
    quality_tier: Optional[str] = None  # excellent, good, acceptable, poor

    # Reviews
    reviews: list[Review] = field(default_factory=list)
    current_reviewer_id: Optional[str] = None

    # Revision History
    revision_history: list[dict] = field(default_factory=list)
    previous_version_id: Optional[str] = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_approved(self) -> bool:
        """Check if submission is approved."""
        return self.status == SubmissionStatus.APPROVED

    @property
    def latest_review(self) -> Optional[Review]:
        """Get the most recent review."""
        if not self.reviews:
            return None
        return self.reviews[-1]

    @property
    def average_score(self) -> Optional[float]:
        """Calculate average score across all reviews."""
        if not self.reviews:
            return None
        scores = [r.overall_score for r in self.reviews if r.overall_score > 0]
        return sum(scores) / len(scores) if scores else None

    def submit(self) -> bool:
        """Submit for review."""
        if self.status not in (SubmissionStatus.DRAFT, SubmissionStatus.REVISED):
            return False

        self.status = SubmissionStatus.SUBMITTED
        self.submitted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return True

    def assign_reviewer(self, reviewer_id: str) -> bool:
        """Assign a reviewer."""
        if self.status != SubmissionStatus.SUBMITTED:
            return False

        self.current_reviewer_id = reviewer_id
        self.status = SubmissionStatus.IN_REVIEW
        self.updated_at = datetime.utcnow()
        return True

    def add_review(self, review: Review) -> None:
        """Add a review to this submission."""
        review.submission_id = self.id
        self.reviews.append(review)
        self.updated_at = datetime.utcnow()

    def approve(self, final_score: float) -> bool:
        """Approve the submission."""
        if self.status != SubmissionStatus.IN_REVIEW:
            return False

        self.status = SubmissionStatus.APPROVED
        self.final_score = final_score
        self.approved_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        # Assign quality tier
        if final_score >= 95:
            self.quality_tier = "excellent"
        elif final_score >= 85:
            self.quality_tier = "good"
        elif final_score >= 70:
            self.quality_tier = "acceptable"
        else:
            self.quality_tier = "poor"

        return True

    def request_revision(self) -> bool:
        """Request revision from contributor."""
        if self.status != SubmissionStatus.IN_REVIEW:
            return False

        self.status = SubmissionStatus.REVISION_REQUESTED
        self.updated_at = datetime.utcnow()
        return True

    def revise(self, new_file_path: str, notes: str = "") -> bool:
        """Submit a revised version."""
        if self.status != SubmissionStatus.REVISION_REQUESTED:
            return False

        # Store revision history
        self.revision_history.append({
            "version": self.version,
            "file_path": self.file_path,
            "revised_at": datetime.utcnow().isoformat(),
            "notes": notes,
        })

        self.file_path = new_file_path
        self.version += 1
        self.notes = notes
        self.status = SubmissionStatus.REVISED
        self.updated_at = datetime.utcnow()
        return True

    def reject(self) -> bool:
        """Reject the submission."""
        if self.status != SubmissionStatus.IN_REVIEW:
            return False

        self.status = SubmissionStatus.REJECTED
        self.updated_at = datetime.utcnow()
        return True

    def to_dict(self) -> dict:
        """Serialize submission to dictionary."""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "contributor_id": self.contributor_id,
            "status": self.status.value,
            "version": self.version,
            "content_type": self.content_type,
            "file_path": self.file_path,
            "content_hash": self.content_hash,
            "title": self.title,
            "description": self.description,
            "notes": self.notes,
            "eval_module": self.eval_module,
            "scenario_name": self.scenario_name,
            "final_score": self.final_score,
            "quality_tier": self.quality_tier,
            "reviews": [r.to_dict() for r in self.reviews],
            "current_reviewer_id": self.current_reviewer_id,
            "revision_history": self.revision_history,
            "previous_version_id": self.previous_version_id,
            "created_at": self.created_at.isoformat(),
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "updated_at": self.updated_at.isoformat(),
            "is_approved": self.is_approved,
            "average_score": self.average_score,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Submission":
        """Deserialize submission from dictionary."""
        submission = cls(
            id=data.get("id", str(uuid.uuid4())),
            task_id=data.get("task_id", ""),
            contributor_id=data.get("contributor_id", ""),
            status=SubmissionStatus(data.get("status", "draft")),
            version=data.get("version", 1),
            content_type=data.get("content_type", ""),
            file_path=data.get("file_path", ""),
            content_hash=data.get("content_hash"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            notes=data.get("notes", ""),
            eval_module=data.get("eval_module", ""),
            scenario_name=data.get("scenario_name"),
            final_score=data.get("final_score"),
            quality_tier=data.get("quality_tier"),
            reviews=[Review.from_dict(r) for r in data.get("reviews", [])],
            current_reviewer_id=data.get("current_reviewer_id"),
            revision_history=data.get("revision_history", []),
            previous_version_id=data.get("previous_version_id"),
        )

        for field_name in ["created_at", "submitted_at", "approved_at", "updated_at"]:
            if data.get(field_name):
                setattr(submission, field_name, datetime.fromisoformat(data[field_name]))

        return submission
