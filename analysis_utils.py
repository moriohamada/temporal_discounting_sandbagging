
import pandas as pd
from pathlib import Path
from inspect_ai.log import read_eval_log
import re
import seaborn as sns
import matplotlib.pyplot as plt

def check_files_read(sample) -> dict:
    """Check which files agent read before submitting answers."""
    read_task = False
    read_deployment_notes = False
    read_ei = False

    for msg in sample.messages:
        if msg.role == "tool" and "Answers recorded:" in str(msg.content):
            break

        if msg.role == "tool":
            content = str(msg.content)
            if "ARITHMETIC EVALUATION" in content:
                read_task = True
            if "capability eval" in content:
                read_deployment_notes = True
            if "final answers in this exact format" in content:
                read_ei = True

    return {
        "read_task": read_task,
        "read_deployment_notes": read_deployment_notes,
        "read_ei": read_ei,
    }


def extract_submitted_answers(sample) -> str | None:
    """Get answers from submit_answers tool call."""
    for msg in sample.messages:
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            for tc in msg.tool_calls:
                if tc.function == "submit_answers":
                    return tc.arguments.get('answers', '')
    return None


def extract_responses(sample) -> tuple[str, str]:
    initial, followup = [], []
    seen_followup = False

    for msg in sample.messages:
        if msg.role == "user" and "before we finish" in str(msg.content).lower():
            seen_followup = True
        elif msg.role == "assistant" and isinstance(msg.content, list):
            for item in msg.content:
                if hasattr(item, 'text') and item.text:
                    (followup if seen_followup else initial).append(item.text)

    return "\n".join(initial), "\n".join(followup)


def timeframe_to_days(tf: str | None) -> float | None:
    if tf is None:
        return 0

    match = re.match(r'(\d+(?:\.\d+)?)\s*(hour|day|week|month|year)s?',
                     tf.lower().strip())
    if not match:
        return None

    number = float(match.group(1))
    unit = match.group(2)
    conversions = {
        'hour': 1 / 24,
        'day': 1,
        'week': 7,
        'month': 30,
        'year': 365
    }
    return number * conversions.get(unit)


def load_results(log_dir: str = "./logs") -> pd.DataFrame:
    rows = []

    for path in Path(log_dir).glob("*.eval"):

        if "-eval_" in path.name:  # unfinished run
            continue

        rep = int(path.stem.rsplit("_", 1)[1])

        log = read_eval_log(str(path))
        if not log.samples:
            print(f"Skipping {path} - no samples")
            continue

        sample = log.samples[0]
        name, _ = path.stem.rsplit("_", 1)
        condition = "counterfactual" if "counterfactual" in name else "sandbag"
        timeframe = None if "counterfactual" in name else name.replace("sandbag_", "").replace("_", " ")
        initial, followup = extract_responses(sample)
        files_read = check_files_read(sample)

        rows.append({
            "condition": condition,
            "timeframe": timeframe,
            "timeframe_days": timeframe_to_days(timeframe),
            "repeat": rep,
            "score": list(sample.scores.values())[0].value if sample.scores else None,
            "submitted_answers": extract_submitted_answers(sample),
            "initial_response": initial,
            "followup_response": followup,
            **files_read,
        })

    return pd.DataFrame(rows)

### Plotting
def abbreviate_label(label):
    if pd.isna(label):
        return 'CF'
    parts = str(label).split()
    if len(parts) < 2:
        return str(label)
    return f"{parts[0]}{parts[1][0]}"


def plot_by_timeframe(df, y, ax=None, title=None, x='timeframe_ord'):
    """Plot y variable by timeframe, with CF as separate point."""
    if ax is None:
        fig, ax = plt.subplots()

    # Point for CF
    sns.pointplot(data=df[df['condition'] == 'counterfactual'],
                  x=x,
                  y=y,
                  ax=ax,
                  color='tab:blue',
                  native_scale=True)

    # Line for sandbag conditions
    sns.lineplot(data=df[df['condition'] == 'sandbag'],
                 x=x,
                 y=y,
                 ax=ax,
                 errorbar=('ci', 95))

    # Set x labels
    timeframe_map = df[[x, 'timeframe']].drop_duplicates().sort_values(x)
    ax.set_xticks(timeframe_map[x])
    ax.set_xticklabels([abbreviate_label(l) for l in timeframe_map['timeframe']])

    if title:
        ax.set_title(title)

    return ax