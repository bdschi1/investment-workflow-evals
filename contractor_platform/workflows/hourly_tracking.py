"""
Hourly time tracking for contract work.

Enables accurate time-based billing for AI training tasks,
matching Mercor's hourly rate model ($85-200/hr for experts).
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid


class TimeEntryStatus(Enum):
    """Status of a time entry."""
    DRAFT = "draft"          # Not yet submitted
    SUBMITTED = "submitted"  # Awaiting approval
    APPROVED = "approved"    # Approved for payment
    REJECTED = "rejected"    # Rejected, needs revision
    PAID = "paid"            # Payment processed


@dataclass
class TimeEntry:
    """A single time tracking entry."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    expert_id: str = ""
    task_id: Optional[str] = None
    project_id: Optional[str] = None

    # Time
    date: str = ""  # YYYY-MM-DD
    start_time: Optional[str] = None  # HH:MM
    end_time: Optional[str] = None    # HH:MM
    duration_hours: float = 0.0

    # Description
    description: str = ""
    work_type: str = ""  # scenario_creation, golden_answer, review, etc.

    # Billing
    hourly_rate: float = 0.0
    total_amount: float = 0.0

    # Status
    status: TimeEntryStatus = TimeEntryStatus.DRAFT

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None

    def calculate_duration(self) -> float:
        """Calculate duration from start/end times."""
        if not self.start_time or not self.end_time:
            return self.duration_hours

        start = datetime.strptime(self.start_time, "%H:%M")
        end = datetime.strptime(self.end_time, "%H:%M")
        delta = end - start
        return delta.total_seconds() / 3600

    def calculate_total(self) -> float:
        """Calculate total amount for this entry."""
        return self.duration_hours * self.hourly_rate

    def submit(self) -> bool:
        """Submit for approval."""
        if self.status != TimeEntryStatus.DRAFT:
            return False

        self.total_amount = self.calculate_total()
        self.status = TimeEntryStatus.SUBMITTED
        self.submitted_at = datetime.utcnow()
        return True

    def approve(self, approver_id: str) -> bool:
        """Approve the time entry."""
        if self.status != TimeEntryStatus.SUBMITTED:
            return False

        self.status = TimeEntryStatus.APPROVED
        self.approved_at = datetime.utcnow()
        self.approved_by = approver_id
        return True

    def reject(self, reason: str = "") -> bool:
        """Reject the time entry."""
        if self.status != TimeEntryStatus.SUBMITTED:
            return False

        self.status = TimeEntryStatus.REJECTED
        return True

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "expert_id": self.expert_id,
            "task_id": self.task_id,
            "project_id": self.project_id,
            "date": self.date,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_hours": self.duration_hours,
            "description": self.description,
            "work_type": self.work_type,
            "hourly_rate": self.hourly_rate,
            "total_amount": self.total_amount,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "approved_by": self.approved_by,
        }


