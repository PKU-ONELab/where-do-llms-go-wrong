import os
import json
import re
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.stats import wilcoxon, t
from statsmodels.stats.weightstats import ttest_ind

# For nominal agreement:
from sklearn.metrics import cohen_kappa_score, confusion_matrix

plt.rcParams['font.family'] = 'STIXGeneral'

# ------------------------------
# Data Loading Functions
# ------------------------------

def jsonl_to_dataframe(file_path: str) -> pd.DataFrame:
    """Reads a JSONL file and converts it to a pandas DataFrame."""
    try:
        data = []
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():
                    try:
                        json_obj = json.loads(line)
                        data.append(json_obj)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON in {file_path}: {e}\nLine: {line}")
        return pd.DataFrame(data)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"An unexpected error occurred while reading {file_path}: {e}")
        return pd.DataFrame()


def get_all_jsonl_file_in_directory(directory: str) -> list:
    """Gets all JSONL file paths in the directory."""
    try:
        return [
            os.path.join(directory, file)
            for file in os.listdir(directory)
            if file.endswith('.jsonl')
        ]
    except FileNotFoundError:
        print(f"Error: Directory not found: {directory}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while listing files in {directory}: {e}")
        return []

def parse_file_info(file_name: str) -> dict:
    """Parses public-release and legacy score filenames."""
    public_baseline = r"baseline__target-(meta-review|review)__prompt-([a-zA-Z0-9-]+)\.jsonl$"
    match = re.search(public_baseline, file_name)
    if match:
        return {"type": "baseline", "review_type": match.group(1), "prompt_setting": match.group(2)}

    public_perturbed = r"perturbed__source-([a-zA-Z]+)__aspect-([a-zA-Z]+)__target-(meta-review|review)__prompt-([a-zA-Z0-9-]+)\.jsonl$"
    match = re.search(public_perturbed, file_name)
    if match:
        return {
            "type": "perturbation",
            "review_type": match.group(3),
            "prompt_setting": match.group(4),
            "perturbation_type": f"{match.group(1)}_{match.group(2)}",
        }

    # Backward-compatible parser for original experiment filenames.
    baseline_pattern = r"output_test_base_input_(meta-review|review)_(.+)_overall"
    match = re.search(baseline_pattern, file_name)
    if match:
        return {"type": "baseline", "review_type": match.group(1), "prompt_setting": match.group(2)}

    pert_pattern = r"test_([a-zA-Z]+)_([a-zA-Z]+)_perturbed_(meta-review|review)_(.+)_overall"
    match = re.search(pert_pattern, file_name)
    if match:
        return {
            "type": "perturbation",
            "review_type": match.group(3),
            "prompt_setting": match.group(4),
            "perturbation_type": f"{match.group(1)}_{match.group(2)}",
        }

    alt_pattern = r"output_test_([a-zA-Z]+)_perturbed_(meta-review|review)_(.+)_overall"
    match = re.search(alt_pattern, file_name)
    if match:
        return {
            "type": "perturbation",
            "review_type": match.group(2),
            "prompt_setting": match.group(3),
            "perturbation_type": match.group(1),
        }

    return None


def load_data(directory: str):
    """Loads all JSONL files, separates into baseline and perturbation DataFrames."""
    file_paths = get_all_jsonl_file_in_directory(directory)
    baseline_dfs = []
    perturb_dfs = []

    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        info = parse_file_info(file_name)
        if info is None:
            print(f"Skipping unrecognized file: {file_name}")
            continue

        df = jsonl_to_dataframe(file_path)
        if df.empty:
            continue

        df["source_file"] = file_name
        df["review_type"] = info.get("review_type", None)     # e.g. "meta-review" or "review"
        df["prompt_setting"] = info.get("prompt_setting", None)
        if info["type"] == "perturbation":
            df["perturbation_type"] = info["perturbation_type"]
            perturb_dfs.append(df)
        else:
            # Baseline
            df["perturbation_type"] = None
            baseline_dfs.append(df)

    baseline_df = pd.concat(baseline_dfs, ignore_index=True) if baseline_dfs else pd.DataFrame()
    perturb_df = pd.concat(perturb_dfs, ignore_index=True) if perturb_dfs else pd.DataFrame()

    return baseline_df, perturb_df

