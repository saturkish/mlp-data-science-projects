#-*- coding: utf-8 -*-
"""
Created on Tue Jul 15 13:12:24 2025
#This code is designed to forecast natural gas prices using Random Forest ML model.
@Author: Ahmet Engin ADIYAMAN
"""

###################################
##0)Imports
###################################
#Class Imports
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from statsmodels.tsa.api import Holt
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

#Data Imports
path = "C:/Users/Engin-Eer/OneDrive - University of Southampton/Semester 2/Cormsis/Dissertation/Dissertation/Forecasting/"
raw = pd.read_excel(path + "wb.xlsx",  header=0,sheet_name = "WB",usecols=range(3,7))
###################################
##1)Creating Lags
###################################
#Create lag features sucj that lag 1, lag 2, lag 3 months
for lag in range(1, 11):
    raw[f'lag_{lag}'] = raw['price'].shift(lag)
raw_lagged = raw.dropna().reset_index(drop=True)
X = raw_lagged[[f'lag_{lag}' for lag in range(1, 11)]]
y = raw_lagged['price']


#Dropping rows with NaN values due to shifting
raw_lagged = raw.dropna().reset_index(drop=True)
###################################
##2)Forecasting with XGBoost
###################################
lags = [f'lag_{i}' for i in range(1, 11)]
raw_lagged = raw.dropna().reset_index(drop=True)

X = raw_lagged[lags]
y = raw_lagged['price']

# Splitting data into train and test sets
test_size = 101


# Same X, y, lags already created
X_train, X_test = X[:-test_size], X[-test_size:]
y_train, y_test = y[:-test_size], y[-test_size:]

xgb = XGBRegressor(n_estimators=100, learning_rate=0.15, max_depth=1, random_state=42)
xgb.fit(X_train, y_train)   
y_pred = xgb.predict(X_test)

rmse = mean_squared_error(y_test, y_pred, squared=False)
r2 = r2_score(y_test, y_pred)

print(f"XGBoost RMSE: {rmse:.4f}")
print(f"XGBoost R²: {r2:.4f}")



# Forecast next 10 years (rolling prediction)
last_known = X_test.iloc[-1].values
forecast = []
for _ in range(120):   # <-- That’s 101 predictions
    pred = xgb.predict(last_known.reshape(1, -1))[0]
    forecast.append(pred)
    last_known = np.roll(last_known, -1)
    last_known[-1] = pred



#print("Next 10 years' forecast:")
#print(np.round(forecast,5))