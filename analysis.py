import sqlite3
import pandas as pd
from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests
import seaborn as sns
import matplotlib.pyplot as plt 
from pathlib import Path

DB_FILE = "loblaw-database.db"
OUTPUT_DR = Path("outputs")

#Part 2: Initial Analysis - Data Overview)
def make_data_overview(connection): 
    query = """
        WITH counts AS (
            SELECT sample_id AS sample, 
                population, 
                count, 
                SUM(count) OVER (PARTITION BY sample_id) AS total_count
            FROM cell_counts
            ) SELECT 
                sample, total_count, population, count, 
                ROUND(100.0 * count / total_count, 2) AS percentage
            FROM counts; 
    """
    return pd.read_sql_query(query, connection)

#Part 3: Statistical Analysis
def get_mel_mirlib_data(connection): 
    # melanoma patients receiving miraclib, only PBMC sample type. responders vs non-responders 
    query = """
        SELECT
            sa.sample_id AS sample,
            sa.subject_id AS subject, 
            su.response
        FROM samples AS sa 
        JOIN subjects AS su ON sa.subject_id = su.subject_id
        WHERE su.condition = 'melanoma' AND su.treatment = 'miraclib' 
        AND sa.sample_type = 'PBMC'; 
    """
    return pd.read_sql_query(query, connection)

def compare_population(data):
    output = []
    for population in data["population"].unique(): 
        responder_vals = data[(data["population"] == population) & (data["response"] == "yes")]["percentage"] 
        non_responder_vals = data[(data["population"] == population) & (data["response"] == "no")]["percentage"]
        statistic, p_val = mannwhitneyu(responder_vals, non_responder_vals, alternative="two-sided")
        output.append({"population": population, "n_responders": len(responder_vals), 
                       "n_non_responders": len(non_responder_vals), 
                       "responder_median": responder_vals.median(), 
                       "non_responder_median": non_responder_vals.median(), 
                       "statistic": statistic, "p_value": p_val})
    stat_outputs = pd.DataFrame(output)
     
    reject, adjusted_p_vals, _, _ = multipletests(stat_outputs["p_value"], method="fdr_bh")
    stat_outputs["adjusted_p_vals"] = adjusted_p_vals
    stat_outputs["significant"] = reject
    return stat_outputs

def make_boxplot(data):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=data, x="population", y="percentage", hue="response", ax=ax)
    ax.set_xlabel("Cell Population")
    ax.set_ylabel("Relative Frequency (%)")
    ax.set_title("Cell Population Frequency by Response to Miraclib Treatment")
    fig.tight_layout()
    return fig

#Part 4 Data Subset Analysis
def get_baseline_mm_data(connection): 
    # melanoma patients receiving miraclib, PBMC sample type + at baseline. 
    # responders vs non-responders, project, sex
    query = """
        SELECT
            sa.sample_id AS sample,
            sa.subject_id AS subject, 
            su.response, 
            su.project, 
            su.sex
        FROM samples AS sa 
        JOIN subjects AS su ON sa.subject_id = su.subject_id
        WHERE su.condition = 'melanoma' AND su.treatment = 'miraclib' 
        AND sa.sample_type = 'PBMC' AND sa.time_from_treatment_start = 0; 
    """
    return pd.read_sql_query(query, connection)

 #answering quesiton in google form 
def get_avg_baseline_b_cells(connection):
        query = """
            SELECT 
                AVG(c.count)
            FROM samples AS sa 
            JOIN subjects AS su ON sa.subject_id = su.subject_id
            JOIN cell_counts AS c ON sa.sample_id = c.sample_id
            WHERE su.condition = 'melanoma' AND sa.time_from_treatment_start = 0 
            AND c.population = 'b_cell' AND su.sex='M' AND su.response='yes';
        """
        answer = connection.execute(query).fetchone()[0]
        return answer


def main(): 
    OUTPUT_DR.mkdir(exist_ok=True)
    with sqlite3.connect(DB_FILE) as connection:
        connection.execute("PRAGMA foreign_keys = ON") 
        overview = make_data_overview(connection)
        overview.to_csv(OUTPUT_DR / "data_overview.csv", index=False)

        additional_data = get_mel_mirlib_data(connection)
        mel_mirlib_PBMC_data = overview.merge(additional_data, on="sample", how="inner")
        stat_outputs = compare_population(mel_mirlib_PBMC_data)
        stat_outputs.to_csv(OUTPUT_DR / "statistic_results.csv", index=False)
        boxplot_fig = make_boxplot(mel_mirlib_PBMC_data)
        boxplot_fig.savefig(OUTPUT_DR / "treatment_response_boxplot.png", dpi=300)
        plt.close(boxplot_fig)

        baseline_info = get_baseline_mm_data(connection)
        full_baseline_data = overview.merge(baseline_info, on="sample", how="inner")
        full_baseline_data.to_csv(OUTPUT_DR/ "baseline_analysis.csv", index=False)
        project_baseline_count = (full_baseline_data.groupby("project")["sample"].nunique().reset_index(name="count"))
        project_baseline_count["category"] = "Project"
        project_baseline_count = project_baseline_count.rename(columns={"project": "group"})
        response_baseline_count = (full_baseline_data.groupby("response")["subject"].nunique().reset_index(name="count"))
        response_baseline_count["category"] = "Response"
        response_baseline_count = response_baseline_count.rename(columns={"response": "group"})
        sex_baseline_counts = (full_baseline_data.groupby("sex")["subject"].nunique().reset_index(name="count"))
        sex_baseline_counts["category"] = "Sex"
        sex_baseline_counts = sex_baseline_counts.rename(columns={"sex": "group"})
        baseline_subsets = pd.concat([
                project_baseline_count,
                response_baseline_count,
                sex_baseline_counts
            ],ignore_index=True
        )[["category", "group", "count"]]
        baseline_subsets.to_csv( OUTPUT_DR / "baseline_subsets.csv", index=False)


if __name__ == "__main__":
    main()