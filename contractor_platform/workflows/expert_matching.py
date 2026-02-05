"""
Expert matching system for task and project assignment.

Uses algorithmic matching similar to Mercor's approach to connect
domain experts with appropriate AI training tasks.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from ..models.expert_profile import ExpertProfile, AvailabilityStatus
from ..models.task import Task, TaskType
from ..models.project import Project, ProjectRequirements
from ..models.user import User, UserTier


@dataclass
class MatchResult:
    """Result of matching an expert to a task or project."""
    expert_id: str
    expert_name: str
    match_score: float  # 0-100
    match_reasons: list[str]
    hourly_rate: float
    availability: str
    quality_score: float
    tasks_completed: int


class ExpertMatcher:
    """
    Algorithmic expert matching for tasks and projects.

    Considers:
    - Domain expertise alignment
    - Credential requirements
    - Experience level
    - Quality track record
    - Availability
    - Rate compatibility
    """

    def __init__(self, data_dir: Path):
        """Initialize matcher with data directory."""
        self.data_dir = data_dir
        self.profiles_file = data_dir / "expert_profiles.json"
        self.users_file = data_dir / "users.json"
        self._ensure_data_files()

    def _ensure_data_files(self) -> None:
        """Ensure data files exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.profiles_file.exists():
            self._save_profiles([])

    def _load_profiles(self) -> list[ExpertProfile]:
        """Load all expert profiles."""
        with open(self.profiles_file) as f:
            data = json.load(f)
        # Simplified loading - in production would use proper deserialization
        return data

    def _save_profiles(self, profiles: list) -> None:
        """Save profiles to storage."""
        with open(self.profiles_file, "w") as f:
            json.dump(profiles, f, indent=2)

    def _load_users(self) -> list[User]:
        """Load all users."""
        if not self.users_file.exists():
            return []
        with open(self.users_file) as f:
            data = json.load(f)
        return [User.from_dict(u) for u in data]

    def find_experts_for_task(
        self,
        task: Task,
        limit: int = 10,
        min_match_score: float = 60.0,
    ) -> list[MatchResult]:
        """
        Find best-matched experts for a task.

        Args:
            task: The task to match experts for
            limit: Maximum number of matches to return
            min_match_score: Minimum match score threshold

        Returns:
            List of MatchResult sorted by match score (descending)
        """
        users = self._load_users()
        matches = []

        for user in users:
            if not user.is_active:
                continue

            # Check tier requirement
            tier_order = [UserTier.TRAINEE, UserTier.STANDARD, UserTier.SENIOR, UserTier.EXPERT]
            if tier_order.index(user.tier) < tier_order.index(task.min_tier):
                continue

            # Calculate match score
            score, reasons = self._calculate_task_match_score(user, task)

            if score >= min_match_score:
                # Calculate hourly rate based on task payment and estimated hours
                hourly_rate = task.calculate_payment(user.tier) / max(task.estimated_hours, 1)

                matches.append(MatchResult(
                    expert_id=user.id,
                    expert_name=user.name or user.email,
                    match_score=score,
                    match_reasons=reasons,
                    hourly_rate=hourly_rate,
                    availability="available",  # Would check real availability
                    quality_score=user.average_quality_score,
                    tasks_completed=user.approved_submissions,
                ))

        # Sort by match score, then quality score
        matches.sort(key=lambda m: (m.match_score, m.quality_score), reverse=True)

        return matches[:limit]

    def find_experts_for_project(
        self,
        project: Project,
        limit: int = 20,
        min_match_score: float = 70.0,
    ) -> list[MatchResult]:
        """
        Find best-matched experts for a project.

        Args:
            project: The project to match experts for
            limit: Maximum number of matches
            min_match_score: Minimum match score threshold

        Returns:
            List of MatchResult sorted by match score
        """
        users = self._load_users()
        requirements = project.requirements
        matches = []

        for user in users:
            if not user.is_active:
                continue

            # Check verification requirement
            if requirements.require_verified and not user.is_verified:
                continue

            # Check quality requirement
            if user.average_quality_score < requirements.min_quality_score:
                continue

            # Calculate match score
            score, reasons = self._calculate_project_match_score(user, project)

            if score >= min_match_score:
                # Estimate hourly rate based on tier
                base_rates = {
                    UserTier.TRAINEE: 50,
                    UserTier.STANDARD: 85,
                    UserTier.SENIOR: 120,
                    UserTier.EXPERT: 175,
                }
                hourly_rate = base_rates.get(user.tier, 85)

                # Cap at project rate cap
                hourly_rate = min(hourly_rate, project.hourly_rate_cap)

                matches.append(MatchResult(
                    expert_id=user.id,
                    expert_name=user.name or user.email,
                    match_score=score,
                    match_reasons=reasons,
                    hourly_rate=hourly_rate,
                    availability="available",
                    quality_score=user.average_quality_score,
                    tasks_completed=user.approved_submissions,
                ))

        # Sort by match score, then quality
        matches.sort(key=lambda m: (m.match_score, m.quality_score), reverse=True)

        return matches[:limit]

    def _calculate_task_match_score(
        self,
        user: User,
        task: Task,
    ) -> tuple[float, list[str]]:
        """Calculate match score for a user-task pair."""
        score = 50.0  # Base score
        reasons = []

        # Expertise match (up to +30)
        if task.required_expertise:
            matching_expertise = [e for e in task.required_expertise if e in user.expertise]
            if matching_expertise:
                expertise_bonus = (len(matching_expertise) / len(task.required_expertise)) * 30
                score += expertise_bonus
                reasons.append(f"Expertise match: {len(matching_expertise)}/{len(task.required_expertise)}")

        # Quality score bonus (up to +15)
        if user.average_quality_score >= 95:
            score += 15
            reasons.append("Excellent quality track record")
        elif user.average_quality_score >= 85:
            score += 10
            reasons.append("Strong quality track record")
        elif user.average_quality_score >= 70:
            score += 5

        # Experience bonus (up to +10)
        if user.approved_submissions >= 50:
            score += 10
            reasons.append("Highly experienced contributor")
        elif user.approved_submissions >= 20:
            score += 7
            reasons.append("Experienced contributor")
        elif user.approved_submissions >= 5:
            score += 3

        # Tier bonus (up to +10)
        tier_bonuses = {
            UserTier.EXPERT: 10,
            UserTier.SENIOR: 7,
            UserTier.STANDARD: 3,
            UserTier.TRAINEE: 0,
        }
        tier_bonus = tier_bonuses.get(user.tier, 0)
        if tier_bonus > 0:
            score += tier_bonus
            reasons.append(f"{user.tier.value.title()} tier")

        # Verification bonus
        if user.is_verified:
            score += 5
            reasons.append("Verified expert")

        return min(score, 100.0), reasons

    def _calculate_project_match_score(
        self,
        user: User,
        project: Project,
    ) -> tuple[float, list[str]]:
        """Calculate match score for a user-project pair."""
        score = 40.0  # Base score
        reasons = []
        requirements = project.requirements

        # Experience requirement
        if user.years_experience >= requirements.min_years_experience:
            score += 15
            reasons.append(f"Meets experience requirement ({user.years_experience}+ years)")
        elif user.years_experience >= requirements.min_years_experience * 0.7:
            score += 7

        # Credential match
        if requirements.required_credentials:
            user_creds = user.certifications
            matching = len(set(requirements.required_credentials) & set(user_creds))
            if matching > 0:
                cred_bonus = (matching / len(requirements.required_credentials)) * 20
                score += cred_bonus
                reasons.append(f"Credential match: {matching}/{len(requirements.required_credentials)}")

        # Quality score
        quality_delta = user.average_quality_score - requirements.min_quality_score
        if quality_delta >= 10:
            score += 15
            reasons.append("Exceeds quality requirements")
        elif quality_delta >= 5:
            score += 10
        elif quality_delta >= 0:
            score += 5

        # Tier bonus
        tier_bonuses = {
            UserTier.EXPERT: 10,
            UserTier.SENIOR: 7,
            UserTier.STANDARD: 3,
        }
        score += tier_bonuses.get(user.tier, 0)

        # Verification
        if requirements.require_verified and user.is_verified:
            score += 5
            reasons.append("Verified credentials")

        return min(score, 100.0), reasons

    def auto_assign_task(
        self,
        task: Task,
        prefer_quality: bool = True,
    ) -> Optional[str]:
        """
        Automatically assign the best-matched expert to a task.

        Args:
            task: Task to assign
            prefer_quality: If True, prioritize quality over match score

        Returns:
            Expert ID if assigned, None if no suitable expert found
        """
        matches = self.find_experts_for_task(task, limit=5)

        if not matches:
            return None

        if prefer_quality:
            # Sort by quality score first
            matches.sort(key=lambda m: m.quality_score, reverse=True)

        return matches[0].expert_id

    def get_expert_recommendations(
        self,
        expert_id: str,
        limit: int = 5,
    ) -> list[dict]:
        """
        Get task recommendations for an expert based on their profile.

        Returns tasks that best match the expert's skills and preferences.
        """
        # This would load available tasks and score them for the expert
        # Simplified implementation
        return []


