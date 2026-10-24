# A/B Test Analysis

An end-to-end A/B testing project that evaluates the effectiveness of an advertising campaign using data analysis, SQL, and statistical hypothesis testing.

## Project Overview

This project analyzes a marketing A/B testing dataset to compare the conversion performance of users exposed to advertisements against users exposed to a public service announcement (PSA). Statistical tests are used to determine whether the observed difference in conversion rates is significant.

## Objectives

- Clean and validate the dataset.
- Perform exploratory data analysis (EDA).
- Calculate and compare conversion rates.
- Conduct statistical hypothesis testing.
- Analyze conversion performance across user segments.
- Visualize results and communicate actionable business insights.

## Tools & Technologies

- **Python:** Pandas, NumPy
- **Statistical Analysis:** SciPy, Statsmodels
- **Data Visualization:** Matplotlib, Seaborn
- **SQL:** Data querying and analysis
- **Dashboard:** Streamlit
- **Version Control:** Git and GitHub

## Key Findings

- The advertising group achieved a conversion rate of approximately **2.55%**, compared with **1.79%** for the PSA group.
- The absolute conversion lift was approximately **0.77 percentage points**.
- A two-proportion statistical test indicated a statistically significant difference between the groups (*p* < 0.001).
- Segment-level analysis was conducted to identify groups with statistically significant differences, using Bonferroni correction to account for multiple comparisons.

## Live Dashboard

[View the A/B Test Analysis Dashboard](https://ab-test-analysis-njlhonfbjklkgnbppe3dzw.streamlit.app/)

## Project Structure

```text
ab-test-analysis/
├── data/
├── notebooks/
├── sql/
├── app.py
├── requirements.txt
└── README.md
```

## How to Run Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/priya-39/ab-test-analysis.git
   cd ab-test-analysis
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   ```

   On Windows PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the dashboard:

   ```bash
   streamlit run app.py
   ```

## Conclusion

The analysis found that the advertising group had a higher conversion rate than the PSA group, with statistical evidence supporting a difference between the two groups. The project demonstrates practical skills in data cleaning, exploratory analysis, SQL, hypothesis testing, visualization, and dashboard development.

## Author

[Priya](https://github.com/priya-39)


