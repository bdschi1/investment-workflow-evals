"""Review workflow for QA and approval of submissions."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..models.task import Task, TaskStatus
from ..models.submission import Submission, SubmissionStatus, Review
from ..models.user import User, UserTier


class ReviewWorkflow:
    """Manages the review and QA process for submissions."""

    def __init__(self, data_dir: Path):
        """Initialize review workflow with data directory."""
        self.data_dir = data_dir
        self.submissions_file = data_dir / "submissions.json"
        self.tasks_file = data_dir / "tasks.json"
        self.users_file = data_dir / "users.json"
        self._ensure_data_files()

    def _ensure_data_files(self) -> None:
        """Ensure data files exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.submissions_file.exists():
            self._save_submissions([])

    def _load_submissions(self) -> list[Submission]:
        """Load all submissions from storage."""
        with open(self.submissions_file, "r") as f:
            data = json.load(f)
        return [Submission.from_dict(s) for s in data]

    def _save_submissions(self, submissions: list[Submission]) -> None:
        """Save all submissions to storage."""
        with open(self.submissions_file, "w") as f:
            json.dump([s.to_dict() for s in submissions], f, indent=2)

    def _load_tasks(self) -> list[Task]:
        """Load all tasks from storage."""
        with open(self.tasks_file, "r") as f:
            data = json.load(f)
        return [Task.from_dict(t) for t in data]

    def _save_tasks(self, tasks: list[Task]) -> None:
        """Save all tasks to storage."""
        with open(self.tasks_file, "w") as f:
            json.dump([t.to_dict() for t in tasks], f, indent=2)

    def _load_users(self) -> list[User]:
        """Load all users from storage."""
        with open(self.users_file, "r") as f:
            data = json.load(f)
        return [User.from_dict(u) for u in data]

    def _save_users(self, users: list[User]) -> None:
        """Save all users to storage."""
        with open(self.users_file, "w") as f:
            json.dump([u.to_dict() for u in users], f, indent=2)

    def get_submission(self, submission_id: str) -> Optional[Submission]:
        """Get a submission by ID."""
        submissions = self._load_submissions()
        for submission in submissions:
            if submission.id == submission_id:
                return submission
        return None

    def create_submission(
        self,
        task_id: str,
        contributor_id: str,
        file_path: str,
        content_type: str,
        title: str = "",
        description: str = "",
        notes: str = "",
    ) -> Submission:
        """Create a new submission for a task."""
        submission = Submission(
            task_id=task_id,
            contributor_id=contributor_id,
            file_path=file_path,
            content_type=content_type,
            title=title,
            description=description,
            notes=notes,
            status=SubmissionStatus.DRAFT,
        )

        submissions = self._load_submissions()
        submissions.append(submission)
        self._save_submissions(submissions)

        return submission

    def submit_for_review(self, submission_id: str) -> tuple[bool, str]:
        """Submit a draft for review."""
        submission = self.get_submission(submission_id)
        if not submission:
            return False, "Submission not found"

        success = submission.submit()
        if success:
            submissions = self._load_submissions()
            submissions = [s if s.id != submission_id else submission for s in submissions]
            self._save_submissions(submissions)
            return True, "Submitted for review"

        return False, f"Cannot submit from status: {submission.status.value}"

    def get_submissions_pending_review(self) -> list[Submission]:
        """Get all submissions awaiting review."""
        submissions = self._load_submissions()
        return [s for s in submissions if s.status == SubmissionStatus.SUBMITTED]

    def get_submissions_for_reviewer(self, reviewer_id: str) -> list[Submission]:
        """Get submissions assigned to a reviewer."""
        submissions = self._load_submissions()
        return [s for s in submissions if s.current_reviewer_id == reviewer_id]

    def assign_reviewer(
        self,
        submission_id: str,
        reviewer_id: str,
    ) -> tuple[bool, str]:
        """Assign a reviewer to a submission."""
        submission = self.get_submission(submission_id)
        if not submission:
            return False, "Submission not found"

        # Verify reviewer has permission
        users = self._load_users()
        reviewer = next((u for u in users if u.id == reviewer_id), None)
        if not reviewer:
            return False, "Reviewer not found"

        if not reviewer.tier.can_review:
            return False, f"User tier {reviewer.tier.value} cannot review submissions"

        # Prevent self-review
        if submission.contributor_id == reviewer_id:
            return False, "Cannot review your own submission"

        success = submission.assign_reviewer(reviewer_id)
        if success:
            submissions = self._load_submissions()
            submissions = [s if s.id != submission_id else submission for s in submissions]
            self._save_submissions(submissions)
            return True, f"Reviewer {reviewer_id} assigned"

        return False, f"Cannot assign reviewer in status: {submission.status.value}"

    def auto_assign_reviewer(self, submission_id: str) -> tuple[bool, str]:
        """Automatically assign a qualified reviewer."""
        submission = self.get_submission(submission_id)
        if not submission:
            return False, "Submission not found"

        users = self._load_users()

        # Find eligible reviewers
        eligible = []
        for user in users:
            if not user.tier.can_review:
                continue
            if user.id == submission.contributor_id:
                continue
            if not user.is_active:
                continue

            # Calculate workload (submissions currently assigned)
            current_assignments = len(self.get_submissions_for_reviewer(user.id))

            eligible.append((user, current_assignments))

        if not eligible:
            return False, "No eligible reviewers available"

        # Sort by workload (ascending) then by tier (descending)
        tier_rank = {UserTier.EXPERT: 3, UserTier.SENIOR: 2, UserTier.ADMIN: 1}
        eligible.sort(key=lambda x: (x[1], -tier_rank.get(x[0].tier, 0)))

        # Assign to least busy eligible reviewer
        selected_reviewer = eligible[0][0]
        return self.assign_reviewer(submission_id, selected_reviewer.id)

    def start_review(self, submission_id: str, reviewer_id: str) -> Review:
        """Start a review session."""
        review = Review(
            submission_id=submission_id,
            reviewer_id=reviewer_id,
            started_at=datetime.utcnow(),
        )
        return review

    def complete_review(
        self,
        submission_id: str,
        review: Review,
        action: str,  # "approve", "revise", "reject"
    ) -> tuple[bool, str]:
        """Complete a review with a decision."""
        submission = self.get_submission(submission_id)
        if not submission:
            return False, "Submission not found"

        if submission.status != SubmissionStatus.IN_REVIEW:
            return False, f"Submission is not in review (status: {submission.status.value})"

        # Complete the review
        review.complete()
        submission.add_review(review)

        # Apply decision
        if action == "approve":
            submission.approve(review.overall_score)

            # Update task status
            self._update_task_status(
                submission.task_id,
                TaskStatus.APPROVED,
                review.overall_score,
                review.summary_feedback,
            )

            # Update contributor stats
            self._update_contributor_stats(
                submission.contributor_id,
                review.overall_score,
                approved=True,
            )

        elif action == "revise":
            if not submission.request_revision():
                return False, "Maximum revisions exceeded"

            self._update_task_status(
                submission.task_id,
                TaskStatus.REVISION,
                feedback=review.summary_feedback,
            )

        elif action == "reject":
            submission.reject()

            self._update_task_status(
                submission.task_id,
                TaskStatus.REJECTED,
                feedback=review.summary_feedback,
            )

            self._update_contributor_stats(
                submission.contributor_id,
                review.overall_score,
                approved=False,
            )

        else:
            return False, f"Invalid action: {action}"

        # Save submission
        submissions = self._load_submissions()
        submissions = [s if s.id != submission_id else submission for s in submissions]
        self._save_submissions(submissions)

        # Update reviewer stats
        self._update_reviewer_stats(review.reviewer_id)

        return True, f"Review completed: {action}"

    def _update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        score: Optional[float] = None,
        feedback: Optional[str] = None,
    ) -> None:
        """Update the associated task status."""
        tasks = self._load_tasks()
        for task in tasks:
            if task.id == task_id:
                task.status = status
                if score is not None:
                    task.review_score = score
                if feedback is not None:
                    task.review_feedback = feedback
                task.reviewed_at = datetime.utcnow()
                task.updated_at = datetime.utcnow()
                break
        self._save_tasks(tasks)

    def _update_contributor_stats(
        self,
        contributor_id: str,
        score: float,
        approved: bool,
    ) -> None:
        """Update contributor statistics after review."""
        users = self._load_users()
        for user in users:
            if user.id == contributor_id:
                user.update_stats(score, approved)
                break
        self._save_users(users)

    def _update_reviewer_stats(self, reviewer_id: str) -> None:
        """Update reviewer statistics."""
        users = self._load_users()
        for user in users:
            if user.id == reviewer_id:
                user.total_reviews += 1
                user.last_active_at = datetime.utcnow()
                break
        self._save_users(users)

    def get_review_statistics(self) -> dict:
        """Get platform review statistics."""
        submissions = self._load_submissions()

        stats = {
            "total_submissions": len(submissions),
            "by_status": {},
            "pending_review": 0,
            "avg_score": 0.0,
            "approval_rate": 0.0,
            "avg_review_time_minutes": 0.0,
        }

        scores = []
        review_times = []
        approved_count = 0
        completed_count = 0

        for submission in submissions:
            status = submission.status.value
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            if submission.status == SubmissionStatus.SUBMITTED:
                stats["pending_review"] += 1

            if submission.final_score is not None:
                scores.append(submission.final_score)

            if submission.status == SubmissionStatus.APPROVED:
                approved_count += 1
                completed_count += 1
            elif submission.status == SubmissionStatus.REJECTED:
                completed_count += 1

            for review in submission.reviews:
                if review.review_duration_minutes:
                    review_times.append(review.review_duration_minutes)

        if scores:
            stats["avg_score"] = sum(scores) / len(scores)

        if completed_count > 0:
            stats["approval_rate"] = (approved_count / completed_count) * 100

        if review_times:
            stats["avg_review_time_minutes"] = sum(review_times) / len(review_times)

        return stats