class QualityTracker:
    """
    Track and analyze expert quality metrics.

    Used for tier promotion decisions and client reporting.
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def calculate_promotion_eligibility(self, user: User) -> dict:
        """
        Check if user is eligible for tier promotion.

        Returns eligibility status and requirements.
        """
        current_tier = user.tier
        next_tier = self._get_next_tier(current_tier)

        if next_tier is None:
            return {
                "eligible": False,
                "current_tier": current_tier.value,
                "next_tier": None,
                "reason": "Already at highest tier",
            }

        requirements = {
            UserTier.STANDARD: {"min_score": 70, "min_submissions": 5},
            UserTier.SENIOR: {"min_score": 85, "min_submissions": 20},
            UserTier.EXPERT: {"min_score": 95, "min_submissions": 50},
        }

        req = requirements.get(next_tier, {})
        min_score = req.get("min_score", 0)
        min_submissions = req.get("min_submissions", 0)

        meets_score = user.average_quality_score >= min_score
        meets_submissions = user.approved_submissions >= min_submissions

        return {
            "eligible": meets_score and meets_submissions,
            "current_tier": current_tier.value,
            "next_tier": next_tier.value,
            "quality_score": user.average_quality_score,
            "required_score": min_score,
            "meets_score": meets_score,
            "submissions": user.approved_submissions,
            "required_submissions": min_submissions,
            "meets_submissions": meets_submissions,
        }

    def _get_next_tier(self, current: UserTier) -> Optional[UserTier]:
        """Get next tier above current."""
        progression = [UserTier.TRAINEE, UserTier.STANDARD, UserTier.SENIOR, UserTier.EXPERT]
        try:
            idx = progression.index(current)
            if idx < len(progression) - 1:
                return progression[idx + 1]
        except ValueError:
            pass
        return None

    def generate_quality_report(self, user_id: str) -> dict:
        """Generate detailed quality report for an expert."""
        # Would aggregate metrics from submissions
        return {
            "user_id": user_id,
            "report_date": datetime.utcnow().isoformat(),
            "metrics": {
                "overall_quality": 0.0,
                "by_dimension": {},
                "trend": "stable",
            },
            "recommendations": [],
        }
