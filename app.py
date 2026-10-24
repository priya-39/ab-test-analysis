from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from statsmodels.stats.proportion import proportions_ztest, proportion_confint

st.set_page_config(page_title="A/B Test Analysis", page_icon="📊", layout="wide")
st.title("Marketing A/B Test Analysis")
st.caption("Question: Does the ad campaign improve conversion compared with the PSA control group?")


@st.cache_data
def load_data(csv_path: str) -> pd.DataFrame:
    data = pd.read_csv(csv_path)
    data.columns = (
        data.columns.str.strip().str.lower().str.replace(" ", "_", regex=False)
    )
    data = data.loc[:, ~data.columns.str.match(r"^unnamed(:_\d+)?$", case=False)]

    required = {
        "user_id", "test_group", "converted", "total_ads",
        "most_ads_day", "most_ads_hour"
    }
    missing = required - set(data.columns)
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))

    data["test_group"] = data["test_group"].astype(str).str.strip().str.lower()
    data["converted"] = (
        data["converted"].astype(str).str.strip().str.lower()
        .map({"true": 1, "false": 0, "1": 1, "0": 0})
    )
    data["total_ads"] = pd.to_numeric(data["total_ads"], errors="coerce")
    data["most_ads_hour"] = pd.to_numeric(data["most_ads_hour"], errors="coerce")
    data["most_ads_day"] = data["most_ads_day"].astype(str).str.strip().str.title()
    data = data.dropna(subset=[
        "test_group", "converted", "total_ads", "most_ads_hour", "most_ads_day"
    ])
    data = data[data["test_group"].isin(["ad", "psa"])].copy()
    data["converted"] = data["converted"].astype(int)
    data["most_ads_hour"] = data["most_ads_hour"].astype(int)

    data["day_type"] = np.where(
        data["most_ads_day"].isin(["Saturday", "Sunday"]), "Weekend", "Weekday"
    )
    data["exposure_level"] = np.where(
        data["total_ads"] <= data["total_ads"].median(),
        "Low exposure", "High exposure"
    )
    return data


DATA_PATH = Path(__file__).resolve().parent / "data" / "marketing_AB.csv"
try:
    df = load_data(str(DATA_PATH))
except FileNotFoundError:
    st.error(
        f"Dataset not found at: {DATA_PATH}\n\n"
        "Place marketing_AB.csv inside the project's data folder."
    )
    st.stop()
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.stop()


# Sidebar filters
st.sidebar.header("Filters")
day_options = ["All"] + sorted(df["most_ads_day"].dropna().unique().tolist())
selected_day = st.sidebar.selectbox("Day of week", day_options, index=0)

hour_min = int(df["most_ads_hour"].min())
hour_max = int(df["most_ads_hour"].max())
selected_hours = st.sidebar.slider(
    "Hour range", min_value=hour_min, max_value=hour_max,
    value=(hour_min, hour_max)
)

exposure_options = ["All", "Low exposure", "High exposure"]
selected_exposure = st.sidebar.selectbox("Ad exposure", exposure_options, index=0)

filtered = df.copy()
if selected_day != "All":
    filtered = filtered[filtered["most_ads_day"] == selected_day]
filtered = filtered[
    filtered["most_ads_hour"].between(selected_hours[0], selected_hours[1])
]
if selected_exposure != "All":
    filtered = filtered[filtered["exposure_level"] == selected_exposure]


# Calculate filtered metrics
ad = filtered[filtered["test_group"] == "ad"]
psa = filtered[filtered["test_group"] == "psa"]
n_ad, n_psa = len(ad), len(psa)

if n_ad == 0 or n_psa == 0:
    st.warning(
        "These filters leave no users in one of the groups. "
        "Change the filters to compare ad and PSA users."
    )
    st.stop()

conv_ad, conv_psa = int(ad["converted"].sum()), int(psa["converted"].sum())
rate_ad, rate_psa = conv_ad / n_ad, conv_psa / n_psa
absolute_lift = rate_ad - rate_psa
relative_lift = absolute_lift / rate_psa * 100 if rate_psa > 0 else np.nan

_, p_value = proportions_ztest(
    count=np.array([conv_ad, conv_psa]),
    nobs=np.array([n_ad, n_psa]),
    alternative="two-sided",
)

