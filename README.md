# 📈 Sales Forecasting

## 📌 Project Overview
This project analyzes historical sales data and builds a simple machine learning model to forecast future sales.  
The goal is to understand sales trends over time and establish a baseline forecasting approach using linear regression.

---

## 🎯 Objectives
- Explore and analyze historical sales data
- Visualize sales trends over time
- Build a basic forecasting model
- Compare actual sales with predicted values

---

## 🧰 Technologies Used
- Python
- Pandas
- NumPy
- Matplotlib
- Scikit-learn
- Jupyter Notebook

---

## 📂 Project Structure
sales-forecasting/
│
├── data/
│ └── sales.csv
│
├── visuals/
│ └── sales_trend.png
│
├── sales_forecasting.ipynb
└── README.md


---

## 📊 Data Description
The dataset contains historical sales information with the following variables:
- `time_index`: numerical representation of time
- `sales`: recorded sales values

---

## 🧠 Modeling Approach
A **Linear Regression** model was used to model the relationship between time and sales.

### Steps:
1. Load and explore the dataset
2. Define the feature (`time_index`) and target (`sales`)
3. Train a linear regression model
4. Generate sales predictions
5. Visualize actual vs predicted sales

---

## 📈 Model Interpretation
The linear regression model captures the overall trend in sales over time.  
While simple, it provides a useful baseline for forecasting.

Limitations:
- Does not account for seasonality
- Ignores external factors (promotions, market changes)
- Assumes a linear relationship

Future improvements could include:
- Time series models (ARIMA, Prophet)
- Feature engineering
- More advanced regression techniques

---

## 🚀 Results
The model successfully learns the general sales trend and produces reasonable predictions for future sales.

---

## 👤 Author
Seth Junior 
Aspiring Data Scientist | Python | Machine Learning
