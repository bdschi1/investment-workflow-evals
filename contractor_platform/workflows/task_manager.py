"""Task management system for creating, assigning, and tracking work."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from ..models.task import Task, TaskType, TaskStatus, TaskPriority
from ..models.user import User, UserTier, Expertise


class TaskManager:
    """Manages the lifecycle of tasks on the platform."""

    def __init__(self, data_dir: Path):
        """Initialize task manager with data directory."""
        self.data_dir = data_dir
        self.tasks_file = data_dir / "tasks.json"
        self.users_file = data_dir / "users.json"
        self._ensure_data_files()

    def _ensure_data_files(self) -> None:
        """Ensure data directory and files exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.tasks_file.exists():
            self._save_tasks([])
        if not self.users_file.exists():
            self._save_users([])

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

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        tasks = self._load_tasks()
        for task in tasks:
            if task.id == task_id:
                return task
        return None

    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        users = self._load_users()
        for user in users:
            if user.id == user_id:
                return user
        return None

    def create_task(
        self,
        title: str,
        description: str,
        task_type: TaskType,
        eval_module: str,
        created_by: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        required_expertise: list[Expertise] = None,
        instructions: str = "",
        resources: list[str] = None,
        deliverables: list[str] = None,
        acceptance_criteria: list[str] = None,
        deadline_days: int = 7,
        bonus_payment: float = 0.0,
        tags: list[str] = None,
        scenario_name: Optional[str] = None,
    ) -> Task:
        """Create a new task."""
        task = Task(
            title=title,
            description=description,
            task_type=task_type,
            priority=priority,
            status=TaskStatus.OPEN,
            eval_module=eval_module,
            scenario_name=scenario_name,
            required_expertise=required_expertise or [],
            created_by=created_by,
            instructions=instructions,
            resources=resources or [],
            deliverables=deliverables or [],
            acceptance_criteria=acceptance_criteria or [],
            bonus_payment=bonus_payment,
            tags=tags or [],
        )

        tasks = self._load_tasks()
        tasks.append(task)
        self._save_tasks(tasks)

        return task

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        task_type: Optional[TaskType] = None,
        eval_module: Optional[str] = None,
        assigned_to: Optional[str] = None,
        min_tier: Optional[UserTier] = None,
        expertise: Optional[list[Expertise]] = None,
        include_overdue: bool = True,
    ) -> list[Task]:
        """List tasks with optional filtering."""
        tasks = self._load_tasks()

        filtered = []
        for task in tasks:
            # Status filter
            if status and task.status != status:
                continue

            # Type filter
            if task_type and task.task_type != task_type:
                continue

            # Module filter
            if eval_module and task.eval_module != eval_module:
                continue

            # Assignment filter
            if assigned_to and task.assigned_to != assigned_to:
                continue

            # Tier filter
            if min_tier:
                tier_order = [UserTier.TRAINEE, UserTier.STANDARD, UserTier.SENIOR, UserTier.EXPERT]
                if tier_order.index(task.min_tier) > tier_order.index(min_tier):
                    continue

            # Expertise filter
            if expertise:
                if not any(e in task.required_expertise for e in expertise):
                    if task.required_expertise:  # Only filter if task has requirements
                        continue

            # Overdue filter
            if not include_overdue and task.is_overdue:
                continue

            filtered.append(task)

        return sorted(filtered, key=lambda t: (t.priority.value, t.created_at), reverse=True)

    def get_available_tasks_for_user(self, user: User) -> list[Task]:
        """Get tasks available for a specific user to claim."""
        tasks = self.list_tasks(status=TaskStatus.OPEN)

        available = []
        for task in tasks:
            # Check tier requirement
            tier_order = [UserTier.TRAINEE, UserTier.STANDARD, UserTier.SENIOR, UserTier.EXPERT, UserTier.ADMIN]
            if tier_order.index(user.tier) < tier_order.index(task.min_tier):
                continue

            # Check expertise (if task has requirements)
            if task.required_expertise:
                if not user.has_expertise(task.required_expertise):
                    continue

            # Check if user is verified for non-training tasks
            if task.task_type != TaskType.TRAINING_TASK and not user.is_verified:
                continue

            available.append(task)

        return available

    def claim_task(self, task_id: str, user_id: str) -> tuple[bool, str]:
        """Claim a task for a user."""
        task = self.get_task(task_id)
        user = self.get_user(user_id)

        if not task:
            return False, "Task not found"

        if not user:
            return False, "User not found"

        if not task.is_claimable:
            return False, f"Task is not available (status: {task.status.value})"

        # Check tier
        tier_order = [UserTier.TRAINEE, UserTier.STANDARD, UserTier.SENIOR, UserTier.EXPERT, UserTier.ADMIN]
        if tier_order.index(user.tier) < tier_order.index(task.min_tier):
            return False, f"Requires {task.min_tier.value} tier or higher"

        # Check expertise
        if task.required_expertise and not user.has_expertise(task.required_expertise):
            return False, "Missing required expertise"

        # Claim the task
        success = task.claim(user_id)
        if success:
            tasks = self._load_tasks()
            tasks = [t if t.id != task_id else task for t in tasks]
            self._save_tasks(tasks)
            return True, f"Task {task_id} claimed successfully"

        return False, "Failed to claim task"

    def start_task(self, task_id: str, user_id: str) -> tuple[bool, str]:
        """Mark a task as in progress."""
        task = self.get_task(task_id)

        if not task:
            return False, "Task not found"

        if task.assigned_to != user_id:
            return False, "Task is not assigned to you"

        success = task.start()
        if success:
            tasks = self._load_tasks()
            tasks = [t if t.id != task_id else task for t in tasks]
            self._save_tasks(tasks)
            return True, f"Task {task_id} started"

        return False, f"Cannot start task in status: {task.status.value}"

    def submit_task(
        self,
        task_id: str,
        user_id: str,
        file_path: str,
        notes: Optional[str] = None,
    ) -> tuple[bool, str]:
        """Submit completed work for a task."""
        task = self.get_task(task_id)

        if not task:
            return False, "Task not found"

        if task.assigned_to != user_id:
            return False, "Task is not assigned to you"

        success = task.submit(file_path, notes)
        if success:
            tasks = self._load_tasks()
            tasks = [t if t.id != task_id else task for t in tasks]
            self._save_tasks(tasks)
            return True, f"Task {task_id} submitted for review"

        return False, f"Cannot submit task in status: {task.status.value}"

    def release_task(self, task_id: str, user_id: str, is_admin: bool = False) -> tuple[bool, str]:
        """Release a claimed task back to the pool."""
        task = self.get_task(task_id)

        if not task:
            return False, "Task not found"

        if task.assigned_to != user_id and not is_admin:
            return False, "Task is not assigned to you"

        success = task.release()
        if success:
            tasks = self._load_tasks()
            tasks = [t if t.id != task_id else task for t in tasks]
            self._save_tasks(tasks)
            return True, f"Task {task_id} released"

        return False, f"Cannot release task in status: {task.status.value}"

    def get_user_active_tasks(self, user_id: str) -> list[Task]:
        """Get all active tasks for a user."""
        tasks = self._load_tasks()
        active_statuses = [
            TaskStatus.CLAIMED,
            TaskStatus.IN_PROGRESS,
            TaskStatus.REVISION,
        ]
        return [
            t for t in tasks
            if t.assigned_to == user_id and t.status in active_statuses
        ]

    def get_tasks_pending_review(self) -> list[Task]:
        """Get all tasks waiting for review."""
        return self.list_tasks(status=TaskStatus.SUBMITTED)

    def get_overdue_tasks(self) -> list[Task]:
        """Get all overdue tasks."""
        tasks = self._load_tasks()
        return [t for t in tasks if t.is_overdue and t.status not in [
            TaskStatus.APPROVED, TaskStatus.REJECTED, TaskStatus.PAID, TaskStatus.CANCELLED
        ]]

    def get_task_statistics(self) -> dict:
        """Get platform task statistics."""
        tasks = self._load_tasks()

        stats = {
            "total_tasks": len(tasks),
            "by_status": {},
            "by_type": {},
            "by_module": {},
            "overdue_count": 0,
            "avg_completion_time_hours": 0,
        }

        completion_times = []

        for task in tasks:
            # By status
            status = task.status.value
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            # By type
            task_type = task.task_type.value
            stats["by_type"][task_type] = stats["by_type"].get(task_type, 0) + 1

            # By module
            module = task.eval_module or "unassigned"
            stats["by_module"][module] = stats["by_module"].get(module, 0) + 1

            # Overdue
            if task.is_overdue:
                stats["overdue_count"] += 1

            # Completion time
            if task.claimed_at and task.submitted_at:
                duration = task.submitted_at - task.claimed_at
                completion_times.append(duration.total_seconds() / 3600)

        if completion_times:
            stats["avg_completion_time_hours"] = sum(completion_times) / len(completion_times)

        return stats

    def bulk_create_tasks(self, task_configs: list[dict]) -> list[Task]:
        """Create multiple tasks at once."""
        created_tasks = []
        for config in task_configs:
            task = self.create_task(**config)
            created_tasks.append(task)
        return created_tasks


