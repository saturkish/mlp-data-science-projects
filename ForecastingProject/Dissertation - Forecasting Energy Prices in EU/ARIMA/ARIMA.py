# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 16:30:17 2025
#This code is designed to forecast natural gas prices using ARIMA method.
@Author: Ahmet Engin ADIYAMAN
"""

###################################
##0)Imports
###################################
#Class Imports
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.stats.diagnostic import acorr_ljungbox

#Data Imports
path = "C:/Users/Engin-Eer/OneDrive - University of Southampton/Semester 2/Cormsis/Dissertation/Dissertation/Forecasting/"
raw = pd.read_excel(path + "wb.xlsx",  header=0,sheet_name = "WB",usecols=range(3,7))
###################################


###################################
#1)Preliminary Analysis
###################################

###################################
#1.1) Test to Stationarity with Augmented Dickey-Fuller (ADF)
###################################
#ADF is the formal statistical test with Null Hypothesis(HO) : The data has a trend (Non-stationary).

result = adfuller(raw["price"])  #Applying ADF Test
print('p-value:', result[1])

print("---")
if result[1] < 0.05:
    print("Reject the null hypothesis (H0) → The data is stationary (No trend).")
else:
    print("Fail to reject the null hypothesis (H0) → The data has a trend (Non-stationary).")
    
#p-value: 0.045
#Reject the null hypothesis (H0) → The data is stationary (No trend).
#Thus, no differencing applied. d=0 for ARIMA(p,d,q).

###################################
#1.2) Test for Seasonality with Autocorrelation Function (ACF), and to decide q as input for ARIMA(p,d,q)
###################################

#Since the series is now stationary after differencing, we can check seasonality using ACF.
plot_acf(raw['price'], lags=36)
plt.title("ACF of Original Series")
plt.show()

#ACF decays quickly and does not peak again significantly at later lags, resulting non-seasonality. 
#Thus, ARIMA is chosen instead of SARIMA, as seasonality is proven not to be in the picture. 

###################################
#1.3) PACF test, and defining p value as input for ARIMA(p,d,q)
###################################
plt.figure(figsize=(8, 5))
plot_pacf(raw['price'], lags=12, method='ywm')
plt.title('PACF of Energy Price Data')
plt.tight_layout()
plt.show()
#PACF test shows drop in 3rd step, determining p=3 for the ARIMA input.



###################################################
############## 2)Application of ARIMA(p=3,d=0,q=2) for 12 months forecast #############
###################################################
# Build model manually based on your analysis
model = ARIMA(raw['price'], order=(3,0, 2))
fit = model.fit()

# Summary
print(fit.summary())

# Diagnostic plots
fit.plot_diagnostics(figsize=(10, 6))
plt.tight_layout()
plt.show()

#The Forecast Using ARIMA 2,2,0
forecast = fit.forecast(steps=12)

#Create date index starting from July 2025
start_date = '2025-07'
forecast.index = pd.date_range(start=start_date, periods=len(forecast), freq='M')

#Fixing the index issue for raw dataframe
raw.index = raw["date"]
# Plot forecast vs actual
forecast.plot(label='Forecast', color='green')
raw['price'].plot(label='Actual', color='blue')
plt.title('ARIMA(3,0,2) 12 months Forecast for Natural Gas Data')
plt.legend()
plt.grid(True)
plt.show()

#Model AIC Value = 574 successfully achieved through ARIMA(3,0,2)


###################################################
############## 3)Application of ARIMA(p=3,d=0,q=2) for 5 years forecast #############
###################################################
# Build model manually based on your analysis
model = ARIMA(raw['price'], order=(3,0, 2))
fit = model.fit()

# Summary
print(fit.summary())

# Diagnostic plots
fit.plot_diagnostics(figsize=(10, 6))
plt.tight_layout()
plt.show()

#The Forecast Using ARIMA 2,2,0
forecast2 = fit.forecast(steps=60)


#Create date index starting from July 2025
start_date = '2025-07'
forecast2.index = pd.date_range(start=start_date, periods=len(forecast2), freq='M')

# Plot forecast vs actual
forecast2.plot(label='Forecast', color='green')
raw['price'].plot(label='Actual', color='blue')
plt.title('ARIMA(3,0,2) 5 Year Forecast for Natural Gas Data')
plt.legend()
plt.grid(True)
plt.show()

###################################################
############## 4)Application of ARIMA(p=3,d=0,q=2) for 10 years forecast #############
###################################################
# Build model manually based on your analysis
model = ARIMA(raw['price'], order=(3,0, 2))
fit2 = model.fit()

# Summary
print(fit2.summary())

# Diagnostic plots
fit2.plot_diagnostics(figsize=(10, 6))
plt.tight_layout()
plt.show()

#The Forecast Using ARIMA 2,2,0
forecast2 = fit2.forecast(steps=120)


#Create date index starting from July 2025
start_date = '2025-07'
forecast2.index = pd.date_range(start=start_date, periods=len(forecast2), freq='M')

# Plot forecast vs actual
forecast2.plot(label='Forecast', color='green')
raw['price'].plot(label='Actual', color='blue')
plt.title('ARIMA(3,0,2) 10 Year Forecast for Natural Gas Data')
plt.legend()
plt.grid(True)
plt.show()



###################################################

#Verifying ARIMA model accuracy with ACF / PACF of residues
residuals = fit.resid
residuals2 = fit2.resid

# Set up subplots
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot ACF
plot_acf(residuals, lags=36, ax=axes[0])
axes[0].set_title('ACF of Residuals')

# Plot PACF
plot_pacf(residuals, lags=36, ax=axes[1], method='ywm')
axes[1].set_title('PACF of Residuals')

plt.tight_layout()
plt.show()

#Ljung-Box test
lb_test = acorr_ljungbox(residuals, lags=[10, 20], return_df=True)
print(lb_test)

#Plots of ACF&PACF successfully states that the model has worked accurately.

#The Ljung-Box test checks whether your residuals are white noise. 
#The null hypothesis (H₀): Residuals are independently distributed (i.e., white noise).
#The alternative (H₁): Residuals are autocorrelated at the tested lag.

#p-values are very high (> 0.05). Thus, we fail to reject the null hypothesis.
#Ljung-Box test shows that there is no significant autocorrelation left in the residuals, and the model worked accurately.
