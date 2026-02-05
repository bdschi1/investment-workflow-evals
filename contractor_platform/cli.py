#!/usr/bin/env python3
"""
Command-line interface for the Investment Workflow Evaluations platform.

This CLI provides tools for domain expert contributors to:
- Register and manage their profile
- Browse and claim tasks
- Submit work for review
- Track earnings and payments
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from contractor_platform.models.user import User, UserTier, Expertise
from contractor_platform.models.task import Task, TaskType, TaskStatus, TaskPriority
from contractor_platform.models.submission import Submission, SubmissionStatus
from contractor_platform.workflows.task_manager import TaskManager
from contractor_platform.workflows.review_workflow import ReviewWorkflow
from contractor_platform.workflows.payment_processor import PaymentProcessor


# Default data directory
DEFAULT_DATA_DIR = Path(__file__).parent.parent / "data"


def get_data_dir() -> Path:
    """Get data directory from environment or default."""
    data_dir = os.environ.get("EVAL_DATA_DIR", str(DEFAULT_DATA_DIR))
    return Path(data_dir)


def get_current_user() -> Optional[User]:
    """Get the current logged-in user."""
    data_dir = get_data_dir()
    session_file = data_dir / "current_session.json"

    if not session_file.exists():
        return None

    with open(session_file) as f:
        session = json.load(f)

    user_id = session.get("user_id")
    if not user_id:
        return None

    task_manager = TaskManager(data_dir)
    return task_manager.get_user(user_id)


def set_current_user(user_id: str) -> None:
    """Set the current logged-in user."""
    data_dir = get_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    session_file = data_dir / "current_session.json"

    with open(session_file, "w") as f:
        json.dump({"user_id": user_id, "logged_in_at": datetime.utcnow().isoformat()}, f)


def require_login(func):
    """Decorator to require user login."""
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            print("Error: Not logged in. Run 'python -m platform.cli login' first.")
            sys.exit(1)
        return func(user, *args, **kwargs)
    return wrapper


# === Registration Commands ===

def cmd_register(args):
    """Register a new contributor account."""
    data_dir = get_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)

    # Parse expertise
    expertise_list = []
    if args.expertise:
        for exp in args.expertise.split(","):
            exp = exp.strip().lower()
            try:
                expertise_list.append(Expertise(exp))
            except ValueError:
                print(f"Warning: Unknown expertise '{exp}', skipping")

    # Create user
    user = User(
        email=args.email,
        name=args.name or "",
        expertise=expertise_list,
    )

    # Save user
    users_file = data_dir / "users.json"
    users = []
    if users_file.exists():
        with open(users_file) as f:
            users = json.load(f)

    users.append(user.to_dict())

    with open(users_file, "w") as f:
        json.dump(users, f, indent=2)

    # Set as current user
    set_current_user(user.id)

    print(f"Registration successful!")
    print(f"User ID: {user.id}")
    print(f"Email: {user.email}")
    print(f"Tier: {user.tier.value}")
    print(f"\nYou are now logged in. Run 'python -m platform.cli tasks list' to see available tasks.")


def cmd_login(args):
    """Login with existing account."""
    data_dir = get_data_dir()
    users_file = data_dir / "users.json"

    if not users_file.exists():
        print("Error: No users registered. Run 'python -m platform.cli register' first.")
        sys.exit(1)

    with open(users_file) as f:
        users = json.load(f)

    # Find user by email
    user_data = None
    for u in users:
        if u.get("email") == args.email:
            user_data = u
            break

    if not user_data:
        print(f"Error: No user found with email '{args.email}'")
        sys.exit(1)

    set_current_user(user_data["id"])
    print(f"Logged in as {user_data.get('name', user_data['email'])}")


# === Task Commands ===

@require_login
def cmd_tasks_list(user, args):
    """List available tasks."""
    data_dir = get_data_dir()
    task_manager = TaskManager(data_dir)

    if args.status == "available":
        tasks = task_manager.get_available_tasks_for_user(user)
    elif args.status == "mine":
        tasks = task_manager.get_user_active_tasks(user.id)
    else:
        status = TaskStatus(args.status) if args.status else None
        tasks = task_manager.list_tasks(status=status)

    if not tasks:
        print("No tasks found.")
        return

    print(f"\n{'ID':<15} {'Type':<20} {'Title':<40} {'Status':<12} {'Payment':<10}")
    print("-" * 100)

    for task in tasks[:20]:  # Limit to 20
        payment = f"${task.calculate_payment(user.tier):.0f}"
        title = task.title[:38] + ".." if len(task.title) > 40 else task.title
        print(f"{task.id:<15} {task.task_type.value:<20} {title:<40} {task.status.value:<12} {payment:<10}")

    if len(tasks) > 20:
        print(f"\n... and {len(tasks) - 20} more tasks")


@require_login
def cmd_tasks_show(user, args):
    """Show task details."""
    data_dir = get_data_dir()
    task_manager = TaskManager(data_dir)

    task = task_manager.get_task(args.task_id)
    if not task:
        print(f"Error: Task '{args.task_id}' not found")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"Task: {task.id}")
    print(f"{'='*60}")
    print(f"\nTitle: {task.title}")
    print(f"Type: {task.task_type.value}")
    print(f"Status: {task.status.value}")
    print(f"Priority: {task.priority.value}")
    print(f"Module: {task.eval_module}")
    print(f"Min Tier: {task.min_tier.value}")
    print(f"Estimated Hours: {task.estimated_hours}")
    print(f"Payment: ${task.calculate_payment(user.tier):.2f}")

    if task.deadline:
        print(f"Deadline: {task.deadline.strftime('%Y-%m-%d %H:%M')}")

    print(f"\nDescription:\n{task.description}")

    if task.instructions:
        print(f"\nInstructions:\n{task.instructions}")

    if task.deliverables:
        print(f"\nDeliverables:")
        for d in task.deliverables:
            print(f"  - {d}")

    if task.acceptance_criteria:
        print(f"\nAcceptance Criteria:")
        for c in task.acceptance_criteria:
            print(f"  - {c}")

    if task.resources:
        print(f"\nResources:")
        for r in task.resources:
            print(f"  - {r}")


@require_login
def cmd_tasks_claim(user, args):
    """Claim a task."""
    data_dir = get_data_dir()
    task_manager = TaskManager(data_dir)

    success, message = task_manager.claim_task(args.task_id, user.id)

    if success:
        print(f"Success: {message}")
        print("Run 'python -m platform.cli tasks start {task_id}' when you begin working.")
    else:
        print(f"Error: {message}")
        sys.exit(1)


@require_login
def cmd_tasks_start(user, args):
    """Start working on a claimed task."""
    data_dir = get_data_dir()
    task_manager = TaskManager(data_dir)

    success, message = task_manager.start_task(args.task_id, user.id)

    if success:
        print(f"Success: {message}")
    else:
        print(f"Error: {message}")
        sys.exit(1)


@require_login
def cmd_tasks_release(user, args):
    """Release a claimed task back to the pool."""
    data_dir = get_data_dir()
    task_manager = TaskManager(data_dir)

    success, message = task_manager.release_task(args.task_id, user.id)

    if success:
        print(f"Success: {message}")
    else:
        print(f"Error: {message}")
        sys.exit(1)


# === Submission Commands ===

@require_login
def cmd_submit(user, args):
    """Submit completed work for a task."""
    data_dir = get_data_dir()
    task_manager = TaskManager(data_dir)
    review_workflow = ReviewWorkflow(data_dir)

    # Verify file exists
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {args.file}")
        sys.exit(1)

    # Submit task
    success, message = task_manager.submit_task(
        args.task_id,
        user.id,
        str(file_path.absolute()),
        args.notes
    )

    if not success:
        print(f"Error: {message}")
        sys.exit(1)

    # Create submission record
    task = task_manager.get_task(args.task_id)
    submission = review_workflow.create_submission(
        task_id=args.task_id,
        contributor_id=user.id,
        file_path=str(file_path.absolute()),
        content_type=task.task_type.value,
        title=task.title,
    )

    # Submit for review
    review_workflow.submit_for_review(submission.id)

    print(f"Success: {message}")
    print(f"Submission ID: {submission.id}")
    print("Your work is now in the review queue.")


# === Profile Commands ===

@require_login
def cmd_profile_show(user, args):
    """Show your profile."""
    print(f"\n{'='*50}")
    print(f"Profile: {user.name or user.email}")
    print(f"{'='*50}")
    print(f"\nID: {user.id}")
    print(f"Email: {user.email}")
    print(f"Tier: {user.tier.value}")
    print(f"Verified: {'Yes' if user.is_verified else 'No'}")

    if user.expertise:
        print(f"Expertise: {', '.join(e.value for e in user.expertise)}")

    print(f"\n--- Performance ---")
    print(f"Total Submissions: {user.total_submissions}")
    print(f"Approved: {user.approved_submissions}")
    print(f"Rejected: {user.rejected_submissions}")
    print(f"Approval Rate: {user.approval_rate:.1f}%")
    print(f"Average Quality Score: {user.average_quality_score:.1f}")

    print(f"\n--- Earnings ---")
    print(f"Total Earnings: ${user.total_earnings:.2f}")
    print(f"Pending Earnings: ${user.pending_earnings:.2f}")

    if user.eligible_for_upgrade:
        print(f"\n* You are eligible for tier upgrade!")


@require_login
def cmd_profile_stats(user, args):
    """Show detailed statistics."""
    data_dir = get_data_dir()
    task_manager = TaskManager(data_dir)
    payment_processor = PaymentProcessor(data_dir)

    # Get earnings report
    report = payment_processor.get_earnings_report(user.id)

    print(f"\n--- Earnings Summary ---")
    print(f"Total Earned: ${report.get('total_earned', 0):.2f}")
    print(f"Total Pending: ${report.get('total_pending', 0):.2f}")
    print(f"Total Tasks Completed: {report.get('task_count', 0)}")

    if report.get("by_task_type"):
        print(f"\n--- By Task Type ---")
        for task_type, amount in report["by_task_type"].items():
            print(f"  {task_type}: ${amount:.2f}")


# === Payment Commands ===

@require_login
def cmd_payments_list(user, args):
    """List your payments."""
    data_dir = get_data_dir()
    payment_processor = PaymentProcessor(data_dir)

    payments = payment_processor.get_user_payments(user.id)

    if not payments:
        print("No payments found.")
        return

    print(f"\n{'ID':<15} {'Amount':<12} {'Status':<12} {'Date':<20}")
    print("-" * 60)

    for payment in payments[:20]:
        date = payment.created_at.strftime("%Y-%m-%d")
        print(f"{payment.id:<15} ${payment.net_amount:<10.2f} {payment.status.value:<12} {date:<20}")


@require_login
def cmd_payments_pending(user, args):
    """Show pending earnings."""
    data_dir = get_data_dir()
    payment_processor = PaymentProcessor(data_dir)

    pending = payment_processor.get_pending_earnings(user.id)
    tasks = payment_processor.get_approved_unpaid_tasks(user.id)

    print(f"\nPending Earnings: ${pending:.2f}")
    print(f"Approved Tasks: {len(tasks)}")

    if tasks:
        print(f"\n{'Task ID':<15} {'Title':<40} {'Amount':<12}")
        print("-" * 70)
        for task in tasks:
            amount = payment_processor.calculate_task_payment(task, user)
            title = task.title[:38] + ".." if len(task.title) > 40 else task.title
            print(f"{task.id:<15} {title:<40} ${amount:<10.2f}")


# === Qualification Commands ===

@require_login
def cmd_qualify(user, args):
    """Start or check qualification assessment."""
    data_dir = get_data_dir()
    task_manager = TaskManager(data_dir)

    # Check if already qualified
    if user.qualification_test_passed:
        print(f"\nYou have already completed qualification.")
        print(f"Qualification Score: {user.qualification_score:.1f}")
        print(f"Current Tier: {user.tier.value}")
        return

    # Check for existing qualification task
    user_tasks = task_manager.get_user_active_tasks(user.id)
    qual_task = None
    for task in user_tasks:
        if task.task_type == TaskType.QUALIFICATION_TEST:
            qual_task = task
            break

    if qual_task:
        print(f"\nYou have an active qualification assessment.")
        print(f"Task ID: {qual_task.id}")
        print(f"Status: {qual_task.status.value}")
        if qual_task.deadline:
            print(f"Deadline: {qual_task.deadline.strftime('%Y-%m-%d %H:%M')}")
        print(f"\nRun 'python -m platform.cli tasks show {qual_task.id}' for details.")
        return

    # Create qualification task
    print("\n=== Qualification Assessment ===\n")
    print("Welcome to the Investment Workflow Evaluations platform!")
    print("Before accessing paid tasks, you'll complete a brief qualification.\n")
    print("Assessment Details:")
    print("  - Type: Basic Equity Analysis")
    print("  - Time Limit: 45 minutes")
    print("  - Passing Score: 70%")
    print("  - Fast-track to Standard tier: 85%+\n")

    if args.start:
        # Create the qualification task
        task = task_manager.create_task(
            title="Qualification Assessment - Basic Equity Analysis",
            description="Complete the consumer retail investment analysis to demonstrate your analytical skills.",
            task_type=TaskType.QUALIFICATION_TEST,
            eval_module="00_qualification",
            created_by="system",
            instructions="""
