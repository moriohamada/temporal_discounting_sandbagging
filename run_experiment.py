"""Run the sandbagging experiment."""

import argparse
from pathlib import Path
from inspect_ai import eval

from task import sandbagging_eval
from scenario import TIMEFRAMES
from dotenv import load_dotenv
load_dotenv(".env")


def get_existing_files(log_dir: Path, conditions: list, n_repeats: int) -> list[Path]:
    """Check for existing log files."""
    existing = []
    for rep in range(n_repeats):
        for cond, tf in conditions:
            name = f"{cond}_{tf.replace(' ', '_')}_{rep}" if tf else f"{cond}_{rep}"
            path = log_dir / f"{name}.eval"
            if path.exists():
                existing.append(path)
    return existing


def run_all_conditions(model: str, n_questions: int = 10, n_repeats: int = 1, seed: int = 0, rep_offset: int = 0):
    conditions = [("counterfactual", "6 months")] + [("sandbag", tf) for tf in TIMEFRAMES]

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Check for existing files
    existing = get_existing_files(log_dir, conditions, n_repeats)
    if existing and rep_offset == 0:
        print(f"Found {len(existing)} existing log files.")
        print("Options:")
        print("  [o] Overwrite existing files")
        print("  [N] Add offset to rep numbers (enter a number)")
        choice = input("Choice: ").strip()

        if choice.lower() == 'o':
            print("Overwriting existing files...")
        elif choice.isdigit():
            rep_offset = int(choice)
            print(f"Using rep offset of {rep_offset}")
        else:
            print("Cancelled.")
            return

    for rep in range(n_repeats):
        actual_rep = rep + rep_offset
        for cond, tf in conditions:
            name = f"{cond}_{tf.replace(' ', '_')}_{actual_rep}" if tf else f"{cond}_{actual_rep}"
            print(f"\n=== {name} ===")
            logs = eval(
                sandbagging_eval(n_questions=n_questions, condition=cond, timeframe=tf, seed=seed + actual_rep),
                model=model,
                log_dir=str(log_dir),
                name=name,
            )

            orig_path = Path(logs[0].location)
            new_path = log_dir / f"{name}.eval"
            orig_path.rename(new_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="anthropic/claude-sonnet-4-20250514")
    parser.add_argument("--n_questions", type=int, default=20)
    parser.add_argument("--n_repeats", type=int, default=100)
    parser.add_argument("--rep_offset", type=int, default=0)
    args = parser.parse_args()

    run_all_conditions(
        model=args.model,
        n_questions=args.n_questions,
        n_repeats=args.n_repeats,
        rep_offset=args.rep_offset,
    )