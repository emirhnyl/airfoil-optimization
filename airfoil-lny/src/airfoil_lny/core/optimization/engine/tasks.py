from celery import shared_task
from pathlib import Path
import logging

from airfoil_lny.core.optimization.engine.optimizer import run_optimization

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def run_optimization_task(self, run_id: str):

    logger.info(f"🚀 Optimization started: {run_id}")

    try:
        run_dir = Path("data/runs") / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        result = run_optimization(run_dir)

        logger.info("✅ Optimization finished")

        return {
            "status": "completed",
            "run_id": run_id,
            "best_score": result["best_score"],
        }

    except Exception as e:
        logger.error(f"❌ Optimization failed: {e}")
        raise