# ------------------------------
# Directional + TOST Test
# ------------------------------

def compare_scores_3way(before, after, delta=1.0, alpha=0.05):
    """
    Compare 'before' vs. 'after' scores to decide among:
      (1) before > after
      (2) before < after
      (3) no significant difference (before ~ after).

    Then, if no difference, check equivalence within ±delta using TOST.
    """
    before_arr = np.array(before, dtype=float)
    after_arr  = np.array(after, dtype=float)
    assert len(before_arr) == len(after_arr), "Both arrays must have the same length."

    differences = before_arr - after_arr
    n = len(differences)

    mean_diff = np.mean(differences)
    std_diff  = np.std(differences, ddof=1)

    # If all identical
    if std_diff == 0.0:
        direction_conclusion = "no significant difference (before ~ after)"
        if abs(mean_diff) <= delta:
            tost_conclusion = f"Equivalent within ±{delta} (TOST)."
            direction_conclusion += " AND they are EQUIVALENT."
        else:
            tost_conclusion = f"Not equivalent within ±{delta} (TOST)."
        return {
            "wilcoxon_stat_greater": None,
            "wilcoxon_p_greater": None,
            "wilcoxon_stat_less": None,
            "wilcoxon_p_less": None,
            "direction_conclusion": direction_conclusion,
            "mean_diff": mean_diff,
            "std_diff": std_diff,
            "TOST_p_lower": None,
            "TOST_p_upper": None,
            "TOST_conclusion": tost_conclusion
        }

    # Wilcoxon: 'greater' and 'less'
    stat_greater, p_greater = wilcoxon(differences, alternative='greater')
    stat_less,    p_less    = wilcoxon(differences, alternative='less')

    if (p_greater < alpha) and (p_less < alpha):
        direction_conclusion = (
            "INCONSISTENT result: both Wilcoxon tests are significant."
            " (Check data for anomalies or many ties.)"
        )
        return {
            "wilcoxon_stat_greater": stat_greater,
            "wilcoxon_p_greater": p_greater,
            "wilcoxon_stat_less": stat_less,
            "wilcoxon_p_less": p_less,
            "direction_conclusion": direction_conclusion,
            "mean_diff": mean_diff,
            "std_diff": std_diff,
            "TOST_p_lower": None,
            "TOST_p_upper": None,
            "TOST_conclusion": None
        }
    elif p_greater < alpha:
        direction_conclusion = "before > after"
    elif p_less < alpha:
        direction_conclusion = "before < after"
    else:
        direction_conclusion = "no significant difference (before ~ after)"

    # If "no significant difference," run TOST
    if direction_conclusion.startswith("no significant difference"):
        import math
        se = std_diff / math.sqrt(n)
        t_lower = (mean_diff + delta) / se
        t_upper = (mean_diff - delta) / se
        from scipy.stats import t
        p_lower = 1 - t.cdf(t_lower, df=n-1)
        p_upper = t.cdf(t_upper, df=n-1)

        if (p_lower < alpha) and (p_upper < alpha):
            tost_conclusion = f"Equivalent within ±{delta} (TOST)."
            direction_conclusion += " AND they are EQUIVALENT."
        else:
            tost_conclusion = f"Not equivalent within ±{delta} (TOST)."

        return {
            "wilcoxon_stat_greater": stat_greater,
            "wilcoxon_p_greater": p_greater,
            "wilcoxon_stat_less": stat_less,
            "wilcoxon_p_less": p_less,
            "direction_conclusion": direction_conclusion,
            "mean_diff": mean_diff,
            "std_diff": std_diff,
            "TOST_p_lower": p_lower,
            "TOST_p_upper": p_upper,
            "TOST_conclusion": tost_conclusion
        }
    else:
        # Significant difference in one direction => no TOST
        return {
            "wilcoxon_stat_greater": stat_greater,
            "wilcoxon_p_greater": p_greater,
            "wilcoxon_stat_less": stat_less,
            "wilcoxon_p_less": p_less,
            "direction_conclusion": direction_conclusion,
            "mean_diff": mean_diff,
            "std_diff": std_diff,
            "TOST_p_lower": None,
            "TOST_p_upper": None,
            "TOST_conclusion": None
        }

