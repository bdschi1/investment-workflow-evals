"""
Flask REST API routes for the Investment Workflow Evaluations platform.

This module provides HTTP endpoints for:
- Listing and retrieving scenarios, rubrics, and golden answers
- Submitting AI outputs for evaluation
- Managing tasks and submissions
- User authentication and profile management

To run the server:
    python -m platform.api.routes

Or with Flask:
    FLASK_APP=platform.api.routes flask run
"""

import os
from pathlib import Path
from functools import wraps

try:
    from flask import Flask, request, jsonify, g
except ImportError:
    Flask = None


def create_app(data_dir: Path = None) -> "Flask":
    """Create and configure the Flask application."""
    if Flask is None:
        raise ImportError("Flask is required for the API. Install with: pip install flask")

    app = Flask(__name__)
    app.config["DATA_DIR"] = data_dir or Path(__file__).parent.parent.parent / "data"

    # Import here to avoid circular imports
    from ..workflows.task_manager import TaskManager
    from ..workflows.review_workflow import ReviewWorkflow
    from ..workflows.payment_processor import PaymentProcessor
    from .client import EvalClient

    # Initialize services
    @app.before_request
    def init_services():
        data_dir = app.config["DATA_DIR"]
        g.task_manager = TaskManager(data_dir)
        g.review_workflow = ReviewWorkflow(data_dir)
        g.payment_processor = PaymentProcessor(data_dir)
        g.eval_client = EvalClient(data_dir=data_dir)

    # === Health Check ===

    @app.route("/health", methods=["GET"])
    def health():
        """Health check endpoint."""
        return jsonify({"status": "healthy", "version": "0.1.0"})

    # === Modules ===

    @app.route("/api/v1/modules", methods=["GET"])
    def list_modules():
        """List all evaluation modules."""
        modules = g.eval_client.list_modules()
        return jsonify({"modules": modules})

    # === Scenarios ===

    @app.route("/api/v1/scenarios", methods=["GET"])
    def list_scenarios():
        """List all scenarios, optionally filtered by module."""
        module = request.args.get("module")
        scenarios = g.eval_client.list_scenarios(module=module)
        return jsonify({"scenarios": scenarios})

    @app.route("/api/v1/scenarios/<scenario_id>", methods=["GET"])
    def get_scenario(scenario_id: str):
        """Get a specific scenario by ID."""
        try:
            scenario = g.eval_client.get_scenario(scenario_id)
            return jsonify(scenario)
        except FileNotFoundError:
            return jsonify({"error": f"Scenario not found: {scenario_id}"}), 404

    # === Rubrics ===

    @app.route("/api/v1/rubrics/<rubric_id>", methods=["GET"])
    def get_rubric(rubric_id: str):
        """Get a specific rubric by ID."""
        try:
            rubric = g.eval_client.get_rubric(rubric_id)
            return jsonify(rubric)
        except FileNotFoundError:
            return jsonify({"error": f"Rubric not found: {rubric_id}"}), 404

    # === Golden Answers ===

    @app.route("/api/v1/golden-answers", methods=["GET"])
    def list_golden_answers():
        """
        List golden answers for training.

        Query params:
            module: Filter by module
            min_quality_score: Minimum quality score (0-100)
            limit: Maximum results (default 100)
        """
        module = request.args.get("module")
        min_score = float(request.args.get("min_quality_score", 0))
        limit = int(request.args.get("limit", 100))

        golden_answers = g.eval_client.get_golden_answers(
            module=module,
            min_quality_score=min_score,
            limit=limit,
        )

        return jsonify({
            "golden_answers": [
                {
                    "id": ga.id,
                    "module": ga.module,
                    "scenario_name": ga.scenario_name,
                    "content": ga.content,
                    "quality_score": ga.quality_score,
                    "metadata": ga.metadata,
                }
                for ga in golden_answers
            ]
        })

    # === Evaluation ===

    @app.route("/api/v1/evaluate", methods=["POST"])
    def evaluate():
        """
        Evaluate AI output against a scenario.

        Request body:
            scenario_id: ID of the scenario
            ai_output: The AI-generated response
            rubric_id: (optional) Specific rubric to use
        """
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body required"}), 400

        scenario_id = data.get("scenario_id")
        ai_output = data.get("ai_output")

        if not scenario_id or not ai_output:
            return jsonify({"error": "scenario_id and ai_output are required"}), 400

        result = g.eval_client.evaluate(
            scenario_id=scenario_id,
            ai_output=ai_output,
            rubric_id=data.get("rubric_id"),
            return_detailed_scores=data.get("return_detailed_scores", False),
        )

        return jsonify({
            "scenario_id": result.scenario_id,
            "overall_score": result.overall_score,
            "dimension_scores": result.dimension_scores,
            "passed": result.passed,
            "critical_failures": result.critical_failures,
            "feedback": result.feedback,
        })

    # === Tasks ===

    @app.route("/api/v1/tasks", methods=["GET"])
    def list_tasks():
        """
        List tasks.

        Query params:
            status: Filter by status
            module: Filter by module
            type: Filter by task type
        """
        from ..models.task import TaskStatus, TaskType

        status = request.args.get("status")
        module = request.args.get("module")
        task_type = request.args.get("type")

        tasks = g.task_manager.list_tasks(
            status=TaskStatus(status) if status else None,
            eval_module=module,
            task_type=TaskType(task_type) if task_type else None,
        )

        return jsonify({
            "tasks": [t.to_dict() for t in tasks]
        })

    @app.route("/api/v1/tasks/<task_id>", methods=["GET"])
    def get_task(task_id: str):
        """Get a specific task by ID."""
        task = g.task_manager.get_task(task_id)
        if not task:
            return jsonify({"error": f"Task not found: {task_id}"}), 404
        return jsonify(task.to_dict())

    @app.route("/api/v1/tasks", methods=["POST"])
    def create_task():
        """
        Create a new task (admin only).

        Request body:
            title: Task title
            description: Task description
            task_type: Type of task
            eval_module: Associated module
            priority: (optional) Priority level
        """
        from ..models.task import TaskType, TaskPriority

        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body required"}), 400

        required = ["title", "description", "task_type", "eval_module"]
        for field in required:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        try:
            task = g.task_manager.create_task(
                title=data["title"],
                description=data["description"],
                task_type=TaskType(data["task_type"]),
                eval_module=data["eval_module"],
                created_by="api",
                priority=TaskPriority(data["priority"]) if data.get("priority") else TaskPriority.MEDIUM,
                instructions=data.get("instructions", ""),
                deliverables=data.get("deliverables", []),
                acceptance_criteria=data.get("acceptance_criteria", []),
            )
            return jsonify(task.to_dict()), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/api/v1/tasks/<task_id>/claim", methods=["POST"])
    def claim_task(task_id: str):
        """Claim a task for the authenticated user."""
        data = request.get_json() or {}
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        success, message = g.task_manager.claim_task(task_id, user_id)

        if success:
            return jsonify({"success": True, "message": message})
        else:
            return jsonify({"success": False, "error": message}), 400

    @app.route("/api/v1/tasks/<task_id>/submit", methods=["POST"])
    def submit_task(task_id: str):
        """Submit completed work for a task."""
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body required"}), 400

        user_id = data.get("user_id")
        file_path = data.get("file_path")

        if not user_id or not file_path:
            return jsonify({"error": "user_id and file_path are required"}), 400

        success, message = g.task_manager.submit_task(
            task_id, user_id, file_path, data.get("notes")
        )

        if success:
            return jsonify({"success": True, "message": message})
        else:
            return jsonify({"success": False, "error": message}), 400

    # === Submissions ===

    @app.route("/api/v1/submissions", methods=["GET"])
    def list_submissions():
        """List submissions pending review."""
        submissions = g.review_workflow.get_submissions_pending_review()
        return jsonify({
            "submissions": [s.to_dict() for s in submissions]
        })

    # === Statistics ===

    @app.route("/api/v1/stats", methods=["GET"])
    def get_stats():
        """Get platform statistics."""
        task_stats = g.task_manager.get_task_statistics()
        review_stats = g.review_workflow.get_review_statistics()
        payment_stats = g.payment_processor.get_payment_statistics()

        return jsonify({
            "tasks": task_stats,
            "reviews": review_stats,
            "payments": payment_stats,
        })

    # === Preference Pairs (for DPO) ===

    @app.route("/api/v1/preference-pairs", methods=["GET"])
    def get_preference_pairs():
        """
        Get preference pairs for DPO training.

        Query params:
            module: Filter by module
            limit: Maximum pairs (default 1000)
            min_score_delta: Minimum score difference (default 10)
        """
        module = request.args.get("module")
        limit = int(request.args.get("limit", 1000))
        min_delta = float(request.args.get("min_score_delta", 10))

        pairs = g.eval_client.get_preference_pairs(
            module=module,
            limit=limit,
            min_score_delta=min_delta,
        )

        return jsonify({
            "pairs": [
                {
                    "prompt": p.prompt,
                    "chosen": p.chosen,
                    "rejected": p.rejected,
                    "scenario_id": p.scenario_id,
                    "metadata": p.metadata,
                }
                for p in pairs
            ]
        })

    # === Enterprise Client Endpoints ===

    @app.route("/api/v1/experts", methods=["GET"])
    def list_experts():
        """
        List available experts with matching scores for requirements.

        Query params:
            sectors: Comma-separated sector requirements
            min_experience: Minimum years experience
            credentials: Required credentials (CFA, CPA, etc.)
            min_quality: Minimum quality score
            available_only: Only show available experts
        """
        from ..workflows.expert_matching import ExpertMatcher

        matcher = ExpertMatcher(app.config["DATA_DIR"])

        # Build requirements from query params
        sectors = request.args.get("sectors", "").split(",") if request.args.get("sectors") else []
        credentials = request.args.get("credentials", "").split(",") if request.args.get("credentials") else []
        min_experience = int(request.args.get("min_experience", 0))
        min_quality = float(request.args.get("min_quality", 0))

        # Get all users and filter
        users = matcher._load_users()

        experts = []
        for user in users:
            if not user.is_active:
                continue
            if min_quality and user.average_quality_score < min_quality:
                continue

            experts.append({
                "id": user.id,
                "name": user.name,
                "tier": user.tier.value,
                "expertise": [e.value for e in user.expertise],
                "quality_score": user.average_quality_score,
                "tasks_completed": user.approved_submissions,
                "is_verified": user.is_verified,
            })

        return jsonify({"experts": experts, "count": len(experts)})

    @app.route("/api/v1/experts/<expert_id>/match", methods=["POST"])
    def match_expert_to_task(expert_id: str):
        """Check if an expert matches task requirements."""
        from ..workflows.expert_matching import ExpertMatcher

        data = request.get_json() or {}
        task_id = data.get("task_id")

        if not task_id:
            return jsonify({"error": "task_id required"}), 400

        matcher = ExpertMatcher(app.config["DATA_DIR"])
        task = g.task_manager.get_task(task_id)

        if not task:
            return jsonify({"error": "Task not found"}), 404

        matches = matcher.find_experts_for_task(task, limit=20)
        expert_match = next((m for m in matches if m.expert_id == expert_id), None)

        if expert_match:
            return jsonify({
                "matches": True,
                "score": expert_match.match_score,
                "reasons": expert_match.match_reasons,
                "hourly_rate": expert_match.hourly_rate,
            })
        else:
            return jsonify({"matches": False, "score": 0, "reasons": []})

    @app.route("/api/v1/projects", methods=["POST"])
    def create_project():
        """
        Create a new enterprise project.

        Request body:
            name: Project name
            description: Project description
            project_type: Type (rlhf_data, dpo_pairs, eval_framework, etc.)
            target_deliverables: Number of deliverables needed
            budget_total: Total budget
            eval_modules: List of modules to cover
        """
        from ..models.project import Project, ProjectType, ProjectStatus

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body required"}), 400

        project = Project(
            name=data.get("name", ""),
            description=data.get("description", ""),
            client_name=data.get("client_name", ""),
            client_contact_email=data.get("client_contact_email", ""),
            project_type=ProjectType(data.get("project_type", "eval_framework")),
            status=ProjectStatus.DRAFT,
            target_deliverables=data.get("target_deliverables", 0),
            budget_total=data.get("budget_total", 0),
            eval_modules=data.get("eval_modules", []),
        )

        # Would save to database in production
        return jsonify(project.to_dict()), 201

    @app.route("/api/v1/time-entries", methods=["POST"])
    def log_time():
        """
        Log time worked by an expert.

        Request body:
            expert_id: Expert ID
            duration_hours: Hours worked
            description: Work description
            work_type: Type of work
            task_id: (optional) Associated task
            project_id: (optional) Associated project
        """
        from ..workflows.hourly_tracking import TimeTracker

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body required"}), 400

        tracker = TimeTracker(app.config["DATA_DIR"])

        entry = tracker.log_time(
            expert_id=data.get("expert_id", ""),
            duration_hours=data.get("duration_hours", 0),
            description=data.get("description", ""),
            work_type=data.get("work_type", "general"),
            task_id=data.get("task_id"),
            project_id=data.get("project_id"),
            hourly_rate=data.get("hourly_rate"),
        )

        return jsonify(entry.to_dict()), 201

    @app.route("/api/v1/billing/summary", methods=["GET"])
    def get_billing_summary():
        """
        Get billing summary for time entries.

        Query params:
            expert_id: Filter by expert
            project_id: Filter by project
            start_date: Start of period (YYYY-MM-DD)
            end_date: End of period (YYYY-MM-DD)
        """
        from ..workflows.hourly_tracking import TimeTracker

        tracker = TimeTracker(app.config["DATA_DIR"])

        summary = tracker.get_billing_summary(
            expert_id=request.args.get("expert_id"),
            project_id=request.args.get("project_id"),
            start_date=request.args.get("start_date"),
            end_date=request.args.get("end_date"),
        )

        return jsonify(summary)

    @app.route("/api/v1/training-data/export", methods=["GET"])
    def export_training_data():
        """
        Export approved training data for AI model training.

        Query params:
            module: Filter by module
            format: Export format (jsonl, parquet)
            min_quality: Minimum quality score
            include_rejected: Include rejected for DPO pairs
        """
        module = request.args.get("module")
        export_format = request.args.get("format", "jsonl")
        min_quality = float(request.args.get("min_quality", 85))

        # Get approved golden answers
        golden_answers = g.eval_client.get_golden_answers(
            module=module,
            min_quality_score=min_quality,
        )

        # Format for training
        training_data = []
        for ga in golden_answers:
            training_data.append({
                "scenario_id": ga.scenario_name,
                "module": ga.module,
                "prompt": f"Analyze {ga.scenario_name}",  # Would load actual prompt
                "response": ga.content,
                "quality_score": ga.quality_score,
            })

        return jsonify({
            "format": export_format,
            "count": len(training_data),
            "data": training_data,
        })

    return app


def main():
    """Run the API server."""
    app = create_app()
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("DEBUG", "false").lower() == "true"

    print(f"Starting Investment Workflow Evaluations API on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":
    main()