class QualityScorer:
    """Scoring utilities for evaluating submission quality."""

    # Dimension weights for different content types
    WEIGHTS = {
        "scenario": {
            "completeness": 0.25,
            "clarity": 0.20,
            "accuracy": 0.25,
            "difficulty_appropriateness": 0.15,
            "format_compliance": 0.15,
        },
        "golden_answer": {
            "factual_accuracy": 0.30,
            "analytical_rigor": 0.25,
            "completeness": 0.20,
            "clarity": 0.15,
            "format_compliance": 0.10,
        },
        "rubric": {
            "dimension_coverage": 0.25,
            "criteria_clarity": 0.25,
            "anchor_quality": 0.20,
            "weighting_logic": 0.15,
            "format_compliance": 0.15,
        },
        "adversarial_test": {
            "failure_mode_targeting": 0.30,
            "difficulty": 0.25,
            "clarity": 0.20,
            "realism": 0.15,
            "format_compliance": 0.10,
        },
    }

    @classmethod
    def calculate_weighted_score(
        cls,
        content_type: str,
        dimension_scores: dict[str, float],
    ) -> float:
        """Calculate weighted overall score from dimension scores."""
        weights = cls.WEIGHTS.get(content_type, {})

        if not weights:
            # Default equal weighting
            if dimension_scores:
                return sum(dimension_scores.values()) / len(dimension_scores)
            return 0.0

        total_score = 0.0
        total_weight = 0.0

        for dimension, weight in weights.items():
            if dimension in dimension_scores:
                total_score += dimension_scores[dimension] * weight
                total_weight += weight

        if total_weight == 0:
            return 0.0

        return total_score / total_weight * 100  # Normalize to 0-100

    @classmethod
    def get_quality_tier(cls, score: float) -> str:
        """Determine quality tier from score."""
        if score >= 95:
            return "excellent"
        elif score >= 85:
            return "good"
        elif score >= 70:
            return "acceptable"
        else:
            return "poor"

    @classmethod
    def check_critical_failures(
        cls,
        content_type: str,
        content: dict,
    ) -> list[str]:
        """Check for critical failure conditions."""
        failures = []

        if content_type == "golden_answer":
            # Check for hallucinated data
            if not content.get("sources"):
                failures.append("No sources cited")

            # Check for missing risk section
            if not content.get("risks"):
                failures.append("No risks identified")

            # Check for missing recommendation
            if not content.get("recommendation"):
                failures.append("No clear recommendation")

        elif content_type == "scenario":
            # Check for missing context
            if not content.get("context"):
                failures.append("No scenario context provided")

            # Check for missing data sources
            if not content.get("data_sources"):
                failures.append("No data sources specified")

        return failures