Complete the qualification scenario in evals/00_qualification/scenarios/basic_equity_analysis.yaml

Your submission should include:
1. Investment Thesis (2-3 sentences)
2. Key Supporting Points (3 bullet points)
3. Primary Risk (1-2 sentences)
4. Valuation Assessment
5. Recommendation: Buy, Hold, or Sell

Target length: 250-400 words. Submit as a markdown file.
            """.strip(),
            deliverables=["Markdown file with your analysis"],
            acceptance_criteria=[
                "Clear directional stance",
                "References specific financial data",
                "Identifies quantifiable risk",
                "Includes peer/historical valuation comparison",
            ],
        )

        # Auto-claim for the user
        task_manager.claim_task(task.id, user.id)
        task_manager.start_task(task.id, user.id)

        print(f"Qualification started!")
        print(f"Task ID: {task.id}")
        print(f"\nView the scenario:")
        print(f"  cat evals/00_qualification/scenarios/basic_equity_analysis.yaml")
        print(f"\nSubmit your work:")
        print(f"  python -m platform.cli submit --task {task.id} --file your_analysis.md")
    else:
        print("Run 'python -m platform.cli qualify --start' to begin the assessment.")


# === Time Tracking Commands ===

@require_login
def cmd_time_log(user, args):
    """Log time worked."""
    from contractor_platform.workflows.hourly_tracking import TimeTracker

    data_dir = get_data_dir()
    tracker = TimeTracker(data_dir)

    # Get hourly rate based on tier
    tier_rates = {
        UserTier.TRAINEE: 50.0,
        UserTier.STANDARD: 85.0,
        UserTier.SENIOR: 125.0,
        UserTier.EXPERT: 175.0,
    }
    hourly_rate = args.rate if args.rate else tier_rates.get(user.tier, 85.0)

    entry = tracker.log_time(
        expert_id=user.id,
        duration_hours=args.hours,
        description=args.description,
        work_type=args.type or "general",
        task_id=args.task,
        hourly_rate=hourly_rate,
    )

    print(f"\nTime logged successfully!")
    print(f"Entry ID: {entry.id}")
    print(f"Hours: {entry.duration_hours:.2f}")
    print(f"Rate: ${entry.hourly_rate:.2f}/hr")
    print(f"Amount: ${entry.total_amount:.2f}")


@require_login
def cmd_time_summary(user, args):
    """Show time tracking summary."""
    from contractor_platform.workflows.hourly_tracking import TimeTracker

    data_dir = get_data_dir()
    tracker = TimeTracker(data_dir)

    summary = tracker.get_billing_summary(
        expert_id=user.id,
        start_date=args.start_date,
        end_date=args.end_date,
    )

    print(f"\n=== Time Tracking Summary ===\n")
    print(f"Total Hours: {summary['total_hours']:.2f}")
    print(f"Total Amount: ${summary['total_amount']:.2f}")
    print(f"Approved: ${summary['approved_amount']:.2f}")
    print(f"Pending: ${summary['pending_amount']:.2f}")
    print(f"Entries: {summary['entry_count']}")

    if summary.get('avg_hourly_rate'):
        print(f"Avg Hourly Rate: ${summary['avg_hourly_rate']:.2f}")

    if summary.get('by_work_type'):
        print(f"\n--- By Work Type ---")
        for work_type, data in summary['by_work_type'].items():
            print(f"  {work_type}: {data['hours']:.1f}h (${data['amount']:.2f})")


# === Admin Commands ===

def cmd_admin_create_task(args):
    """Create a new task (admin only)."""
    data_dir = get_data_dir()
    task_manager = TaskManager(data_dir)

    # Parse task type
    try:
        task_type = TaskType(args.type)
    except ValueError:
        print(f"Error: Invalid task type '{args.type}'")
        print(f"Valid types: {', '.join(t.value for t in TaskType)}")
        sys.exit(1)

    task = task_manager.create_task(
        title=args.title,
        description=args.description,
        task_type=task_type,
        eval_module=args.module,
        created_by="admin",
        priority=TaskPriority(args.priority) if args.priority else TaskPriority.MEDIUM,
    )

    print(f"Task created: {task.id}")
    print(f"Title: {task.title}")
    print(f"Base Payment: ${task.base_payment:.2f}")


def cmd_admin_stats(args):
    """Show platform statistics (admin only)."""
    data_dir = get_data_dir()
    task_manager = TaskManager(data_dir)
    review_workflow = ReviewWorkflow(data_dir)
    payment_processor = PaymentProcessor(data_dir)

    task_stats = task_manager.get_task_statistics()
    review_stats = review_workflow.get_review_statistics()
    payment_stats = payment_processor.get_payment_statistics()

    print("\n=== Platform Statistics ===\n")

    print("--- Tasks ---")
    print(f"Total: {task_stats['total_tasks']}")
    for status, count in task_stats.get("by_status", {}).items():
        print(f"  {status}: {count}")

    print("\n--- Submissions ---")
    print(f"Total: {review_stats['total_submissions']}")
    print(f"Pending Review: {review_stats['pending_review']}")
    print(f"Approval Rate: {review_stats['approval_rate']:.1f}%")
    print(f"Avg Score: {review_stats['avg_score']:.1f}")

    print("\n--- Payments ---")
    print(f"Total Paid: ${payment_stats['total_paid']:.2f}")
    print(f"Pending: ${payment_stats['total_pending']:.2f}")


# === Main CLI ===

def main():
    parser = argparse.ArgumentParser(
        description="Investment Workflow Evaluations Platform CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Register:     python -m platform.cli register --email you@example.com --name "Your Name"
  Login:        python -m platform.cli login --email you@example.com
  List tasks:   python -m platform.cli tasks list --status available
  Claim task:   python -m platform.cli tasks claim TASK-ABC123
  Submit:       python -m platform.cli submit --task TASK-ABC123 --file my_work.yaml
  Profile:      python -m platform.cli profile show
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Register
    register_parser = subparsers.add_parser("register", help="Register a new account")
    register_parser.add_argument("--email", required=True, help="Your email address")
    register_parser.add_argument("--name", help="Your full name")
    register_parser.add_argument("--expertise", help="Comma-separated expertise areas")
    register_parser.set_defaults(func=cmd_register)

    # Login
    login_parser = subparsers.add_parser("login", help="Login to existing account")
    login_parser.add_argument("--email", required=True, help="Your email address")
    login_parser.set_defaults(func=cmd_login)

    # Tasks
    tasks_parser = subparsers.add_parser("tasks", help="Task management")
    tasks_sub = tasks_parser.add_subparsers(dest="tasks_command")

    # tasks list
    tasks_list = tasks_sub.add_parser("list", help="List tasks")
    tasks_list.add_argument("--status", default="available",
                           help="Filter by status (available, mine, open, claimed, etc.)")
    tasks_list.set_defaults(func=cmd_tasks_list)

    # tasks show
    tasks_show = tasks_sub.add_parser("show", help="Show task details")
    tasks_show.add_argument("task_id", help="Task ID")
    tasks_show.set_defaults(func=cmd_tasks_show)

    # tasks claim
    tasks_claim = tasks_sub.add_parser("claim", help="Claim a task")
    tasks_claim.add_argument("task_id", help="Task ID")
    tasks_claim.set_defaults(func=cmd_tasks_claim)

    # tasks start
    tasks_start = tasks_sub.add_parser("start", help="Start working on a task")
    tasks_start.add_argument("task_id", help="Task ID")
    tasks_start.set_defaults(func=cmd_tasks_start)

    # tasks release
    tasks_release = tasks_sub.add_parser("release", help="Release a claimed task")
    tasks_release.add_argument("task_id", help="Task ID")
    tasks_release.set_defaults(func=cmd_tasks_release)

    # Submit
    submit_parser = subparsers.add_parser("submit", help="Submit completed work")
    submit_parser.add_argument("--task", dest="task_id", required=True, help="Task ID")
    submit_parser.add_argument("--file", required=True, help="Path to submission file")
    submit_parser.add_argument("--notes", help="Additional notes")
    submit_parser.set_defaults(func=cmd_submit)

    # Profile
    profile_parser = subparsers.add_parser("profile", help="Profile management")
    profile_sub = profile_parser.add_subparsers(dest="profile_command")

    profile_show = profile_sub.add_parser("show", help="Show your profile")
    profile_show.set_defaults(func=cmd_profile_show)

    profile_stats = profile_sub.add_parser("stats", help="Show detailed statistics")
    profile_stats.set_defaults(func=cmd_profile_stats)

    # Payments
    payments_parser = subparsers.add_parser("payments", help="Payment management")
    payments_sub = payments_parser.add_subparsers(dest="payments_command")

    payments_list = payments_sub.add_parser("list", help="List your payments")
    payments_list.set_defaults(func=cmd_payments_list)

    payments_pending = payments_sub.add_parser("pending", help="Show pending earnings")
    payments_pending.set_defaults(func=cmd_payments_pending)

    # Qualify
    qualify_parser = subparsers.add_parser("qualify", help="Start qualification assessment")
    qualify_parser.add_argument("--start", action="store_true", help="Start the assessment")
    qualify_parser.set_defaults(func=cmd_qualify)

    # Time
    time_parser = subparsers.add_parser("time", help="Time tracking")
    time_sub = time_parser.add_subparsers(dest="time_command")

    time_log = time_sub.add_parser("log", help="Log time worked")
    time_log.add_argument("--hours", type=float, required=True, help="Hours worked")
    time_log.add_argument("--description", required=True, help="Work description")
    time_log.add_argument("--type", help="Work type (scenario_creation, golden_answer, etc.)")
    time_log.add_argument("--task", help="Associated task ID")
    time_log.add_argument("--rate", type=float, help="Override hourly rate")
    time_log.set_defaults(func=cmd_time_log)

    time_summary = time_sub.add_parser("summary", help="Show time summary")
    time_summary.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    time_summary.add_argument("--end-date", help="End date (YYYY-MM-DD)")
    time_summary.set_defaults(func=cmd_time_summary)

    # Admin
    admin_parser = subparsers.add_parser("admin", help="Admin commands")
    admin_sub = admin_parser.add_subparsers(dest="admin_command")

    admin_create = admin_sub.add_parser("create-task", help="Create a new task")
    admin_create.add_argument("--title", required=True, help="Task title")
    admin_create.add_argument("--description", required=True, help="Task description")
    admin_create.add_argument("--type", required=True, help="Task type")
    admin_create.add_argument("--module", required=True, help="Eval module")
    admin_create.add_argument("--priority", help="Priority (low, medium, high, urgent)")
    admin_create.set_defaults(func=cmd_admin_create_task)

    admin_stats = admin_sub.add_parser("stats", help="Show platform statistics")
    admin_stats.set_defaults(func=cmd_admin_stats)

    # Parse and execute
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
