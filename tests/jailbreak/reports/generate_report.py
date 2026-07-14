# reports/generate_report.py
import json
from datetime import datetime
from pathlib import Path

def generate_report(results: Dict, output_dir: Path = Path("./reports")):
    output_dir.mkdir(exist_ok=True)

    # Human-readable report
    report_path = output_dir / f"jailbreak_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_path, "w") as f:
        f.write(f"# Jailbreak Test Report\n\n")
        f.write(f"**Suite:** {results['suite']}\n")
        f.write(f"**Model:** {results['model']}\n")
        f.write(f"**Timestamp:** {results['timestamp']}\n\n")

        f.write("## Summary\n\n")
        f.write(f"- Total Turns: {len(results['tests'])}\n")
        f.write(f"- Refusals: {results['summary'].get('refusals', 0)}\n")
        f.write(f"- Status: {results['summary'].get('status', 'FAIL')}\n\n")

        f.write("## Turn-by-Turn Results\n\n")
        for test in results["tests"]:
            f.write(f"### Turn {test['turn']}\n\n")
            f.write(f"**Prompt:** {test['prompt'][:100]}...\n\n")
            f.write(f"**Response:** {test['response'][:200]}...\n\n")
            f.write(f"**Judgment:** {test['judgment']}\n\n")
            f.write("---\n\n")

    # Machine-readable JSON
    json_path = output_dir / f"jailbreak_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)

    return report_path, json_path
