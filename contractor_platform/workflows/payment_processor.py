"""Payment processing for approved submissions."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from ..models.task import Task, TaskStatus
from ..models.submission import Submission, SubmissionStatus
from ..models.payment import Payment, PaymentBatch, PaymentStatus, PaymentMethod
from ..models.user import User, UserTier


class PaymentProcessor:
    """Handles payment calculation and processing for contributors."""

    # Platform fee percentage (0 = no platform fee)
    PLATFORM_FEE_PERCENT = 0.0

    # Minimum payout threshold
    MIN_PAYOUT_AMOUNT = 25.0

    def __init__(self, data_dir: Path):
        """Initialize payment processor with data directory."""
        self.data_dir = data_dir
        self.payments_file = data_dir / "payments.json"
        self.tasks_file = data_dir / "tasks.json"
        self.users_file = data_dir / "users.json"
        self._ensure_data_files()

    def _ensure_data_files(self) -> None:
        """Ensure data files exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.payments_file.exists():
            self._save_payments([])

    def _load_payments(self) -> list[Payment]:
        """Load all payments from storage."""
        with open(self.payments_file, "r") as f:
            data = json.load(f)
        return [Payment.from_dict(p) for p in data]

    def _save_payments(self, payments: list[Payment]) -> None:
        """Save all payments to storage."""
        with open(self.payments_file, "w") as f:
            json.dump([p.to_dict() for p in payments], f, indent=2)

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

    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        users = self._load_users()
        for user in users:
            if user.id == user_id:
                return user
        return None

    def calculate_task_payment(self, task: Task, user: User) -> float:
        """Calculate the payment amount for a completed task."""
        # Base payment from task type
        base = task.base_payment

        # Tier multiplier
        tier_multiplier = user.tier.rate_multiplier

        # Priority bonus
        priority_bonus = task.priority.priority_bonus

        # Additional bonus from task
        bonus = task.bonus_payment

        # Quality bonus based on review score
        quality_bonus = 1.0
        if task.review_score:
            if task.review_score >= 95:
                quality_bonus = 1.15  # 15% bonus for excellent
            elif task.review_score >= 90:
                quality_bonus = 1.10  # 10% bonus for very good

        total = (base * tier_multiplier * priority_bonus * quality_bonus) + bonus

        return round(total, 2)

    def get_approved_unpaid_tasks(self, user_id: str) -> list[Task]:
        """Get all approved tasks for a user that haven't been paid."""
        tasks = self._load_tasks()
        return [
            t for t in tasks
            if t.assigned_to == user_id
            and t.status == TaskStatus.APPROVED
        ]

    def get_pending_earnings(self, user_id: str) -> float:
        """Get total pending earnings for a user."""
        user = self.get_user(user_id)
        if not user:
            return 0.0

        tasks = self.get_approved_unpaid_tasks(user_id)
        total = sum(self.calculate_task_payment(t, user) for t in tasks)
        return round(total, 2)

    def create_payment(
        self,
        user_id: str,
        task_ids: list[str] = None,
        payment_method: PaymentMethod = None,
    ) -> tuple[Optional[Payment], str]:
        """Create a payment for approved tasks."""
        user = self.get_user(user_id)
        if not user:
            return None, "User not found"

        # Get tasks to pay for
        if task_ids:
            tasks = self._load_tasks()
            tasks_to_pay = [t for t in tasks if t.id in task_ids]
        else:
            tasks_to_pay = self.get_approved_unpaid_tasks(user_id)

        if not tasks_to_pay:
            return None, "No approved tasks to pay"

        # Verify all tasks belong to user and are approved
        for task in tasks_to_pay:
            if task.assigned_to != user_id:
                return None, f"Task {task.id} is not assigned to this user"
            if task.status != TaskStatus.APPROVED:
                return None, f"Task {task.id} is not approved"

        # Create payment
        payment = Payment(
            user_id=user_id,
            payment_method=payment_method or PaymentMethod.BANK_TRANSFER,
            status=PaymentStatus.PENDING,
        )

        # Add line items for each task
        for task in tasks_to_pay:
            amount = self.calculate_task_payment(task, user)
            payment.add_line_item(
                description=f"{task.task_type.value}: {task.title}",
                amount=amount,
                task_id=task.id,
            )

        # Apply platform fee
        payment.set_platform_fee(self.PLATFORM_FEE_PERCENT)

        # Check minimum payout
        if payment.net_amount < self.MIN_PAYOUT_AMOUNT:
            return None, f"Minimum payout is ${self.MIN_PAYOUT_AMOUNT}. Current: ${payment.net_amount}"

        # Check tax form
        if not user.tax_form_collected:
            payment.hold("Tax form required")
            payment.notes = "Please submit W-9 (US) or W-8BEN (non-US) before payment can be processed."

        # Save payment
        payments = self._load_payments()
        payments.append(payment)
        self._save_payments(payments)

        return payment, "Payment created successfully"

    def process_payment(
        self,
        payment_id: str,
        payment_reference: str,
    ) -> tuple[bool, str]:
        """Mark a payment as processing."""
        payments = self._load_payments()
        payment = next((p for p in payments if p.id == payment_id), None)

        if not payment:
            return False, "Payment not found"

        success = payment.process(payment_reference)
        if success:
            self._save_payments(payments)
            return True, "Payment is processing"

        return False, f"Cannot process payment in status: {payment.status.value}"

    def complete_payment(
        self,
        payment_id: str,
        transaction_id: str,
    ) -> tuple[bool, str]:
        """Mark a payment as completed."""
        payments = self._load_payments()
        payment = next((p for p in payments if p.id == payment_id), None)

        if not payment:
            return False, "Payment not found"

        success = payment.complete(transaction_id)
        if success:
            self._save_payments(payments)

            # Update task statuses to PAID
            self._mark_tasks_paid(payment.task_ids)

            # Update user earnings
            self._update_user_earnings(payment.user_id, payment.net_amount)

            return True, "Payment completed"

        return False, f"Cannot complete payment in status: {payment.status.value}"

    def _mark_tasks_paid(self, task_ids: list[str]) -> None:
        """Mark tasks as paid."""
        tasks = self._load_tasks()
        for task in tasks:
            if task.id in task_ids:
                task.status = TaskStatus.PAID
                task.updated_at = datetime.utcnow()
        self._save_tasks(tasks)

    def _update_user_earnings(self, user_id: str, amount: float) -> None:
        """Update user's total earnings."""
        users = self._load_users()
        for user in users:
            if user.id == user_id:
                user.total_earnings += amount
                user.updated_at = datetime.utcnow()
                break
        self._save_users(users)

    def fail_payment(self, payment_id: str, reason: str) -> tuple[bool, str]:
        """Mark a payment as failed."""
        payments = self._load_payments()
        payment = next((p for p in payments if p.id == payment_id), None)

        if not payment:
            return False, "Payment not found"

        success = payment.fail(reason)
        if success:
            self._save_payments(payments)
            return True, "Payment marked as failed"

        return False, f"Cannot fail payment in status: {payment.status.value}"

    def get_payment(self, payment_id: str) -> Optional[Payment]:
        """Get a payment by ID."""
        payments = self._load_payments()
        return next((p for p in payments if p.id == payment_id), None)

    def get_user_payments(
        self,
        user_id: str,
        status: Optional[PaymentStatus] = None,
    ) -> list[Payment]:
        """Get all payments for a user."""
        payments = self._load_payments()
        user_payments = [p for p in payments if p.user_id == user_id]

        if status:
            user_payments = [p for p in user_payments if p.status == status]

        return sorted(user_payments, key=lambda p: p.created_at, reverse=True)

    def create_payment_batch(
        self,
        user_ids: list[str] = None,
        min_amount: float = None,
    ) -> tuple[Optional[PaymentBatch], str]:
        """Create a batch of payments for multiple users."""
        users = self._load_users()

        if user_ids:
            users = [u for u in users if u.id in user_ids]

        batch = PaymentBatch()

        for user in users:
            pending = self.get_pending_earnings(user.id)

            # Check minimum threshold
            threshold = min_amount or self.MIN_PAYOUT_AMOUNT
            if pending < threshold:
                continue

            # Check tax form
            if not user.tax_form_collected:
                continue

            # Create payment for user
            payment, msg = self.create_payment(user.id)
            if payment:
                batch.add_payment(payment)

        if batch.payment_count == 0:
            return None, "No eligible payments for batch"

        return batch, f"Batch created with {batch.payment_count} payments"

    def get_payment_statistics(self) -> dict:
        """Get platform payment statistics."""
        payments = self._load_payments()

        stats = {
            "total_payments": len(payments),
            "by_status": {},
            "total_paid": 0.0,
            "total_pending": 0.0,
            "avg_payment_amount": 0.0,
            "by_method": {},
        }

        amounts = []

        for payment in payments:
            # By status
            status = payment.status.value
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            # By method
            if payment.payment_method:
                method = payment.payment_method.value
                stats["by_method"][method] = stats["by_method"].get(method, 0) + 1

            # Amounts
            if payment.status == PaymentStatus.COMPLETED:
                stats["total_paid"] += payment.net_amount
                amounts.append(payment.net_amount)
            elif payment.status == PaymentStatus.PENDING:
                stats["total_pending"] += payment.net_amount

        if amounts:
            stats["avg_payment_amount"] = sum(amounts) / len(amounts)

        return stats

    def get_earnings_report(
        self,
        user_id: str,
        start_date: datetime = None,
        end_date: datetime = None,
    ) -> dict:
        """Generate an earnings report for a user."""
        user = self.get_user(user_id)
        if not user:
            return {"error": "User not found"}

        payments = self.get_user_payments(user_id)

        # Filter by date range
        if start_date:
            payments = [p for p in payments if p.created_at >= start_date]
        if end_date:
            payments = [p for p in payments if p.created_at <= end_date]

        report = {
            "user_id": user_id,
            "user_name": user.name,
            "period_start": start_date.isoformat() if start_date else None,
            "period_end": end_date.isoformat() if end_date else None,
            "total_earned": 0.0,
            "total_pending": 0.0,
            "payment_count": 0,
            "task_count": 0,
            "by_task_type": {},
            "payments": [],
        }

        for payment in payments:
            if payment.status == PaymentStatus.COMPLETED:
                report["total_earned"] += payment.net_amount
            elif payment.status == PaymentStatus.PENDING:
                report["total_pending"] += payment.net_amount

            report["payment_count"] += 1
            report["task_count"] += len(payment.task_ids)

            for item in payment.line_items:
                task_type = item.get("description", "").split(":")[0]
                report["by_task_type"][task_type] = (
                    report["by_task_type"].get(task_type, 0) + item["amount"]
                )

            report["payments"].append({
                "id": payment.id,
                "amount": payment.net_amount,
                "status": payment.status.value,
                "created_at": payment.created_at.isoformat(),
                "completed_at": payment.completed_at.isoformat() if payment.completed_at else None,
            })

        return report
