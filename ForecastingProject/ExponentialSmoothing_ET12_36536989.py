
#Title: ET12 | Exponential Smoothing for (D) UK inland monthly energy consumption (ET12): [1995/01 - 2024/10]
#Author: 36536989


#################################
######## Library Imports ########
#################################
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from statsmodels.tsa.api import ExponentialSmoothing
from sklearn.metrics import mean_squared_error
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.stattools import adfuller
######################################
## Defining the Path for Data Files ##
######################################
my_path = "C:\\Users\\Engin-Eer\\OneDrive - University of Southampton\\Semester 2\\MATH6011 - Forecasting\\Assignment\\"
######################################



############################################################
########### ETL Process (Extract, Transform, Load) #########
############################################################
##Extract & Import
df4 = pd.read_excel(my_path + "Data_36536989.xls", sheet_name = "ET12",header=None)

##Data Transformation Process
#Actual header row is set as the header row
df4.columns = df4.iloc[5].values
#Unnecessary rows, annually, quarterly data is removed.
df4 = df4[6:364].reset_index(drop=True)
#Remove unwanted spaces
df4.iloc[:, 0] = df4.iloc[:, 0].str.strip()

#Converting January 1850 type of data to datetime.dt.date
df4.iloc[:,0] = pd.to_datetime(df4.iloc[:,0], format="%B %Y").dt.date #To convert 2025-2 data to datetime
#Replacing Date Column's name to 'Date'
df4.rename(columns={"Month": "Date"}, inplace=True)
df4.rename(columns={"Unadjusted total [note 1]": "Unadjusted total"}, inplace=True)

#Only getting the related columns to df4_cleaned dataframe
df4_cleaned = df4.iloc[:,[0,1]]

#Data Cleaning 
df4_cleaned.iloc[:, 1] = df4_cleaned.iloc[:, 1].astype(str).str.strip()
df4_cleaned.iloc[:, 1] = df4_cleaned.iloc[:, 1].apply(lambda x: x[0] if isinstance(x, list) else x)
df4_cleaned.iloc[:, 1] = df4_cleaned.iloc[:, 1].str.replace(r"[^\d.-]", "", regex=True)
df4_cleaned.iloc[:, 1] = pd.to_numeric(df4_cleaned.iloc[:, 1], errors="coerce")

#Assigning numeric value to a variable msta for ease of use.
et12 = df4_cleaned.iloc[:,1]
# Convert to numeric (forcing errors='coerce' to handle any non-numeric values)
et12 = pd.to_numeric(et12, errors='coerce')

##Checking Data Integrity
#Checking if there is any NA data in the time & anomaly columns
print("Number of Errors in ET12 data (date&value combined): " , df4_cleaned.iloc[:,0].isna().sum() + df4_cleaned.iloc[:,1].isna().sum())  # Count missing values
print(et12.head())
print(et12.dtypes)
print("----")


##########################################
########### Preliminary Analysis #########
##########################################
# 1) Test to Stationarity & Trend with Augmented Dickey-Fuller (ADF)
#ADF is the formal statistical test with Null Hypothesis(HO) : The data has a trend (Non-stationary).

result = adfuller(et12)  # Applying ADF Test on MSTA anomaly column
print("ADF Statistic:", result[0])
print("p-value:", result[1])

if result[1] < 0.05:
    print("Reject the null hypothesis (H0) → The data is stationary (No trend).")
else:
    print("Fail to reject the null hypothesis (H0) → The data has a trend (Non-stationary).")

#Results: 
# ADF Statistic: 0.9005088698649245
# p-value: 0.9930969636248911

#Thus, we fail to reject the null hypothesis (H0), which H0 was: The data has a trend (Non-stationary). In other words, the data is non-stationary, and has a trend.

# 2) Test for Seasonality with Autocorrelation Function (ACF) 
plot_acf(df4_cleaned.iloc[:,1], lags=24)  # Check for lags for every year
plt.show()

#Comment: 
#It is known that "Autocorrelations of a stationary time series drop to zero quite quickly." (p.16, Zemkoho)
#The dataset is significantly strongly seasonal.

############################################################################################################
############## Application of Holt-Winter Exponential Smoothing Forecasting Method to ET12 data ############
############################################################################################################

# Here, alpha = 0.3, beta=0.5, gamma=0.7
fit4 = ExponentialSmoothing(et12, seasonal_periods=14, seasonal='add').fit(smoothing_level=0.3, smoothing_seasonal=0.7)
fit4.fittedvalues.plot(color='red')

fit4.forecast(14).rename('Model with additive seasonality').plot(color='green', legend=True)
plt.xlabel('Dates')
plt.ylabel('Values')
plt.title('HW method-based forecasts for Inland energy consumption ')
plt.show()


#====================================
# Evaluating the errors
#====================================
MSE4=mean_squared_error(fit4.fittedvalues, et12)

#=====================================
# Printing the paramters and errors for each scenario
#=====================================
results=pd.DataFrame(index=[r"alpha", r"beta", r"gamma", r"l0"])
params = ['smoothing_level', 'smoothing_trend', 'smoothing_seasonal']
results["HW model 4"] = [fit4.params[p] for p in params] + [MSE4]
print(results)

#=====================================
# Evaluating and plotting the residual series for each scenario
#=====================================
residuals4= fit4.fittedvalues - et12
residuals4.rename('residual plot for model 4').plot(color='black', legend=True)
plt.title('Residual plot')
plt.show()

#=====================================
# ACF plots of the residual series for each scenario
#=====================================
plot_acf(residuals4, title='Residual ACF for model 4', lags=50)
plt.show()

#Printing out the Predicted Values
# Generate date range for 14 months from November 2024
forecast_dates2 = pd.date_range(start="2024-11", periods=14, freq="ME")

# Convert forecast to DataFrame
forecast_df4 = pd.DataFrame({
    "Date": forecast_dates2.strftime("%Y-%m"),
    "Forecasted Value": fit4.forecast(14).values
})

# Display the table
print(forecast_df4)

