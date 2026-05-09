import os
import json
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
plt.rcParams['font.family'] = 'STIXGeneral'

# ------------------------------
# Data Loading Functions
# ------------------------------

def jsonl_to_dataframe(file_path: str) -> pd.DataFrame:
    """
    Reads a JSONL file and converts it to a pandas DataFrame.
    """
    try:
        data = []
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:
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
    """
    Gets all JSONL file paths in the directory.
    """
    try:
        jsonl_files = [os.path.join(directory, file)
                       for file in os.listdir(directory)
                       if file.endswith('.jsonl')]
        return jsonl_files
    except FileNotFoundError:
        print(f"Error: Directory not found: {directory}")
        return []
    except Exception as e:
         print(f"An unexpected error occurred while listing files in {directory}: {e}")
         return []


def parse_file_info(file_name: str) -> dict:
    """Parses public-release and legacy meta-review score filenames."""
    public_baseline = r"baseline__target-meta-review__prompt-([a-zA-Z0-9-]+)\.jsonl$"
    match = re.search(public_baseline, file_name)
    if match:
        return {"type": "baseline", "prompt_setting": match.group(1)}

    public_perturbed = r"perturbed__source-([a-zA-Z]+)__aspect-([a-zA-Z]+)__target-meta-review__prompt-([a-zA-Z0-9-]+)\.jsonl$"
    match = re.search(public_perturbed, file_name)
    if match:
        return {
            "type": "perturbation",
            "prompt_setting": match.group(3),
            "perturbation_type": f"{match.group(1)}_{match.group(2)}",
        }

    # Backward-compatible parser for original experiment filenames.
    baseline_pattern = r"output_test_base_input_meta-review_([a-zA-Z0-9-]+)_overall"
    match = re.search(baseline_pattern, file_name)
    if match:
        return {"type": "baseline", "prompt_setting": match.group(1)}

    pert_pattern = r"test_([a-zA-Z]+)_([a-zA-Z]+)_perturbed_meta-review_([a-zA-Z0-9-]+)_overall"
    match = re.search(pert_pattern, file_name)
    if match:
        perturb_content = match.group(1)
        perturb_aspect = match.group(2)
        prompt_setting = match.group(3)
        perturbation_type = f"{perturb_content}_{perturb_aspect}"
        return {"type": "perturbation", "prompt_setting": prompt_setting, "perturbation_type": perturbation_type}

    alt_pattern = r"output_test_([a-zA-Z]+)_perturbed_meta-review_([a-zA-Z0-9-]+)_overall"
    match = re.search(alt_pattern, file_name)
    if match:
        perturbation_type = match.group(1)
        prompt_setting = match.group(2)
        return {"type": "perturbation", "prompt_setting": prompt_setting, "perturbation_type": perturbation_type}

    return None


def load_data(directory: str):
    """
    Loads all JSONL files, separates into baseline and perturbation DataFrames.
    """
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

        if info["type"] == "baseline":
            df["prompt_setting"] = info["prompt_setting"]
            baseline_dfs.append(df)
        elif info["type"] == "perturbation":
            df["prompt_setting"] = info["prompt_setting"]
            df["perturbation_type"] = info["perturbation_type"]
            perturb_dfs.append(df)

    baseline_df = pd.concat(baseline_dfs, ignore_index=True) if baseline_dfs else pd.DataFrame()
    perturb_df = pd.concat(perturb_dfs, ignore_index=True) if perturb_dfs else pd.DataFrame()

    return baseline_df, perturb_df




# -------------------------------
#            Figure
# ------------------------------

