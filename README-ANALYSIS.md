# FreshMart Insights Platform

## Technical Analysis Report

This project was designed as a business intelligence and analytics solution for a Romanian retail scenario. It combines data preparation, exploratory analysis, geographic visualization, and predictive modeling to answer real commercial questions: which regions are most profitable, which customer segments drive performance, and which factors influence profitability.

---

## 1. Project Objective

The main goal of the project was to transform a raw retail dataset into a structured analytics product capable of supporting managerial decisions. Instead of only storing transactional data, the project converts it into a usable decision-support system with:

- interactive filtering and dashboards,
- geographic performance analysis,
- outlier and missing-data handling,
- customer segmentation,
- profitability prediction,
- regression-based profitability modeling.

The project aligns with the practical needs of retail analytics: understanding revenue drivers, identifying risk patterns, and converting historical transactions into actionable insights.

---

## 2. Dataset Overview

The dataset used in the project simulates a retail operations context for Romania and contains transaction-level information from 2014 to 2017. It includes approximately 9,994 records and combines:

- transaction metadata,
- customer information,
- geographic location (county and region),
- product category and sub-category,
- financial metrics such as sales, profit, discount, and margin,
- operational indicators such as shipment duration.

### Key columns

- Order_ID, Row_ID
- Order_Date, Ship_Date
- Segment, Region, County
- Category, Sub_Category
- Sales, Quantity, Discount, Profit
- Profit_Margin_Pct, Revenue_Per_Unit
- Is_Profitable

The business case is realistic: a retail chain operating across multiple Romanian counties, with categories grouped into Electronics, Home & Living, and General Products.

---

## 3. Data Preparation and Transformation

A key part of the project is the data preparation workflow, implemented in the preparation script. This step ensures the raw dataset becomes operationally usable for analysis.

### Data cleaning and adaptation

The preparation stage includes:

- renaming columns to a consistent internal schema,
- adapting the original dataset to a Romanian retail context,
- replacing country and region fields with Romania-specific geographic mappings,
- translating U.S.-style region/state data into Romanian counties,
- normalizing category names to match the FreshMart business context.

### Feature engineering

Several analytical features were derived to support deeper business analysis:

- Order_Year, Order_Month, Order_Quarter
- Ship_Duration_Days
- Profit_Margin_Pct
- Revenue_Per_Unit
- Is_Profitable

These derived fields make the dataset much more useful for modeling and decision-making. For example, margin and profitability flag help distinguish between high-volume and high-value transactions.

### Data quality simulation

The project intentionally injects realistic missing values into the dataset:

- approximately 3% missing values in Discount
- approximately 3% missing values in Ship_Duration_Days

This creates a realistic business scenario where data quality issues must be handled before running analysis or modeling. It demonstrates practical understanding of real-world analytical pipelines.

---

## 4. Analytics and Business Intelligence Layer

The dashboard is implemented in Streamlit and provides multiple analytical views.

### Overview and KPI dashboard

The main dashboard includes:

- total revenue,
- total profit,
- number of transactions,
- average profit margin,
- profitability rate,
- yearly sales vs. profit comparison,
- category-based sales overview.

This creates a quick operational view suitable for executive reporting and business review meetings.

### GeoPandas mapping

The project uses GeoPandas to visualize sales patterns across Romanian counties. Each county is represented as a geographic point, and bubble size + color intensity are used to show:

- total sales,
- profit,
- margin,
- quantity.

This demonstrates spatial data analysis capabilities and helps reveal regional concentration of performance.

### Missing value and outlier analysis

The app includes dedicated sections for:

- missing-value distribution,
- imputation strategy comparison,
- IQR-based outlier detection,
- winsorization/removal decisions.

This is especially relevant for real-world analytics work, where data quality issues strongly affect model reliability.

### Statistical analysis

The project applies pandas aggregation and descriptive statistics to examine:

- summary measures for key numerical variables,
- grouped metrics by category, region, segment, and ship mode,
- pivot tables,
- correlation analysis,
- monthly trend behavior over time.

