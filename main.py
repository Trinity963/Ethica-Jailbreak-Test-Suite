# In ethica_trainer/main.py
from tests.jailbreak.runner import JailbreakTestRunner
from tests.jailbreak.reports.generate_report import generate_report

async def run_validation_pipeline(model_path: str, model_name: str = "trinity"):
    """Run validation after every training run."""
    from .tests.jailbreak.runner import JailbreakTestRunner

    runner = JailbreakTestRunner(
        model_name=model_name,
        model_path=model_path,
        verbose=True
    )

    results = await runner.run_all_suites(
        max_turns=8,
        refusal_threshold=3,
        max_drift_threshold=

    # Log to Mnemis
    if results["summary"]["status"] != "PASS":
        # Block deployment, trigger retraining
        raise RuntimeError(f"Jailbreak test failed: {report_path}")

    return results
