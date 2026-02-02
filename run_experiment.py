"""Run the sandbagging experiment."""

from pathlib import Path
from inspect_ai import eval

from task import sandbagging_eval
from scenario import TIMEFRAMES
from dotenv import load_dotenv
load_dotenv(".env")


def run_all_conditions(model: str, n_questions: int = 10, n_repeats: int = 1, seed: int = 42):
    conditions = [("counterfactual", None)] + [("sandbag", tf) for tf in TIMEFRAMES]

    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)

    for rep in range(n_repeats):
        for cond, tf in conditions:
            name = f"{cond}_{tf.replace(' ', '_')}_{rep}" if tf else f"{cond}_{rep}"
            print(f"\n=== {name} ===")
            logs = eval(
                sandbagging_eval(n_questions=n_questions, condition=cond, timeframe=tf, seed=seed + rep),
                model=model,
                log_dir=str(log_dir),
                name=name,
            )

            # Rename log file
            orig_path = Path(logs[0].location)
            new_path = log_dir / f"{name}.eval"
            orig_path.rename(new_path)

            if logs[0].results:
                print(f"Score: {logs[0].results.scores[0].value}")


if __name__ == "__main__":
    run_all_conditions(model="anthropic/claude-sonnet-4-20250514", n_questions=25, n_repeats=3)