#-*- coding: utf-8 -*-
"""
Created on Mon Jul 14 17:27:56 2025
#This code is designed to forecast natural gas prices using Exponential Smoothing method.
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
from sklearn.metrics import mean_squared_error
#Data Imports
path = "C:/Users/Engin-Eer/OneDrive - University of Southampton/Semester 2/Cormsis/Dissertation/Dissertation/Forecasting/"
raw = pd.read_excel(path + "wb.xlsx",  header=0,sheet_name = "WB",usecols=range(3,7))
###################################


####################################################################################################################
##############Application of Holt Double Exponential Smoothing Forecasting Method to Natural Gas  data ############
####################################################################################################################

#Holt's double forecasting basically works by adding a trend component to SES method, and it only predicts one step ahead.
#Here, Exponential,Damped or Auto-optimized models are not used as anomaly data flactuates between +-1.5, and so, anomalies can be negative.
#a) The goal is to forecast monthly behaviour until December 2025.
#Holt model 1: alpha = 0.8, beta=0.2
#Step 1: Ensure datetime index is set
raw.index = raw["date"]
raw.set_index('date', inplace=True)

#Step 2: Fit Holt’s Linear Trend Model
#fit1 = Holt(raw['price']).fit(smoothing_level=0.8, smoothing_trend=0.4, optimized=False)
fit1 = Holt(raw['price']).fit(optimized=True)
#Step 3: Forecast next 12 months
fcast1 = fit1.forecast(120).rename("Holt's linear trend")

#Step 4: Create proper date index for forecast
last_date = raw.index[-1]
forecast_index = pd.date_range(start=last_date + pd.offsets.MonthEnd(1), periods=120, freq='M')
fcast1.index = forecast_index

#Step 5: Plotting
plt.figure(figsize=(12, 6))

#Original data
plt.plot(raw['price'], color='black', label='Original Data')

#Fitted values
plt.plot(fit1.fittedvalues, color='blue', label='Fitted Model')

#Forecast
plt.plot(fcast1, color='red', linewidth=2.5, linestyle='solid', label='The Forecast')

#Formatting
plt.legend()
plt.xlabel("Date")
plt.ylabel("Natural Gas Price Anomaly")
plt.title("Holt Linear Exponential Smoothing Forecast for Natural Gas Data")
plt.grid(True)
plt.show()

##########################
##Testing Model Accuracy##
##########################
##Evaluating the error
MSE1=mean_squared_error(fit1.fittedvalues, raw["price"])


print('Summary of errors resulting from the SES model')

#Printing Errors for each model using MSE
cars = {'Model': ['MSE'],
        'LES model 1': [MSE1],
        }
AllErrors = pd.DataFrame(cars, columns = ['Model', 'LES model 1'])
print(AllErrors)

#Comments
#MSE indicates forecasting error, so lower the better. By looking at MSE errors, the goal is minimizing forecasting errors. 
#The data is about Temperature anomalies. Since it tend to fluctuate rather than follow a strict increasing or decreasing trend, this model logically makes sense.


##ACF of the residuals is created for each method to test the performance of each method.
#Calculate residuals (Actual - Fitted)
residuals1 = raw["price"] - fit1.fittedvalues


#Plots for Residuals
plt.figure(figsize=(12, 6))
plt.subplot(3, 1, 1)
plt.plot(residuals1, color='blue')
plt.title("Residuals of Holt's Linear Trend Model")
plt.tight_layout()
plt.show()

#ACF Plots for Residuals
plt.figure(figsize=(12, 6))

plt.subplot(3, 1, 1)
plot_acf(residuals1.dropna(), lags=50, title="ACF of Residuals (Holt's Linear Trend)", ax=plt.gca())

plt.tight_layout()
plt.show()

#Comment
#Visuals show that significantly majority of the points in the ACF plot fall within the blue shaded area (confidence bounds). Thus, there is no significant autocorrelation in the residuals. It is promising, as it means that the model effectively captured most of the patterns in data.