@dataclass
class Timesheet:
    """Weekly timesheet for an expert."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    expert_id: str = ""
    week_start: str = ""  # Monday of the week (YYYY-MM-DD)
    week_end: str = ""    # Sunday of the week

    entries: list[TimeEntry] = field(default_factory=list)

    # Totals
    total_hours: float = 0.0
    total_amount: float = 0.0

    # Status
    status: TimeEntryStatus = TimeEntryStatus.DRAFT
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None

    def add_entry(self, entry: TimeEntry) -> None:
        """Add a time entry to the timesheet."""
        entry.expert_id = self.expert_id
        self.entries.append(entry)
        self._recalculate_totals()

    def _recalculate_totals(self) -> None:
        """Recalculate total hours and amount."""
        self.total_hours = sum(e.duration_hours for e in self.entries)
        self.total_amount = sum(e.total_amount for e in self.entries)

    def submit(self) -> bool:
        """Submit timesheet for approval."""
        if self.status != TimeEntryStatus.DRAFT:
            return False

        # Submit all entries
        for entry in self.entries:
            if entry.status == TimeEntryStatus.DRAFT:
                entry.submit()

        self.status = TimeEntryStatus.SUBMITTED
        self.submitted_at = datetime.utcnow()
        self._recalculate_totals()
        return True

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "expert_id": self.expert_id,
            "week_start": self.week_start,
            "week_end": self.week_end,
            "entries": [e.to_dict() for e in self.entries],
            "total_hours": self.total_hours,
            "total_amount": self.total_amount,
            "status": self.status.value,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
        }


class TimeTracker:
    """
    Manages time tracking for experts.

    Supports:
    - Individual time entries
    - Weekly timesheets
    - Approval workflows
    - Billing reports
    """

    # Standard hourly rates by tier (aligned with Mercor's $85-200 range)
    HOURLY_RATES = {
        "trainee": 50.0,
        "standard": 85.0,
        "senior": 125.0,
        "expert": 175.0,
    }

    # Premium rates for specialized work
    PREMIUM_RATES = {
        "red_teaming": 1.25,      # 25% premium
        "expert_audit": 1.20,     # 20% premium
        "rush_delivery": 1.30,    # 30% premium
    }

    def __init__(self, data_dir: Path):
        """Initialize time tracker."""
        self.data_dir = data_dir
        self.entries_file = data_dir / "time_entries.json"
        self.timesheets_file = data_dir / "timesheets.json"
        self._ensure_data_files()

    def _ensure_data_files(self) -> None:
        """Ensure data files exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.entries_file.exists():
            self._save_entries([])
        if not self.timesheets_file.exists():
            self._save_timesheets([])

    def _load_entries(self) -> list[dict]:
        """Load all time entries."""
        with open(self.entries_file) as f:
            return json.load(f)

    def _save_entries(self, entries: list[dict]) -> None:
        """Save time entries."""
        with open(self.entries_file, "w") as f:
            json.dump(entries, f, indent=2)

    def _load_timesheets(self) -> list[dict]:
        """Load all timesheets."""
        with open(self.timesheets_file) as f:
            return json.load(f)

    def _save_timesheets(self, timesheets: list[dict]) -> None:
        """Save timesheets."""
        with open(self.timesheets_file, "w") as f:
            json.dump(timesheets, f, indent=2)

    def get_hourly_rate(
        self,
        tier: str,
        work_type: str = None,
        is_rush: bool = False,
    ) -> float:
        """
        Calculate hourly rate for an expert.

        Args:
            tier: Expert tier (trainee, standard, senior, expert)
            work_type: Type of work (may have premium)
            is_rush: Whether this is rush delivery

        Returns:
            Hourly rate in USD
        """
        base_rate = self.HOURLY_RATES.get(tier, 85.0)

        # Apply work type premium
        if work_type and work_type in self.PREMIUM_RATES:
            base_rate *= self.PREMIUM_RATES[work_type]

        # Apply rush premium
        if is_rush:
            base_rate *= self.PREMIUM_RATES.get("rush_delivery", 1.0)

        return round(base_rate, 2)

    def log_time(
        self,
        expert_id: str,
        duration_hours: float,
        description: str,
        work_type: str,
        task_id: str = None,
        project_id: str = None,
        hourly_rate: float = None,
        date: str = None,
    ) -> TimeEntry:
        """
        Log time worked.

        Args:
            expert_id: ID of the expert
            duration_hours: Hours worked
            description: Description of work done
            work_type: Type of work
            task_id: Associated task ID
            project_id: Associated project ID
            hourly_rate: Override hourly rate (uses tier rate if not provided)
            date: Date of work (defaults to today)

        Returns:
            Created TimeEntry
        """
        entry = TimeEntry(
            expert_id=expert_id,
            task_id=task_id,
            project_id=project_id,
            date=date or datetime.utcnow().strftime("%Y-%m-%d"),
            duration_hours=duration_hours,
            description=description,
            work_type=work_type,
            hourly_rate=hourly_rate or self.HOURLY_RATES.get("standard", 85.0),
        )
        entry.total_amount = entry.calculate_total()

        # Save entry
        entries = self._load_entries()
        entries.append(entry.to_dict())
        self._save_entries(entries)

        return entry

    def get_expert_entries(
        self,
        expert_id: str,
        start_date: str = None,
        end_date: str = None,
        status: TimeEntryStatus = None,
    ) -> list[dict]:
        """Get time entries for an expert."""
        entries = self._load_entries()

        filtered = [
            e for e in entries
            if e["expert_id"] == expert_id
        ]

        if start_date:
            filtered = [e for e in filtered if e["date"] >= start_date]

        if end_date:
            filtered = [e for e in filtered if e["date"] <= end_date]

        if status:
            filtered = [e for e in filtered if e["status"] == status.value]

        return filtered

    def get_pending_approval(self, approver_id: str = None) -> list[dict]:
        """Get entries pending approval."""
        entries = self._load_entries()
        return [
            e for e in entries
            if e["status"] == TimeEntryStatus.SUBMITTED.value
        ]

    def approve_entry(self, entry_id: str, approver_id: str) -> bool:
        """Approve a time entry."""
        entries = self._load_entries()

        for entry in entries:
            if entry["id"] == entry_id:
                if entry["status"] != TimeEntryStatus.SUBMITTED.value:
                    return False

                entry["status"] = TimeEntryStatus.APPROVED.value
                entry["approved_at"] = datetime.utcnow().isoformat()
                entry["approved_by"] = approver_id

                self._save_entries(entries)
                return True

        return False

    def get_billing_summary(
        self,
        expert_id: str = None,
        project_id: str = None,
        start_date: str = None,
        end_date: str = None,
    ) -> dict:
        """
        Get billing summary.

        Args:
            expert_id: Filter by expert
            project_id: Filter by project
            start_date: Start of period
            end_date: End of period

        Returns:
            Summary with hours, amounts, and breakdowns
        """
        entries = self._load_entries()

        # Apply filters
        if expert_id:
            entries = [e for e in entries if e["expert_id"] == expert_id]
        if project_id:
            entries = [e for e in entries if e.get("project_id") == project_id]
        if start_date:
            entries = [e for e in entries if e["date"] >= start_date]
        if end_date:
            entries = [e for e in entries if e["date"] <= end_date]

        # Calculate totals
        total_hours = sum(e["duration_hours"] for e in entries)
        total_amount = sum(e["total_amount"] for e in entries)

        approved = [e for e in entries if e["status"] == TimeEntryStatus.APPROVED.value]
        pending = [e for e in entries if e["status"] == TimeEntryStatus.SUBMITTED.value]

        # Breakdown by work type
        by_work_type = {}
        for entry in entries:
            wt = entry.get("work_type", "other")
            if wt not in by_work_type:
                by_work_type[wt] = {"hours": 0.0, "amount": 0.0}
            by_work_type[wt]["hours"] += entry["duration_hours"]
            by_work_type[wt]["amount"] += entry["total_amount"]

        return {
            "total_hours": total_hours,
            "total_amount": total_amount,
            "approved_hours": sum(e["duration_hours"] for e in approved),
            "approved_amount": sum(e["total_amount"] for e in approved),
            "pending_hours": sum(e["duration_hours"] for e in pending),
            "pending_amount": sum(e["total_amount"] for e in pending),
            "entry_count": len(entries),
            "by_work_type": by_work_type,
            "avg_hourly_rate": total_amount / total_hours if total_hours > 0 else 0,
        }