def create_scenario_task(
    manager: TaskManager,
    eval_module: str,
    scenario_name: str,
    created_by: str,
    priority: TaskPriority = TaskPriority.MEDIUM,
) -> Task:
    """Helper to create a scenario creation task."""
    return manager.create_task(
        title=f"Create scenario: {scenario_name}",
        description=f"Create a new evaluation scenario '{scenario_name}' for the {eval_module} module.",
        task_type=TaskType.SCENARIO_CREATION,
        eval_module=eval_module,
        scenario_name=scenario_name,
        created_by=created_by,
        priority=priority,
        instructions="""
Create a complete evaluation scenario including:
1. Scenario context (company, market conditions, available data)
2. Specific task or question for the AI to answer
3. Data sources and reference materials
4. Key facts that must be included in a correct response
5. Common pitfalls to test for

Follow the scenario template in templates/scenario_template.yaml
""",
        deliverables=[
            f"evals/{eval_module}/scenarios/{scenario_name}.yaml",
        ],
        acceptance_criteria=[
            "Scenario follows standard template format",
            "All data sources are publicly verifiable",
            "Context is complete enough for independent analysis",
            "Key facts and pitfalls are clearly documented",
            "Difficulty level is appropriate for the module",
        ],
    )


def create_golden_answer_task(
    manager: TaskManager,
    eval_module: str,
    scenario_name: str,
    created_by: str,
    priority: TaskPriority = TaskPriority.MEDIUM,
) -> Task:
    """Helper to create a golden answer writing task."""
    return manager.create_task(
        title=f"Write golden answer: {scenario_name}",
        description=f"Write an expert-level reference answer for the '{scenario_name}' scenario.",
        task_type=TaskType.GOLDEN_ANSWER,
        eval_module=eval_module,
        scenario_name=scenario_name,
        created_by=created_by,
        priority=priority,
        required_expertise=[Expertise.EQUITY_RESEARCH],
        instructions="""
Write a comprehensive golden answer that demonstrates:
1. Proper analytical workflow and methodology
2. Evidence-backed reasoning with citations
3. Risk awareness and balanced presentation
4. Professional communication style
5. Appropriate caveats and disclaimers

The answer should be suitable for use as:
- Training target for RLHF/DPO
- Baseline for comparison scoring
- Reference for prompt engineering
""",
        deliverables=[
            f"evals/{eval_module}/golden_answers/{scenario_name}.md",
        ],
        acceptance_criteria=[
            "Follows golden answer template structure",
            "All factual claims are cited to verifiable sources",
            "Calculations are shown step-by-step",
            "At least 5 specific risks are identified",
            "Clear investment recommendation with sizing rationale",
            "Passes institutional quality standards",
        ],
    )


def create_rubric_task(
    manager: TaskManager,
    eval_module: str,
    rubric_name: str,
    created_by: str,
    priority: TaskPriority = TaskPriority.MEDIUM,
) -> Task:
    """Helper to create a rubric development task."""
    return manager.create_task(
        title=f"Develop rubric: {rubric_name}",
        description=f"Create scoring rubric '{rubric_name}' for the {eval_module} module.",
        task_type=TaskType.RUBRIC_DEVELOPMENT,
        eval_module=eval_module,
        created_by=created_by,
        priority=priority,
        instructions="""
Create a detailed scoring rubric including:
1. Scoring dimensions with clear definitions
2. Point allocations and weights
3. Anchor examples for each score level
4. Critical failure criteria
5. Pass/fail thresholds

Follow the rubric design principles in docs/rubric_design_principles.md
""",
        deliverables=[
            f"evals/{eval_module}/rubrics/{rubric_name}.yaml",
        ],
        acceptance_criteria=[
            "Dimensions cover all aspects of quality",
            "Weights reflect relative importance",
            "Anchor examples are concrete and clear",
            "Critical failures are well-defined",
            "Rubric has been calibrated across examples",
        ],
    )
