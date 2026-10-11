# FreshMart Insights Platform

<p align="center">
  <img src="https://img.shields.io/badge/Retail-Analytics-0F172A?style=for-the-badge&logo=shopping&logoColor=white" alt="Retail Analytics" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/ML-Scikit%20Learn-FA6C2B?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="Scikit-learn" />
</p>

A more strategic name for this project is: <strong>FreshMart Insights Platform</strong>.

## Elevator Pitch

FreshMart Insights Platform transforms retail data into actionable business intelligence by combining interactive dashboards, geographic analysis, and predictive modeling in one unified solution. Designed around a Romanian retail dataset, the project helps uncover sales trends, customer behavior, and profitability patterns across regions, categories, and segments. It demonstrates how data engineering, statistical analysis, and machine learning can be applied to real business decision-making.

## Why This Project Stands Out

- End-to-end analytics workflow from data preparation to insight delivery
- Strong business narrative grounded in a realistic retail scenario
- Visual, recruiter-friendly dashboard with data storytelling
- Applied use of Python, statistics, machine learning, and geospatial analytics
- A practical example of how analytical thinking can support pricing, segmentation, and profitability strategies

## Key Features

- Interactive Streamlit dashboard with dynamic filtering by year, region, category, and customer segment
- KPI overview for revenue, profit, transaction volume, and profitability rate
- Regional sales mapping using GeoPandas and county-level geographic visualizations
- Missing value and outlier analysis with imputation and treatment strategies
- Encoding and scaling demonstrations for machine learning readiness
- Aggregation and correlation analysis using pandas for business insight extraction
- Customer segmentation using K-Means clustering
- Profitability prediction using Logistic Regression
- Profit modeling with Multiple Linear Regression via Statsmodels
- Multi-chart Matplotlib gallery covering scatter, bar, heatmap, time-series, and histogram views

## Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat-square&logo=matplotlib&logoColor=white)
![GeoPandas](https://img.shields.io/badge/GeoPandas-2D7D7D?style=flat-square&logo=geopandas&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/scikit--learn-FA6C2B?style=flat-square&logo=scikit-learn&logoColor=white)
![Statsmodels](https://img.shields.io/badge/Statsmodels-1F77B4?style=flat-square)
![SAS](https://img.shields.io/badge/SAS-Analytics-1D4ED8?style=flat-square)

### Core technologies

- Python 3.10+
- Streamlit for interactive UI and analytics workflows
- Pandas and NumPy for data wrangling and transformations
- Matplotlib for custom business visualizations
- GeoPandas and Shapely for geo-analytics and regional mapping
- Scikit-learn for clustering and predictive modeling
- Statsmodels for regression analysis and statistical interpretation
- SAS for academic/analytical comparison and extended data analysis

## Project Structure

```text
FreshMart-Insights-Platform/
├── Data/
│   └── FreshMart_Dataset.csv
├── Python/
│   ├── app.py
│   └── prepare_data.py
├── SAS/
│   └── ProjectSAS.sas
├── .venv/
├── venv/
├── .gitignore
├── README.md
└── ...
```

## Architecture & Design Patterns

This project follows a practical, modular analytics architecture designed for readability and extensibility:

- Layered architecture: data ingestion → preprocessing → transformation → analytics → visualization
- Functional decomposition: each analytical section in the dashboard is separated into dedicated functions for maintainability
- ETL-inspired workflow: raw data is cleaned, enriched, and transformed before modeling
- Feature engineering: derived fields such as profit margin, profitability flags, and shipping time support downstream analysis
- Reusable analytics patterns: groupby aggregation, pivot tables, encoding, scaling, and visual storytelling are applied consistently
- Business-intelligence mindset: technical methods are connected to business questions such as regional performance, customer value, and profitability drivers

This structure reflects disciplined engineering practices and an emphasis on analytical clarity, which is attractive for recruiter evaluation and stakeholder communication.

## Installation & Setup

### 1) Clone the repository

```bash
git clone https://github.com/TurcanuTeodor/FreshMart-Insights-Platform.git
cd FreshMart-Insights-Platform
```

### 2) Create a virtual environment

```bash
python -m venv .venv
```

On Windows:

```powershell
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install streamlit pandas numpy matplotlib scikit-learn geopandas shapely statsmodels openpyxl
```

### 4) Prepare the dataset

The project already includes the processed dataset in:

```text
Data/FreshMart_Dataset.csv
```

If you want to regenerate the prepared dataset from the source workbook, run:

```bash
python Python/prepare_data.py
```

### 5) Launch the dashboard

```bash
streamlit run Python/app.py
```

### 6) Open the app

Visit the local URL generated by Streamlit, typically:

```text
http://localhost:8501
```

## Usage Highlights

After launching the app, users can:

- Explore total sales, profit, and margin trends
- Filter by year, category, region, and customer segment
- Analyze county-level sales performance on a Romanian map
- Compare missing value treatment strategies
- Visualize clustering results and customer segments
- Evaluate model output for profitability and profit estimation

## Business Impact

This solution is designed to support decisions in areas such as:

- Regional sales optimization
- Category-level performance analysis
- Customer segmentation strategy
- Profitability improvement
- Pricing and discount evaluation
- Data quality monitoring in retail operations

## Future Enhancements

- Forecasting module using time-series models
- Customer churn and retention analysis
- Recommendation engine for product bundles
- CI/CD pipeline and deployment to cloud hosting
- Automated reporting with exportable PDF/Excel summaries

## Project Summary

FreshMart Insights Platform combines applied data science, business intelligence, and software engineering in a single polished project. It reflects the ability to move from raw data to strategic decision support, which is highly relevant for analytics, consulting, data, and product-focused roles.

---

<p align="center">
  <strong>Built for business insight, analytics thinking, and technical storytelling.</strong>
</p>
