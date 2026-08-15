"""Run the self-contained reproducible subset that needs no paper dataset."""

from __future__ import annotations

import subprocess
import sys


def main() -> None:
    commands = [
        [
            sys.executable,
            "experiments/reproduce_core.py",
            "--input",
            "examples/assets/demo_64.png",
            "--config",
            "configs/paper_default.json",
        ],
        [
            sys.executable,
            "experiments/run_sbox_analysis.py",
            "--paper-table-i",
            "--output",
            "results/generated/paper_sbox_metrics.json",
        ],
        [sys.executable, "experiments/run_chaos_analysis.py"],
    ]
    for command in commands:
        print("+", " ".join(command), flush=True)
        subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