These operations reveal relationships that can support operational and strategic recommendations.

---

## 5. Machine Learning and Modeling

The project includes both unsupervised and supervised learning approaches.

### 5.1 K-Means segmentation

Customer-level segmentation is performed using K-Means clustering on three main variables:

- Frequency of orders
- Monetary value of purchases
- Average discount usage

This creates customer groups that can be interpreted as different value/behavior segments. The elbow method is used to help select an appropriate number of clusters, and cluster summaries are visualized.

This is highly relevant for retail strategy because it supports:

- loyalty analysis,
- targeted promotions,
- price sensitivity segmentation,
- customer prioritization.

### 5.2 Logistic Regression for profitability prediction

The project builds a binary classification model to predict whether an order is profitable.

Target variable:

- Is_Profitable = 1 if profit > 0

Features used include:

- Sales
- Quantity
- Discount
- Ship_Duration_Days
- Category
- Segment

The workflow includes:

- encoding of categorical variables,
- scaling of continuous features,
- train/test split,
- model training,
- classification report,
- confusion matrix,
- coefficient interpretation.

This demonstrates an applied machine learning workflow directly connected to a business outcome.

### 5.3 Multiple Linear Regression using Statsmodels

A regression model is built to estimate Profit based on:

- Sales
- Quantity
- Discount
- Ship_Duration_Days
- category and segment dummies

The model outputs:

- regression summary,
- R² and adjusted R²,
- F-statistic and p-values,
- residual diagnostics,
- actual vs predicted profit comparisons.

This section is valuable because it shows both prediction and explanatory power: not only can the model forecast profit, but it also reveals which variables most influence it.

---

## 6. Key Business Insights Derived from the Project

Although the project is more analytical than purely strategic, it supports several important retail conclusions:

- Profitability is not driven by volume alone; sales and discount patterns matter significantly.
- Geographical concentration across counties can signal local demand and logistics opportunity.
- Customer segmentation supports more intelligent promotion strategies.
- Missing data handling is essential in retail analytics because incomplete records can distort decision-making.
- Product categories and customer segments affect revenue and margin differently.
- Model-based analysis can guide pricing, discount, and inventory strategy.

These types of conclusions demonstrate strong business reasoning, which is important for both recruiter evaluation and internship or junior analyst roles.

---

## 7. Technical Architecture and Design Patterns

The project follows a clean and modular analytics architecture:

### Main patterns used

- Layered architecture: raw data → preprocessing → transformation → analytics → visualization
- Functional decomposition: each dashboard section is separated into dedicated functions
- ETL-inspired workflow: data is cleaned, enriched, and engineered before use in models
- Feature engineering: derived attributes support downstream analysis and prediction
- Business intelligence design: technical operations are framed around business questions

This architecture is efficient, readable, and easy to extend. It also communicates strong software engineering discipline and analytical thinking.

---

## 8. Tools and Technologies Used

- Python
- Streamlit
- Pandas
- NumPy
- Matplotlib
- GeoPandas
- Shapely
- Scikit-learn
- Statsmodels
- SAS (for academic/parallel analytical comparison)

This stack demonstrates a broad set of data-oriented skills: data wrangling, statistical analysis, visualization, geospatial analytics, and machine learning.

---

## 9. Project Value

This project is valuable because it does more than display charts: it shows the complete lifecycle of analytics work in a business context.

It demonstrates:

- strong Python programming foundations,
- practical analytics workflow design,
- data quality awareness,
- business problem framing,
- statistical and ML understanding,
- skills in communicating results through interactive visuals.

For recruiters, this makes the project highly relevant to roles in data analysis, business intelligence, analytics engineering, and data science.

---

## 10. Summary

FreshMart Insights Platform is a complete retail analytics project that combines operational data processing with business intelligence and predictive analytics. It bridges the gap between raw data and business decision-making, making it a strong portfolio project for demonstrating analytical capability, technical maturity, and practical understanding of real-world data challenges.
