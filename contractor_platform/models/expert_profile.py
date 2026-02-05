"""
Expert profile model for detailed contractor vetting and matching.

Mirrors Mercor's approach of deep expert profiling for AI training work.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class VerificationStatus(Enum):
    """Verification status for credentials."""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class AvailabilityStatus(Enum):
    """Expert availability for new work."""
    AVAILABLE = "available"          # Ready for new tasks
    PARTIALLY_AVAILABLE = "partial"  # Limited capacity
    UNAVAILABLE = "unavailable"      # Not taking new work
    ON_PROJECT = "on_project"        # Committed to active project


@dataclass
class Credential:
    """Professional credential or certification."""
    type: str  # CFA, CPA, MD, PhD, JD, etc.
    issuer: str
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    verification_status: VerificationStatus = VerificationStatus.PENDING
    verification_url: Optional[str] = None  # Link to verify
    credential_id: Optional[str] = None


@dataclass
class WorkExperience:
    """Professional work experience entry."""
    title: str
    company: str
    industry: str
    start_date: str
    end_date: Optional[str] = None  # None = current
    description: str = ""
    is_buy_side: bool = False  # Hedge fund, asset manager
    is_sell_side: bool = False  # Investment bank, broker
    is_corporate: bool = False  # Corporate finance, IR
    aum_managed: Optional[str] = None  # Assets under management if applicable


@dataclass
class Education:
    """Educational background."""
    degree: str  # BS, MS, MBA, PhD, etc.
    field: str
    institution: str
    graduation_year: int
    gpa: Optional[float] = None
    honors: Optional[str] = None


@dataclass
class ExpertProfile:
    """
    Comprehensive expert profile for matching to AI training tasks.

    Designed for finance domain experts contributing to investment
    workflow evaluations and AI model training data.
    """

    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""  # Links to User model

    # Professional Identity
    full_name: str = ""
    headline: str = ""  # "Senior Equity Analyst | Healthcare | 12 Years"
    bio: str = ""
    location: str = ""
    timezone: str = ""

    # Contact & Links
    email: str = ""
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    personal_website: Optional[str] = None

    # Credentials
    credentials: list[Credential] = field(default_factory=list)

    # Experience
    work_experience: list[WorkExperience] = field(default_factory=list)
    total_years_experience: int = 0

    # Education
    education: list[Education] = field(default_factory=list)

    # Finance-Specific Expertise
    asset_classes: list[str] = field(default_factory=list)
    # Options: equities, fixed_income, derivatives, commodities, fx, crypto, alternatives

    sector_coverage: list[str] = field(default_factory=list)
    # Options: technology, healthcare, financials, industrials, consumer, energy,
    #          materials, utilities, real_estate, communication_services

    investment_styles: list[str] = field(default_factory=list)
    # Options: fundamental, quantitative, technical, event_driven, macro,
    #          long_short, long_only, activist, distressed

    modeling_skills: list[str] = field(default_factory=list)
    # Options: dcf, lbo, merger, sum_of_parts, monte_carlo, factor_models

    tools_proficiency: list[str] = field(default_factory=list)
    # Options: bloomberg, factset, capital_iq, pitchbook, excel, python, sql

    # AI Training Specific
    ai_training_experience: bool = False
    rlhf_experience: bool = False
    data_labeling_experience: bool = False
    rubric_creation_experience: bool = False
    evaluation_framework_experience: bool = False

    # Availability
    availability_status: AvailabilityStatus = AvailabilityStatus.AVAILABLE
    hours_per_week_available: int = 0
    preferred_task_types: list[str] = field(default_factory=list)
    minimum_hourly_rate: Optional[float] = None

    # Performance Metrics (populated from task history)
    tasks_completed: int = 0
    average_quality_score: float = 0.0
    on_time_delivery_rate: float = 100.0
    client_satisfaction_score: float = 0.0
    total_hours_worked: float = 0.0
    total_earnings: float = 0.0

    # Vetting Status
    is_vetted: bool = False
    vetting_date: Optional[datetime] = None
    vetting_score: Optional[float] = None  # AI interview score
    vetting_notes: str = ""

    # Resume
    resume_url: Optional[str] = None
    resume_parsed: bool = False

    # Video Interview (Mercor-style)
    video_interview_completed: bool = False
    video_interview_url: Optional[str] = None
    video_interview_score: Optional[float] = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_active_at: Optional[datetime] = None

    @property
    def is_fully_verified(self) -> bool:
        """Check if all credentials are verified."""
        if not self.credentials:
            return False
        return all(c.verification_status == VerificationStatus.VERIFIED
                   for c in self.credentials)

    @property
    def has_buy_side_experience(self) -> bool:
        """Check for buy-side experience (hedge funds, asset managers)."""
        return any(exp.is_buy_side for exp in self.work_experience)

    @property
    def has_sell_side_experience(self) -> bool:
        """Check for sell-side experience (investment banks)."""
        return any(exp.is_sell_side for exp in self.work_experience)

    @property
    def seniority_level(self) -> str:
        """Determine seniority based on experience."""
        if self.total_years_experience >= 15:
            return "principal"
        elif self.total_years_experience >= 10:
            return "senior"
        elif self.total_years_experience >= 5:
            return "mid"
        elif self.total_years_experience >= 2:
            return "junior"
        else:
            return "entry"

    @property
    def hourly_rate_tier(self) -> str:
        """Suggested hourly rate tier based on profile."""
        # Based on Mercor's $85-200/hr range for finance experts
        if self.is_fully_verified and self.total_years_experience >= 10:
            if any(c.type in ["CFA", "PhD"] for c in self.credentials):
                return "premium"  # $150-200/hr
        if self.total_years_experience >= 5 and self.has_buy_side_experience:
            return "standard"  # $100-150/hr
        return "base"  # $75-100/hr

    def matches_task_requirements(
        self,
        required_sectors: list[str] = None,
        required_skills: list[str] = None,
        required_credentials: list[str] = None,
        min_years_experience: int = 0,
    ) -> tuple[bool, float]:
        """
        Check if profile matches task requirements.

        Returns (matches, match_score) where match_score is 0-100.
        """
        score = 0
        max_score = 0

        # Sector match
        if required_sectors:
            max_score += 30
            matching = len(set(required_sectors) & set(self.sector_coverage))
            if matching > 0:
                score += (matching / len(required_sectors)) * 30

        # Skills match
        if required_skills:
            max_score += 30
            all_skills = self.modeling_skills + self.tools_proficiency
            matching = len(set(required_skills) & set(all_skills))
            if matching > 0:
                score += (matching / len(required_skills)) * 30

        # Credentials match
        if required_credentials:
            max_score += 20
            cred_types = [c.type for c in self.credentials]
            matching = len(set(required_credentials) & set(cred_types))
            if matching > 0:
                score += (matching / len(required_credentials)) * 20

        # Experience match
        if min_years_experience > 0:
            max_score += 20
            if self.total_years_experience >= min_years_experience:
                score += 20
            elif self.total_years_experience >= min_years_experience * 0.7:
                score += 10

        if max_score == 0:
            return True, 100.0

        match_score = (score / max_score) * 100
        matches = match_score >= 60  # 60% threshold

        return matches, match_score

    def to_dict(self) -> dict:
        """Serialize profile to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "headline": self.headline,
            "bio": self.bio,
            "location": self.location,
            "timezone": self.timezone,
            "credentials": [
                {
                    "type": c.type,
                    "issuer": c.issuer,
                    "verification_status": c.verification_status.value,
                }
                for c in self.credentials
            ],
            "total_years_experience": self.total_years_experience,
            "asset_classes": self.asset_classes,
            "sector_coverage": self.sector_coverage,
            "investment_styles": self.investment_styles,
            "modeling_skills": self.modeling_skills,
            "tools_proficiency": self.tools_proficiency,
            "availability_status": self.availability_status.value,
            "hours_per_week_available": self.hours_per_week_available,
            "tasks_completed": self.tasks_completed,
            "average_quality_score": self.average_quality_score,
            "on_time_delivery_rate": self.on_time_delivery_rate,
            "total_hours_worked": self.total_hours_worked,
            "total_earnings": self.total_earnings,
            "is_vetted": self.is_vetted,
            "vetting_score": self.vetting_score,
            "seniority_level": self.seniority_level,
            "hourly_rate_tier": self.hourly_rate_tier,
            "has_buy_side_experience": self.has_buy_side_experience,
            "is_fully_verified": self.is_fully_verified,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
