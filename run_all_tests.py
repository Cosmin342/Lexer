#!/usr/bin/env python3
import subprocess
import sys
import shutil
import tempfile
from pathlib import Path


def run_t2_preserving_outputs(project_dir, command):
    output_dir = project_dir / "tests" / "T2" / "out"
    output_existed = output_dir.exists()

    with tempfile.TemporaryDirectory() as temp_dir:
        backup_dir = Path(temp_dir) / "out"
        if output_existed:
            shutil.copytree(output_dir, backup_dir)

        try:
            return subprocess.run(
                command,
                cwd=project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
        finally:
            if output_dir.exists():
                shutil.rmtree(output_dir)
            if output_existed:
                shutil.copytree(backup_dir, output_dir)


def main():
    project_dir = Path(__file__).resolve().parent
    suites = [
        ("T1", [sys.executable, "Tester.py", "--stage", "1"]),
        ("T2", [sys.executable, "checker.py", "python3"]),
        ("T3", [sys.executable, "Tester.py", "--stage", "3"]),
    ]

    failed_suites = []
    for name, command in suites:
        print("\n=== Running {} tests ===".format(name), flush=True)
        if name == "T2":
            result = run_t2_preserving_outputs(project_dir, command)
        else:
            result = subprocess.run(
                command,
                cwd=project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
        output = result.stdout or ""
        print(output, end="")
        if result.returncode != 0 or "FAILED" in output or "failed [0p]" in output:
            failed_suites.append(name)

    if failed_suites:
        print("\nRunner errors in: {}".format(", ".join(failed_suites)))
        return 1

    print("\nAll test suites finished.")
    return 0


if __name__ == "__main__":
    sys.exit(main())