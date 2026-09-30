# Kenya Gender Parity & Empowerment Tracker

A simple dashboard with charts showing Kenya's progress in education, jobs, and government leadership.

## Key Features & Dashboard Tabs

* **Primary GPI:** Visualizes the gross school enrollment Gender Parity Index for primary education over time, highlighting progress toward perfect parity (1.0).
* **Primary vs Secondary:** Compares educational parity trends across education levels, calculating average gaps and identifying milestone years.
* **Labor Force:** Analyzes modeled International Labour Organization (ILO) estimates for female labor force participation ($\ge 15$ years), featuring dynamic peak and low point detection.
* **Parliament:** Tracks the proportion of national parliamentary seats held by women against Kenya’s 30% constitutional target.
* **Latest Values:** Side-by-side bar visualizations comparing most recent indicator metrics across education ratios and participation percentages.
* **Correlation Heatmap:** Advanced multi-indicator correlation matrix supporting configurable statistical methods (pearson, spearman, kendall), custom colormaps, toggleable cell annotations, and automated strongest relationship highlights.
* **Export Data:** Responsive tabular data preview with customized multi-indicator filtering and instant one-click CSV export.

## Core Indicators & Data Sources

The dashboard tracks key developmental metrics sourced from standard international development datasets:

* **School Enrollment (Primary & Secondary GPI):** Gross enrollment ratio gender parity index.
* **Female Labor Force Participation:** Modeled ILO estimates for women ages 15+ as a percentage of the female population.
* **Parliamentary Representation:** Proportion of seats held by women in national parliaments.

## Tech Stack

* **Language:** Python
* **Web Framework:** Streamlit
* **Data Processing:** Pandas, NumPy
* **Data Visualization:** Matplotlib, Seaborn

* http://localhost:8502/
