import argparse
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
KB_DIR = ROOT_DIR / "LogicRAG_Data" / "precomputed_knowledge_base" / "kb_out_kitti"
RESULTS_CSV = ROOT_DIR / "resultados_kitti.csv"
ENV_FILE = ROOT_DIR / ".env"


def run_step(script_name, description):
    script_path = ROOT_DIR / script_name
    command = [sys.executable, str(script_path)]

    print("\n" + "=" * 70)
    print(f"STEP: {description}")
    print(f"Command: {' '.join(command)}")
    print("=" * 70 + "\n")

    subprocess.run(command, cwd=ROOT_DIR, check=True)


def validate_inputs(skip_parse, skip_agent):
    if not skip_parse and not KB_DIR.exists():
        print(f"Error: LogicRAG data folder not found: {KB_DIR}")
        print("Copy or extract LogicRAG_Data into the LogicRAG folder before running the demo.")
        return False

    if skip_parse and not RESULTS_CSV.exists():
        print(f"Error: results CSV not found: {RESULTS_CSV}")
        print("Run without --skip-parse first, or create resultados_kitti.csv.")
        return False

    if not skip_agent and not ENV_FILE.exists():
        print(f"Error: .env file not found: {ENV_FILE}")
        print("Create LogicRAG/.env with the IAedu API values before calling the agent.")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(description="Run the LogicRAG + IAedu driving demo.")
    parser.add_argument("--skip-parse", action="store_true", help="Reuse existing resultados_kitti.csv.")
    parser.add_argument("--skip-agent", action="store_true", help="Only generate resultados_kitti.csv; do not call IAedu.")
    args = parser.parse_args()

    print("\n" + "#" * 70)
    print("LogicRAG + IAedu demo")
    print("#" * 70)

    if not validate_inputs(args.skip_parse, args.skip_agent):
        return 1

    try:
        if not args.skip_parse:
            run_step(
                "parse_kb_to_csv.py",
                "Translate precomputed LogicRAG knowledge-base files into natural-language facts",
            )

        if not args.skip_agent:
            run_step(
                "driving_agent.py",
                "Send the latest LogicRAG fact to the IAedu driving assistant",
            )

    except subprocess.CalledProcessError as error:
        print(f"\nDemo failed while running: {error.cmd}")
        return error.returncode or 1

    print("\nLogicRAG demo finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
