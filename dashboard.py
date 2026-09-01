import streamlit as st
import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

st.set_page_config(
    page_title="Analysis Dashboard",
    layout="wide",
)

@st.cache_data
def load_outputs():
    outputs = {}
    csv_files = {
        "data_overview": "data_overview.csv",
        "statistic_results": "statistic_results.csv",
        "baseline_analysis": "baseline_analysis.csv",
        "baseline_subsets": "baseline_subsets.csv",
    }
    for name, filename in csv_files.items():
        file_path = OUTPUT_DIR / filename
        if file_path.exists():
            outputs[name] = pd.read_csv(file_path)
    return outputs
outputs = load_outputs()
boxplot_path = OUTPUT_DIR / "treatment_response_boxplot.png"

if not outputs:
    st.error(
        "No analysis outputs were found in the output folder. "
        "Run analysis.py first."
    )
    st.stop()

st.title("Analysis Dashboard")
st.header("Part 2: Data Overview")
if "data_overview" in outputs:
    data_overview = outputs["data_overview"]
    st.write(
        "Overview of cell population counts and relative frequencies "
        "across samples."
    )
    st.dataframe(
        data_overview,
        use_container_width=True,
        height=500,
    )
else:
    st.warning("data_overview.csv was not found.")

st.header("Part 3: Statistical Analysis")
if "statistic_results" in outputs:
    statistic_results = outputs["statistic_results"]
    bool_columns = statistic_results.select_dtypes(include="bool").columns
    statistic_results[bool_columns] = (statistic_results[bool_columns].astype(str))
    st.write(
        "Mann–Whitney U tests comparing cell population frequencies between responders and non-responders of melanoma patients receiving miraclib."
    )
    st.dataframe(
        statistic_results,
        use_container_width=True,
    )
else:
    st.warning("statistic_results.csv was not found.")

st.subheader("Treatment Response Visualization")
if boxplot_path.exists():
    st.image(
        str(boxplot_path),
        caption="Cell Population Frequency by Response to Miraclib Treatment from PBMC samples.",
        use_container_width=True,
    )
else:
    st.warning("treatment_response_boxplot.png was not found.")

st.header("Part 4: Baseline Analysis")
if "baseline_analysis" in outputs:
    baseline_analysis = outputs["baseline_analysis"]
    st.write("Baseline PBMC samples from melanoma patients receiving miraclib treatment.")
    st.dataframe(
        baseline_analysis,
        use_container_width=True,
        height=500,
    )
else:
    st.warning("baseline_analysis.csv was not found.")

st.subheader("Baseline Population Summary")
baseline_subsets = outputs["baseline_subsets"]
st.dataframe(baseline_subsets, hide_index=True)
col1, col2, col3 = st.columns(3)

st.divider()
st.caption( "Dashboard generated from analysis.py outputs.")