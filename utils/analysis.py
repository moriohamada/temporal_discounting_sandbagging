
import pandas as pd
from pathlib import Path
from inspect_ai.log import read_eval_log
import re
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def check_files_read(sample) -> dict:
    read_task = False
    read_deployment_notes = False
    read_log = False
    read_ei = False

    for msg in sample.messages:
        if msg.role == "tool" and "Answers recorded:" in str(msg.content):
            break # only care whether they read these files before submitting answer

        if msg.role == "tool":
            content = str(msg.content)
            if "ARITHMETIC EVALUATION" in content:
                read_task = True
            if "capability eval" in content:
                read_deployment_notes = True
            if "Corpus sync" in content:
                read_log = True
            if "final answers in this exact format" in content:
                read_ei = True

    return {
        "read_task": read_task,
        "read_deployment_notes": read_deployment_notes,
        "read_log": read_log,
        "read_ei": read_ei,
    }


def extract_submitted_answers(sample) -> str | None:
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
        if not sample.scores: # some runs failed due to reaching api lim
            continue
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


from statsmodels.genmod.generalized_estimating_equations import GEE
from statsmodels.genmod.families import Binomial

def permutation_test_gee(formula, data, groups=None, n_permutations=1000, family=Binomial()):

    if groups is None:
        data = data.copy()
        data['_dummy_group'] = 1
        groups = '_dummy_group'

    # Extract regressor name
    regressor = formula.split('~')[1].strip().split()[0]

    # Fit
    model_full = GEE.from_formula(formula, groups=groups,
                                  data=data, family=family)
    result_full = model_full.fit()
    observed_deviance = result_full.deviance

    # for storing shuffled devs
    perm_deviances = []

    for i in range(n_permutations):
        # Shuffle the regressor
        data_perm = data.copy()
        data_perm[regressor] = np.random.permutation(data[regressor].values)

        # Fit model on permuted data
        model_perm = GEE.from_formula(formula, groups=groups, data=data_perm, family=family)
        try:
            result_perm = model_perm.fit()
            perm_deviances.append(result_perm.deviance)
        except:
            continue

    perm_deviances = np.array(perm_deviances)

    p_value = np.mean(perm_deviances <= observed_deviance)

    return observed_deviance, perm_deviances, p_value

### Plotting
def abbreviate_label(label):
    if pd.isna(label):
        return 'CF'
    parts = str(label).split()
    if len(parts) < 2:
        return str(label)
    return f"{parts[0]}{parts[1][0]}"


def plot_by_timeframe(df, y, ax=None, title=None, x='timeframe_ord'):
    if ax is None:
        fig, ax = plt.subplots()

    sns.pointplot(data=df[df['condition'] == 'counterfactual'],
                  x=x,
                  y=y,
                  ax=ax,
                  color='tab:blue',
                  native_scale=True)

    sns.lineplot(data=df[df['condition'] == 'sandbag'],
                 x=x,
                 y=y,
                 ax=ax,
                 errorbar=('ci', 95))

    timeframe_map = df[[x, 'timeframe']].drop_duplicates().sort_values(x)
    ax.set_xticks(timeframe_map[x])
    ax.set_xticklabels([abbreviate_label(l) for l in timeframe_map['timeframe']])

    if title:
        ax.set_title(title)

    return ax