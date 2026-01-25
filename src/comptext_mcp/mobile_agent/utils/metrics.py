"""
Metrics collection for Mobile Agent.

Tracks token usage, latency, costs, and CompText optimization performance.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class TaskMetrics:
    """Metrics for a single task execution."""
    task_id: str
    task_description: str
    started_at: datetime
    completed_at: Optional[datetime] = None

    # Token metrics
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    # CompText comparison
    baseline_tokens: int = 0  # Estimated without CompText
    comptext_tokens: int = 0  # Actual with CompText
    token_reduction_percent: float = 0.0

    # Performance
    steps_count: int = 0
    successful_steps: int = 0
    failed_steps: int = 0
    total_duration_ms: float = 0.0
    avg_step_duration_ms: float = 0.0

    # Cost estimation (based on Ollama Cloud pricing)
    estimated_cost_usd: float = 0.0

    # Status
    success: bool = False
    error: Optional[str] = None


@dataclass
class PerformanceMetrics:
    """Aggregated performance metrics."""
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0

    total_tokens: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0

    total_baseline_tokens: int = 0
    total_comptext_tokens: int = 0
    avg_token_reduction_percent: float = 0.0

    total_duration_ms: float = 0.0
    avg_task_duration_ms: float = 0.0
    avg_step_duration_ms: float = 0.0

    total_steps: int = 0
    successful_steps: int = 0

    total_cost_usd: float = 0.0
    avg_cost_per_task_usd: float = 0.0

    # Success rates
    task_success_rate: float = 0.0
    step_success_rate: float = 0.0


class TokenMetricsCollector:
    """
    Collects and aggregates token usage metrics.

    Enables comparison between baseline (verbose) and CompText-optimized prompts.
    """

    # Ollama Cloud pricing (estimated, per 1M tokens)
    PRICING = {
        "qwen3-coder:480b": {"input": 0.50, "output": 1.50},
        "deepseek-v3.2:671b": {"input": 0.60, "output": 1.80},
        "nemotron-3-nano:30b": {"input": 0.05, "output": 0.15},
    }

    def __init__(self, model: str = "qwen3-coder:480b"):
        self.model = model
        self.tasks: list[TaskMetrics] = []
        self._current_task: Optional[TaskMetrics] = None

    def start_task(self, task_id: str, description: str) -> TaskMetrics:
        """Start tracking a new task."""
        task = TaskMetrics(
            task_id=task_id,
            task_description=description,
            started_at=datetime.now(),
        )
        self._current_task = task
        return task

    def record_step(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        duration_ms: float,
        success: bool,
        baseline_tokens: Optional[int] = None,
    ):
        """Record metrics for a single step."""
        if not self._current_task:
            return

        task = self._current_task
        task.prompt_tokens += prompt_tokens
        task.completion_tokens += completion_tokens
        task.total_tokens += prompt_tokens + completion_tokens
        task.steps_count += 1

        if success:
            task.successful_steps += 1
        else:
            task.failed_steps += 1

        task.total_duration_ms += duration_ms

        # CompText comparison
        if baseline_tokens:
            task.baseline_tokens += baseline_tokens
            task.comptext_tokens += prompt_tokens

    def complete_task(self, success: bool, error: Optional[str] = None):
        """Complete current task tracking."""
        if not self._current_task:
            return

        task = self._current_task
        task.completed_at = datetime.now()
        task.success = success
        task.error = error

        # Calculate averages
        if task.steps_count > 0:
            task.avg_step_duration_ms = task.total_duration_ms / task.steps_count

        # Calculate token reduction
        if task.baseline_tokens > 0:
            task.token_reduction_percent = (
                (task.baseline_tokens - task.comptext_tokens)
                / task.baseline_tokens
                * 100
            )

        # Estimate cost
        task.estimated_cost_usd = self._calculate_cost(
            task.prompt_tokens,
            task.completion_tokens,
        )

        self.tasks.append(task)
        self._current_task = None

    def get_performance_metrics(self) -> PerformanceMetrics:
        """Get aggregated performance metrics."""
        if not self.tasks:
            return PerformanceMetrics()

        metrics = PerformanceMetrics(
            total_tasks=len(self.tasks),
            successful_tasks=sum(1 for t in self.tasks if t.success),
            failed_tasks=sum(1 for t in self.tasks if not t.success),
            total_tokens=sum(t.total_tokens for t in self.tasks),
            total_prompt_tokens=sum(t.prompt_tokens for t in self.tasks),
            total_completion_tokens=sum(t.completion_tokens for t in self.tasks),
            total_baseline_tokens=sum(t.baseline_tokens for t in self.tasks),
            total_comptext_tokens=sum(t.comptext_tokens for t in self.tasks),
            total_duration_ms=sum(t.total_duration_ms for t in self.tasks),
            total_steps=sum(t.steps_count for t in self.tasks),
            successful_steps=sum(t.successful_steps for t in self.tasks),
            total_cost_usd=sum(t.estimated_cost_usd for t in self.tasks),
        )

        # Calculate averages
        if metrics.total_tasks > 0:
            metrics.avg_task_duration_ms = metrics.total_duration_ms / metrics.total_tasks
            metrics.avg_cost_per_task_usd = metrics.total_cost_usd / metrics.total_tasks
            metrics.task_success_rate = metrics.successful_tasks / metrics.total_tasks * 100

        if metrics.total_steps > 0:
            metrics.avg_step_duration_ms = metrics.total_duration_ms / metrics.total_steps
            metrics.step_success_rate = metrics.successful_steps / metrics.total_steps * 100

        if metrics.total_baseline_tokens > 0:
            metrics.avg_token_reduction_percent = (
                (metrics.total_baseline_tokens - metrics.total_comptext_tokens)
                / metrics.total_baseline_tokens
                * 100
            )

        return metrics

    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate estimated cost in USD."""
        pricing = self.PRICING.get(self.model, self.PRICING["qwen3-coder:480b"])
        input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def get_comparison_report(self) -> str:
        """Generate a comparison report between baseline and CompText."""
        metrics = self.get_performance_metrics()

        report = [
            "=" * 60,
            "CompText Mobile Agent - Performance Report",
            "=" * 60,
            "",
            f"Total Tasks: {metrics.total_tasks}",
            f"Success Rate: {metrics.task_success_rate:.1f}%",
            "",
            "--- Token Usage ---",
            f"Total Tokens: {metrics.total_tokens:,}",
            f"  - Prompt: {metrics.total_prompt_tokens:,}",
            f"  - Completion: {metrics.total_completion_tokens:,}",
            "",
            "--- CompText Optimization ---",
            f"Baseline Tokens (estimated): {metrics.total_baseline_tokens:,}",
            f"CompText Tokens (actual): {metrics.total_comptext_tokens:,}",
            f"Token Reduction: {metrics.avg_token_reduction_percent:.1f}%",
            "",
            "--- Performance ---",
            f"Total Duration: {metrics.total_duration_ms/1000:.2f}s",
            f"Avg Task Duration: {metrics.avg_task_duration_ms/1000:.2f}s",
            f"Avg Step Duration: {metrics.avg_step_duration_ms:.0f}ms",
            "",
            "--- Cost Analysis ---",
            f"Total Cost: ${metrics.total_cost_usd:.4f}",
            f"Avg Cost/Task: ${metrics.avg_cost_per_task_usd:.4f}",
            f"Model: {self.model}",
            "",
            "=" * 60,
        ]

        return "\n".join(report)

    def export_csv(self, filepath: str):
        """Export task metrics to CSV."""
        import csv

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "task_id",
                "description",
                "started_at",
                "completed_at",
                "success",
                "steps",
                "prompt_tokens",
                "completion_tokens",
                "total_tokens",
                "baseline_tokens",
                "comptext_tokens",
                "token_reduction_pct",
                "duration_ms",
                "cost_usd",
                "error",
            ])

            for task in self.tasks:
                writer.writerow([
                    task.task_id,
                    task.task_description[:50],
                    task.started_at.isoformat(),
                    task.completed_at.isoformat() if task.completed_at else "",
                    task.success,
                    task.steps_count,
                    task.prompt_tokens,
                    task.completion_tokens,
                    task.total_tokens,
                    task.baseline_tokens,
                    task.comptext_tokens,
                    f"{task.token_reduction_percent:.1f}",
                    f"{task.total_duration_ms:.0f}",
                    f"{task.estimated_cost_usd:.4f}",
                    task.error or "",
                ])