ad_ci_low, ad_ci_high = proportion_confint(
    count=conv_ad, nobs=n_ad, alpha=0.05, method="wilson"
)
psa_ci_low, psa_ci_high = proportion_confint(
    count=conv_psa, nobs=n_psa, alpha=0.05, method="wilson"
)


# KPI cards
st.subheader("Key performance indicators")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Ad conversion rate", f"{rate_ad:.2%}",
          help=f"{conv_ad:,} conversions from {n_ad:,} users")
c2.metric("PSA conversion rate", f"{rate_psa:.2%}",
          help=f"{conv_psa:,} conversions from {n_psa:,} users")
c3.metric("Absolute lift", f"{absolute_lift * 100:+.3f} pp",
          help="Ad conversion rate minus PSA conversion rate, in percentage points")
c4.metric("Two-sided p-value", f"{p_value:.4g}",
          help="Two-proportion z-test; unadjusted alpha = 0.05")

st.caption(
    f"Relative lift: {relative_lift:+.2f}% versus PSA"
    if np.isfinite(relative_lift)
    else "Relative lift is unavailable because the PSA conversion rate is zero."
)
st.caption(f"Filtered sample sizes — Ad: {n_ad:,} users; PSA: {n_psa:,} users.")


# Chart with 95% Wilson confidence intervals
st.subheader("Conversion rate with 95% confidence intervals")
labels = ["Ad", "PSA"]
rates = np.array([rate_ad, rate_psa])
lower = np.array([ad_ci_low, psa_ci_low])
upper = np.array([ad_ci_high, psa_ci_high])
yerr = np.vstack([rates - lower, upper - rates])

fig, ax = plt.subplots(figsize=(7, 4.5))
bars = ax.bar(labels, rates * 100, yerr=yerr * 100, capsize=7)
ax.set_ylabel("Conversion rate (%)")
ax.set_title("Conversion rate by test group")
ax.grid(axis="y", linestyle="--", alpha=0.35)
ax.set_axisbelow(True)
for bar, rate, up in zip(bars, rates, upper):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        up * 100,
        f"{rate:.2%}",
        ha="center",
        va="bottom"
    )
fig.tight_layout()
st.pyplot(fig)
plt.close(fig)
st.caption(
    "Error bars show 95% Wilson confidence intervals for each group's conversion rate. "
    "They are not a confidence interval for the difference in conversion rates."
)


# Plain-English interpretation
st.subheader("What do the results mean?")
alpha = 0.05
if p_value < alpha:
    direction = (
        "higher" if absolute_lift > 0
        else "lower" if absolute_lift < 0
        else "the same"
    )
    result_sentence = (
        f"The difference is statistically significant at the 5% level "
        f"(p = {p_value:.4g}). The ad group's conversion rate is "
        f"{abs(absolute_lift) * 100:.3f} percentage points {direction} "
        "than the PSA group's."
    )
else:
    result_sentence = (
        f"The difference is not statistically significant at the 5% level "
        f"(p = {p_value:.4g}). The observed lift is {absolute_lift * 100:+.3f} "
        "percentage points, but this subset does not provide sufficient evidence "
        "of a difference in conversion rates."
    )

if np.isfinite(relative_lift):
    result_sentence += f" Relative lift versus PSA is {relative_lift:+.2f}%."
result_sentence += (
    " Statistical significance alone does not establish profitability or prove "
    "that the campaign caused the difference."
)
st.info(result_sentence)

st.warning(
    "Interpretation cautions: changing filters creates multiple comparisons, so some "
    "subsets may appear significant by chance. Segment results are exploratory. "
    "Ad exposure was not randomized, so differences by exposure level are associations, "
    "not evidence that exposure caused conversion. The overall test allocation is "
    "highly imbalanced; inspect sample sizes and confidence intervals."
)

with st.expander("View filtered summary table"):
    summary = pd.DataFrame({
        "Group": ["Ad", "PSA"],
        "Users": [n_ad, n_psa],
        "Conversions": [conv_ad, conv_psa],
        "Conversion rate": [rate_ad, rate_psa],
        "95% CI lower": [ad_ci_low, psa_ci_low],
        "95% CI upper": [ad_ci_high, psa_ci_high],
    })
    st.dataframe(
        summary.style.format({
            "Conversion rate": "{:.2%}",
            "95% CI lower": "{:.2%}",
            "95% CI upper": "{:.2%}",
        }),
        use_container_width=True,
        hide_index=True,
    )