# ------------------------------
# Purely Nominal Agreement
# ------------------------------

def measure_nominal_agreement(before_labels, after_labels):
    """
    Computes Cohen’s Kappa and a confusion matrix for purely nominal data.
      - 'before_labels', 'after_labels': arrays/lists of same length

    Returns (kappa, cm) where kappa is float, cm is a 2D ndarray (confusion matrix).
    """
    from sklearn.metrics import cohen_kappa_score, confusion_matrix
    kappa = cohen_kappa_score(before_labels, after_labels)
    cm = confusion_matrix(before_labels, after_labels)
    return kappa, cm


# ------------------------------
# final decision mapping
# ------------------------------

DECISION_MAPPING = {
    "Reject": 0,
    "Accept as Poster": 1,
    "Accept as Spotlight": 2,
    "Accept as Oral": 3
}

def map_final_decision_to_numeric(series: pd.Series) -> pd.Series:
    """
    Maps string decisions to numeric codes (0..3). Unknown values -> NaN.
    """
    def encode_decision(decision):
        if decision in DECISION_MAPPING:
            return DECISION_MAPPING[decision]
        return np.nan
    return series.apply(encode_decision)

# ------------------------------
# Field-Specific Delta
# ------------------------------

FIELD_DELTA_MAP = {
    "contribution_score": 0.5,  # 4-point scale
    "soundness_score":    0.5,  # 4-point scale
    "presentation_score": 0.5,  # 4-point scale
    "overall_score":      1.0,  # [1,3,5,6,8,10]
    "final_decision":     0.5   # 4 categories => numeric codes (0..3)
}

# ------------------------------
# Main analysis function
# ------------------------------

