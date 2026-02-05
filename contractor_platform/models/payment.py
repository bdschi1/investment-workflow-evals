"""Payment model for contractor compensation."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class PaymentStatus(Enum):
    """Status of a payment."""

    PENDING = "pending"          # Approved but not yet processed
    PROCESSING = "processing"    # Being processed
    COMPLETED = "completed"      # Successfully paid
    FAILED = "failed"            # Payment failed
    CANCELLED = "cancelled"      # Payment cancelled
    ON_HOLD = "on_hold"          # Payment on hold (dispute, verification)


class PaymentMethod(Enum):
    """Supported payment methods."""

    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    WISE = "wise"
    PAYONEER = "payoneer"
    CRYPTO_USDC = "crypto_usdc"


@dataclass
class Payment:
    """A payment to a contributor."""

    # Identity
    id: str = field(default_factory=lambda: f"PAY-{uuid.uuid4().hex[:8].upper()}")
    user_id: str = ""

    # Status
    status: PaymentStatus = PaymentStatus.PENDING
    payment_method: Optional[PaymentMethod] = None

    # Amount
    gross_amount: float = 0.0  # Before any deductions
    platform_fee: float = 0.0  # Platform fee (if any)
    net_amount: float = 0.0    # Amount to be paid

    # Currency
    currency: str = "USD"
    exchange_rate: Optional[float] = None  # If converted

    # Associated Work
    task_ids: list[str] = field(default_factory=list)
    submission_ids: list[str] = field(default_factory=list)

    # Line Items
    line_items: list[dict] = field(default_factory=list)
    # Each item: {"description": str, "amount": float, "task_id": str}

    # Payment Details
    payment_reference: Optional[str] = None  # External reference ID
    transaction_id: Optional[str] = None     # Provider transaction ID

    # Dates
    period_start: Optional[datetime] = None  # Work period start
    period_end: Optional[datetime] = None    # Work period end
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Notes
    notes: str = ""
    failure_reason: Optional[str] = None

    # Tax Info
    is_taxable: bool = True
    tax_form_collected: bool = False  # W-9, W-8BEN, etc.

    def add_line_item(
        self,
        description: str,
        amount: float,
        task_id: Optional[str] = None,
        submission_id: Optional[str] = None,
    ) -> None:
        """Add a line item to this payment."""
        item = {
            "description": description,
            "amount": amount,
            "task_id": task_id,
            "submission_id": submission_id,
        }
        self.line_items.append(item)

        if task_id and task_id not in self.task_ids:
            self.task_ids.append(task_id)
        if submission_id and submission_id not in self.submission_ids:
            self.submission_ids.append(submission_id)

        self.gross_amount += amount
        self._recalculate_net()

    def _recalculate_net(self) -> None:
        """Recalculate net amount."""
        self.net_amount = self.gross_amount - self.platform_fee

    def set_platform_fee(self, fee_percentage: float = 0.0) -> None:
        """Set platform fee as percentage of gross."""
        self.platform_fee = self.gross_amount * (fee_percentage / 100)
        self._recalculate_net()

    def process(self, payment_reference: str) -> bool:
        """Mark payment as processing."""
        if self.status != PaymentStatus.PENDING:
            return False

        self.status = PaymentStatus.PROCESSING
        self.payment_reference = payment_reference
        self.processed_at = datetime.utcnow()
        return True

    def complete(self, transaction_id: str) -> bool:
        """Mark payment as completed."""
        if self.status != PaymentStatus.PROCESSING:
            return False

        self.status = PaymentStatus.COMPLETED
        self.transaction_id = transaction_id
        self.completed_at = datetime.utcnow()
        return True

    def fail(self, reason: str) -> bool:
        """Mark payment as failed."""
        if self.status not in (PaymentStatus.PENDING, PaymentStatus.PROCESSING):
            return False

        self.status = PaymentStatus.FAILED
        self.failure_reason = reason
        return True

    def cancel(self, reason: str = "") -> bool:
        """Cancel the payment."""
        if self.status in (PaymentStatus.COMPLETED, PaymentStatus.CANCELLED):
            return False

        self.status = PaymentStatus.CANCELLED
        self.notes = reason if reason else self.notes
        return True

    def hold(self, reason: str) -> bool:
        """Put payment on hold."""
        if self.status not in (PaymentStatus.PENDING, PaymentStatus.PROCESSING):
            return False

        self.status = PaymentStatus.ON_HOLD
        self.notes = reason
        return True

    def to_dict(self) -> dict:
        """Serialize payment to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "status": self.status.value,
            "payment_method": self.payment_method.value if self.payment_method else None,
            "gross_amount": self.gross_amount,
            "platform_fee": self.platform_fee,
            "net_amount": self.net_amount,
            "currency": self.currency,
            "exchange_rate": self.exchange_rate,
            "task_ids": self.task_ids,
            "submission_ids": self.submission_ids,
            "line_items": self.line_items,
            "payment_reference": self.payment_reference,
            "transaction_id": self.transaction_id,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "created_at": self.created_at.isoformat(),
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "notes": self.notes,
            "failure_reason": self.failure_reason,
            "is_taxable": self.is_taxable,
            "tax_form_collected": self.tax_form_collected,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Payment":
        """Deserialize payment from dictionary."""
        payment = cls(
            id=data.get("id", f"PAY-{uuid.uuid4().hex[:8].upper()}"),
            user_id=data.get("user_id", ""),
            status=PaymentStatus(data.get("status", "pending")),
            payment_method=PaymentMethod(data["payment_method"]) if data.get("payment_method") else None,
            gross_amount=data.get("gross_amount", 0.0),
            platform_fee=data.get("platform_fee", 0.0),
            net_amount=data.get("net_amount", 0.0),
            currency=data.get("currency", "USD"),
            exchange_rate=data.get("exchange_rate"),
            task_ids=data.get("task_ids", []),
            submission_ids=data.get("submission_ids", []),
            line_items=data.get("line_items", []),
            payment_reference=data.get("payment_reference"),
            transaction_id=data.get("transaction_id"),
            notes=data.get("notes", ""),
            failure_reason=data.get("failure_reason"),
            is_taxable=data.get("is_taxable", True),
            tax_form_collected=data.get("tax_form_collected", False),
        )

        for field_name in ["period_start", "period_end", "created_at", "processed_at", "completed_at"]:
            if data.get(field_name):
                setattr(payment, field_name, datetime.fromisoformat(data[field_name]))

        return payment


@dataclass
class PaymentBatch:
    """A batch of payments to be processed together."""

    id: str = field(default_factory=lambda: f"BATCH-{uuid.uuid4().hex[:8].upper()}")
    payments: list[Payment] = field(default_factory=list)
    status: PaymentStatus = PaymentStatus.PENDING

    # Totals
    total_gross: float = 0.0
    total_fees: float = 0.0
    total_net: float = 0.0
    payment_count: int = 0

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def add_payment(self, payment: Payment) -> None:
        """Add a payment to this batch."""
        self.payments.append(payment)
        self.total_gross += payment.gross_amount
        self.total_fees += payment.platform_fee
        self.total_net += payment.net_amount
        self.payment_count += 1

    def to_dict(self) -> dict:
        """Serialize batch to dictionary."""
        return {
            "id": self.id,
            "payments": [p.to_dict() for p in self.payments],
            "status": self.status.value,
            "total_gross": self.total_gross,
            "total_fees": self.total_fees,
            "total_net": self.total_net,
            "payment_count": self.payment_count,
            "created_at": self.created_at.isoformat(),
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
