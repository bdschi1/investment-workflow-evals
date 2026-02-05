"""User model for domain expert contributors."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class UserTier(Enum):
    """Contributor quality tiers based on performance."""

    TRAINEE = "trainee"      # New contributor, training tasks only
    STANDARD = "standard"    # 70%+ quality, 5+ approved submissions
    SENIOR = "senior"        # 85%+ quality, 20+ approved submissions
    EXPERT = "expert"        # 95%+ quality, 50+ approved submissions
    ADMIN = "admin"          # Platform administrator

    @property
    def rate_multiplier(self) -> float:
        """Payment rate multiplier for this tier."""
        multipliers = {
            UserTier.TRAINEE: 0.5,
            UserTier.STANDARD: 1.0,
            UserTier.SENIOR: 1.25,
            UserTier.EXPERT: 1.5,
            UserTier.ADMIN: 1.0,
        }
        return multipliers[self]

    @property
    def can_review(self) -> bool:
        """Whether this tier can review submissions."""
        return self in (UserTier.SENIOR, UserTier.EXPERT, UserTier.ADMIN)

    @property
    def min_quality_score(self) -> float:
        """Minimum quality score required for this tier."""
        scores = {
            UserTier.TRAINEE: 0.0,
            UserTier.STANDARD: 70.0,
            UserTier.SENIOR: 85.0,
            UserTier.EXPERT: 95.0,
            UserTier.ADMIN: 0.0,
        }
        return scores[self]

    @property
    def min_approved_submissions(self) -> int:
        """Minimum approved submissions required for this tier."""
        counts = {
            UserTier.TRAINEE: 0,
            UserTier.STANDARD: 5,
            UserTier.SENIOR: 20,
            UserTier.EXPERT: 50,
            UserTier.ADMIN: 0,
        }
        return counts[self]


class Expertise(Enum):
    """Domain expertise areas for task matching."""

    # Investment Research
    EQUITY_RESEARCH = "equity_research"
    FIXED_INCOME = "fixed_income"
    DERIVATIVES = "derivatives"
    COMMODITIES = "commodities"
    FX = "fx"

    # Valuation
    DCF_VALUATION = "dcf_valuation"
    COMPARABLE_ANALYSIS = "comparable_analysis"
    LBO_MODELING = "lbo_modeling"
    MERGER_MODELING = "merger_modeling"

    # Portfolio Management
    PORTFOLIO_CONSTRUCTION = "portfolio_construction"
    RISK_MANAGEMENT = "risk_management"
    FACTOR_INVESTING = "factor_investing"
    QUANTITATIVE_STRATEGIES = "quantitative_strategies"

    # Sector Expertise
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCIALS = "financials"
    INDUSTRIALS = "industrials"
    CONSUMER = "consumer"
    ENERGY = "energy"
    REAL_ESTATE = "real_estate"

    # Special Areas
    ESG = "esg"
    PRIVATE_MARKETS = "private_markets"
    CREDIT_ANALYSIS = "credit_analysis"
    MACRO_ECONOMICS = "macro_economics"


@dataclass
class User:
    """Domain expert contributor on the platform."""

    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    email: str = ""
    name: str = ""

    # Professional Profile
    title: str = ""
    organization: str = ""
    years_experience: int = 0
    certifications: list[str] = field(default_factory=list)  # CFA, FRM, etc.
    expertise: list[Expertise] = field(default_factory=list)
    bio: str = ""
    linkedin_url: Optional[str] = None

    # Platform Status
    tier: UserTier = UserTier.TRAINEE
    is_active: bool = True
    is_verified: bool = False

    # Performance Metrics
    total_submissions: int = 0
    approved_submissions: int = 0
    rejected_submissions: int = 0
    total_reviews: int = 0
    average_quality_score: float = 0.0

    # Financials
    total_earnings: float = 0.0
    pending_earnings: float = 0.0

    # Payment Info (stored securely, references only)
    payment_method_id: Optional[str] = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_active_at: Optional[datetime] = None

    # Onboarding
    onboarding_completed: bool = False
    qualification_test_passed: bool = False
    qualification_score: Optional[float] = None

    @property
    def approval_rate(self) -> float:
        """Calculate submission approval rate."""
        if self.total_submissions == 0:
            return 0.0
        return (self.approved_submissions / self.total_submissions) * 100

    @property
    def eligible_for_upgrade(self) -> bool:
        """Check if user is eligible for tier upgrade."""
        next_tier = self._get_next_tier()
        if next_tier is None:
            return False

        return (
            self.average_quality_score >= next_tier.min_quality_score
            and self.approved_submissions >= next_tier.min_approved_submissions
        )

    def _get_next_tier(self) -> Optional[UserTier]:
        """Get the next tier above current."""
        tier_order = [UserTier.TRAINEE, UserTier.STANDARD, UserTier.SENIOR, UserTier.EXPERT]
        try:
            current_idx = tier_order.index(self.tier)
            if current_idx < len(tier_order) - 1:
                return tier_order[current_idx + 1]
        except ValueError:
            pass
        return None

    def has_expertise(self, required: list[Expertise]) -> bool:
        """Check if user has any of the required expertise areas."""
        if not required:
            return True
        return any(exp in self.expertise for exp in required)

    def update_stats(self, quality_score: float, approved: bool) -> None:
        """Update user statistics after a submission is reviewed."""
        self.total_submissions += 1

        if approved:
            self.approved_submissions += 1
        else:
            self.rejected_submissions += 1

        # Update rolling average quality score
        if self.average_quality_score == 0:
            self.average_quality_score = quality_score
        else:
            # Weighted average favoring recent submissions
            weight = min(0.3, 1.0 / self.total_submissions)
            self.average_quality_score = (
                (1 - weight) * self.average_quality_score + weight * quality_score
            )

        self.updated_at = datetime.utcnow()
        self.last_active_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Serialize user to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "title": self.title,
            "organization": self.organization,
            "years_experience": self.years_experience,
            "certifications": self.certifications,
            "expertise": [e.value for e in self.expertise],
            "bio": self.bio,
            "linkedin_url": self.linkedin_url,
            "tier": self.tier.value,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "total_submissions": self.total_submissions,
            "approved_submissions": self.approved_submissions,
            "rejected_submissions": self.rejected_submissions,
            "total_reviews": self.total_reviews,
            "average_quality_score": self.average_quality_score,
            "approval_rate": self.approval_rate,
            "total_earnings": self.total_earnings,
            "pending_earnings": self.pending_earnings,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_active_at": self.last_active_at.isoformat() if self.last_active_at else None,
            "onboarding_completed": self.onboarding_completed,
            "qualification_test_passed": self.qualification_test_passed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Deserialize user from dictionary."""
        user = cls(
            id=data.get("id", str(uuid.uuid4())),
            email=data.get("email", ""),
            name=data.get("name", ""),
            title=data.get("title", ""),
            organization=data.get("organization", ""),
            years_experience=data.get("years_experience", 0),
            certifications=data.get("certifications", []),
            expertise=[Expertise(e) for e in data.get("expertise", [])],
            bio=data.get("bio", ""),
            linkedin_url=data.get("linkedin_url"),
            tier=UserTier(data.get("tier", "trainee")),
            is_active=data.get("is_active", True),
            is_verified=data.get("is_verified", False),
            total_submissions=data.get("total_submissions", 0),
            approved_submissions=data.get("approved_submissions", 0),
            rejected_submissions=data.get("rejected_submissions", 0),
            total_reviews=data.get("total_reviews", 0),
            average_quality_score=data.get("average_quality_score", 0.0),
            total_earnings=data.get("total_earnings", 0.0),
            pending_earnings=data.get("pending_earnings", 0.0),
            onboarding_completed=data.get("onboarding_completed", False),
            qualification_test_passed=data.get("qualification_test_passed", False),
            qualification_score=data.get("qualification_score"),
        )

        if data.get("created_at"):
            user.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            user.updated_at = datetime.fromisoformat(data["updated_at"])
        if data.get("last_active_at"):
            user.last_active_at = datetime.fromisoformat(data["last_active_at"])

        return user