def perform_and_print_tests(baseline_df, perturb_df,
                            review_type_col="review_type",
                            prompt_setting_col="prompt_setting",
                            perturbation_col="perturbation_type",
                            id_col="id",
                            alpha=0.05):
    """
    Performs the 3-way comparison test for each (review_type, prompt_setting, perturbation_type, score_col)
    and also computes a purely nominal agreement measure (Cohen's Kappa + confusion matrix)
    if 'score_col' is a purely nominal field (e.g., 'final_decision').

    1) Group baseline & perturbation by 'review_type' (meta-review or review).
    2) For each 'prompt_setting',
    3) For each 'perturbation_type',
    4) Merge on 'id' and compare common score columns.
    5) For each score column:
       - Convert numeric if needed,
       - run compare_scores_3way,
       - if 'score_col' == 'final_decision', also run measure_nominal_agreement.
    """

    # Identify all possible review_types in baseline:
    review_types = sorted(baseline_df[review_type_col].dropna().unique())
    for rtype in review_types:
        print(f"\n{'='*40}\nReview Type: {rtype}\n{'='*40}")

        # Subset for this review_type
        baseline_sub_rt = baseline_df[baseline_df[review_type_col] == rtype]
        perturb_sub_rt  = perturb_df[perturb_df[review_type_col] == rtype]

        # Identify the prompt settings in baseline for this review_type
        prompt_settings = sorted(baseline_sub_rt[prompt_setting_col].dropna().unique())
        for psetting in prompt_settings:
            print(f"\n{'='*40}\nPrompt Setting: {psetting}\n{'='*40}")

            baseline_ps = baseline_sub_rt[baseline_sub_rt[prompt_setting_col] == psetting]
            perturb_ps  = perturb_sub_rt[perturb_sub_rt[prompt_setting_col] == psetting]
            if baseline_ps.empty or perturb_ps.empty:
                print("  No data in baseline or perturbation for this prompt setting.")
                continue

            # Extract perturbation types
            if perturbation_col in perturb_ps.columns:
                perturb_types = sorted(perturb_ps[perturbation_col].dropna().unique())
            else:
                perturb_types = ["No_perturbation_col_found"]

            baseline_cols = set(baseline_ps.columns)

            for pt in perturb_types:
                print(f"\n--- Perturbation Type: {pt} ---\n")
                if pt == "No_perturbation_col_found":
                    sub_pert = perturb_ps
                else:
                    sub_pert = perturb_ps[perturb_ps[perturbation_col] == pt]

                if sub_pert.empty:
                    print(f"    No data for perturbation type={pt}")
                    continue

                perturb_cols = set(sub_pert.columns)
                exclude_cols = {id_col, review_type_col, prompt_setting_col, 
                                perturbation_col, "source_file"}
                common_cols  = list((baseline_cols & perturb_cols) - exclude_cols)
                if not common_cols:
                    print("    No common score columns. Skipping.")
                    continue

                merged_data = pd.merge(
                    baseline_ps, sub_pert, on=id_col, suffixes=('_before', '_after')
                )
                if merged_data.empty:
                    print("    No matching data. Skipping.")
                    continue

                for score_col in common_cols:
                    before_col = score_col + "_before"
                    after_col  = score_col + "_after"
                    if before_col not in merged_data.columns or after_col not in merged_data.columns:
                        print(f"    Missing columns for '{score_col}'. Skipping.")
                        continue

                    # If final_decision => map numeric
                    if score_col == "final_decision":
                        merged_data[before_col] = map_final_decision_to_numeric(merged_data[before_col])
                        merged_data[after_col]  = map_final_decision_to_numeric(merged_data[after_col])
                    else:
                        # Convert numeric
                        merged_data[before_col] = pd.to_numeric(merged_data[before_col], errors='coerce')
                        merged_data[after_col]  = pd.to_numeric(merged_data[after_col], errors='coerce')

                    temp_df = merged_data.dropna(subset=[before_col, after_col])
                    if temp_df.empty:
                        print(f"    All NaN in '{score_col}'. Skipping.")
                        continue

                    before_scores = temp_df[before_col].tolist()
                    after_scores  = temp_df[after_col].tolist()

                    if not before_scores or not after_scores:
                        print(f"    No valid data for '{score_col}'. Skipping.")
                        continue

                    # 1) run directional/invariance test
                    delta_for_field = FIELD_DELTA_MAP.get(score_col, 1.0)
                    print(f"  * Score Column: {score_col} (delta={delta_for_field})")
                    results = compare_scores_3way(before_scores, after_scores,
                                                  delta=delta_for_field, alpha=alpha)
                    print(f"    Direction Conclusion: {results['direction_conclusion']}")
                    if results['TOST_conclusion']:
                        print(f"    TOST Conclusion:      {results['TOST_conclusion']}")

                    # 2) If 'score_col' is purely nominal, e.g., 'final_decision',
                    #    measure nominal agreement (Cohen's kappa & confusion matrix).
                    if score_col == "final_decision":
                        # We already have them as numeric codes, but that's fine for nominal usage.
                        from sklearn.metrics import cohen_kappa_score, confusion_matrix
                        kappa = cohen_kappa_score(before_scores, after_scores)
                        cm = confusion_matrix(before_scores, after_scores)
                        print(f"    Cohen's Kappa: {kappa:.3f}")
                        print(f"    Confusion Matrix:\n{cm}")


# ------------------------------
# Main Execution
# ------------------------------

if __name__ == "__main__":
    data_directory = "./"  # Update as needed

    baseline_df, perturb_df = load_data(data_directory)
    print("Baseline data loaded from files:")
    if not baseline_df.empty:
        print(baseline_df["source_file"].unique())
    else:
        print("No baseline data loaded.")

    print("Perturbation data loaded from files:")
    if not perturb_df.empty:
        print(perturb_df["source_file"].unique())
    else:
        print("No perturbation data loaded.")

    if not baseline_df.empty and not perturb_df.empty:
        perform_and_print_tests(baseline_df, perturb_df, alpha=0.05)
    else:
        print("Missing baseline and/or perturbation data.")