def visualize_accept_ratio_change(
    baseline_df,
    perturb_df,
    prompt_setting_col="prompt_setting",
    perturbation_col="perturbation_type",
    sort_bars=True,
    figsize=(12, 4),
    font_scale=1.2,
    figure_title="Change in Acceptance Ratio Due to Perturbations",
    custom_titles=None,
    custom_x_labels=None,
    save_path=None,
    dpi=300,
    wrap_labels=True,
    label_wrap_width=10
):
    if perturb_df.empty:
        print("No perturbation data to visualize.")
        return

    accepted_choices = {"Accept as Poster", "Accept as Spotlight", "Accept as Oral"}
    
    # Compute Baseline Acceptance Ratio
    baseline = baseline_df.copy()
    baseline["accepted"] = baseline["final_decision"].isin(accepted_choices).astype(int)
    if "paper_id" in baseline.columns:
        baseline = baseline.drop_duplicates(subset=["paper_id"])
    baseline_acceptance = baseline.groupby(prompt_setting_col)["accepted"].mean().reset_index()
    
    # Compute Perturbation Acceptance Ratio
    perturb = perturb_df.copy()
    perturb["accepted_after"] = perturb["final_decision"].isin(accepted_choices).astype(int)
    perturb_acceptance = (
        perturb.groupby([prompt_setting_col, perturbation_col])["accepted_after"]
        .mean()
        .reset_index(name="accept_ratio_after")
    )

    # Merge and Calculate Delta
    merged = perturb_acceptance.merge(baseline_acceptance, on=prompt_setting_col, how="left")
    merged = merged.rename(columns={"accepted": "baseline_accept_ratio"})
    merged["delta_accept_ratio"] = merged["accept_ratio_after"] - merged["baseline_accept_ratio"]

    # Plotting
    prompt_settings = sorted(merged[prompt_setting_col].unique())
    n_prompts = len(prompt_settings)
    sns.set_context("paper", font_scale=font_scale)

    custom_titles = {
    "dimension": "Dimension as COT",
    "none": "None-COT",
    "template": "ICLR Template",
}

    custom_x_labels = {
    "dimension": ["Paper Soundness", "Rebuttal Completeness", "Rebuttal Presentation", "Review Factual", "Paper Presentation", "Paper Contribution","Rebuttal Tone","Review Tone", "Review Conclusion"],
    "none": ["Paper Soundness", "Rebuttal Completeness", "Rebuttal Presentation", "Review Factual", "Paper Presentation", "Paper Contribution","Rebuttal Tone","Review Tone", "Review Conclusion"],
    "template": ["Paper Soundness", "Rebuttal Completeness", "Rebuttal Presentation", "Review Factual", "Paper Presentation", "Paper Contribution","Rebuttal Tone","Review Tone", "Review Conclusion"],
}
    
    fig, axes = plt.subplots(1, n_prompts, figsize=figsize, sharey=True)
    if n_prompts == 1:
        axes = [axes]
    

    for i, (ax, prompt) in enumerate(zip(axes, prompt_settings)):
        data = merged[merged[prompt_setting_col] == prompt]
        if sort_bars:
            data = data.sort_values("delta_accept_ratio", ascending=False)
        
        # Wrap x-axis labels
        if wrap_labels:
            labels = custom_x_labels[prompt] if custom_x_labels and prompt in custom_x_labels else ['\n'.join(textwrap.wrap(label, label_wrap_width)) for label in data[perturbation_col]]
        else:
            labels = data[perturbation_col]
        
        sns.barplot(
            data=data,
            x=perturbation_col,
            y="delta_accept_ratio",
            ax=ax,
            palette=sns.color_palette("RdBu", len(data))
        )
        ax.axhline(0, color="black", linestyle="-", linewidth=1)
        
        # Annotate bars with custom positioning
        for idx, (p, label) in enumerate(zip(ax.patches, labels)):
            value = p.get_height()
            text = f"{value:.3f}" if abs(value) > 0.0005 else "0.000"
            xy_position = (p.get_x() + p.get_width() / 2., value+0.013 ) if idx < len(ax.patches) - 1 else (p.get_x() + p.get_width() / 2., value-0.016 )
            ax.annotate(
                text,
                xy_position,
                ha='center', va='center',
                fontsize=8 * font_scale,
                color='black'
            )
        
        # Set custom titles for each subplot
        title = custom_titles[prompt] if custom_titles and prompt in custom_titles else prompt
        ax.set_title(title, fontsize=10 * font_scale, fontweight='bold')
        ax.set_ylabel("Change in Acceptance Ratio" if i == 0 else "", fontsize=10 * font_scale, fontweight="bold")
        ax.set_xlabel("Perturbation Aspect", fontsize=10 * font_scale, fontweight='bold')
        ax.set_xticklabels(labels, rotation=30, fontsize=8 * font_scale)

    fig.suptitle(figure_title, fontsize=14 * font_scale, fontweight='bold', y=1.05)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches="tight")
    
    plt.show()
    return fig


# ------------------------------
# Main Execution
# ------------------------------

if __name__ == "__main__":
    data_directory = './'
     # BASE DIR

    baseline_df, perturb_df = load_data(data_directory)

    print("Baseline data loaded from files:")
    print(baseline_df["source_file"].unique() if not baseline_df.empty else "No baseline data loaded.")
    print("Perturbation data loaded from files:")
    print(perturb_df["source_file"].unique() if not perturb_df.empty else "No perturbation data loaded.")

    if not perturb_df.empty:
        fig = visualize_accept_ratio_change(
            baseline_df=baseline_df,
            perturb_df=perturb_df,
            sort_bars=True,
            figsize=(18, 6),
            font_scale=1.6,
            figure_title="",
            save_path="acceptance_ratio_changes.pdf",
            dpi=300,
            wrap_labels=True,
            label_wrap_width=12
        )
    else:
        print("No perturbation data found, skipping plotting.")