
#Title:CH4 | Exponential Smoothing for (B) Global Monthly Atmospheric Carbon Dioxide Levels (CH4): [1983/07 - 2024/09]
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
df2 = pd.read_excel(my_path + "Data_36536989.xls", sheet_name = "CH4")

##Data Transformation Process
#Merging Year&Month, and converting it to datetime
df2["Date"] = df2["Year"].astype(str) + "-" + df2["Month"].astype(str)
#Converting 1850-1 type of data to datetime.dt.date
df2.iloc[:,4] = pd.to_datetime(df2.iloc[:,4], format="%Y-%m").dt.date #To convert 2025-2 data to datetime
#Only getting the related columns to df2_cleaned dataframe
df2_cleaned = df2.iloc[:,[4,2]].reset_index(drop=True)
#Assigning numeric value to a variable noaa for ease of use.
ch4 = df2_cleaned.iloc[:,1]

##Checking Data Integrity
#Checking if there is any NA data in the time & anomaly columns
print("Number of Errors in NOAA data (date&value combined): " , df2_cleaned.iloc[:,0].isna().sum() + df2_cleaned.iloc[:,1].isna().sum())  # Count missing values
print(ch4.head())
print(ch4.dtypes)
print("----")

##########################################
########### Preliminary Analysis #########
##########################################
# 1) Test to Stationarity & Trend with Augmented Dickey-Fuller (ADF)
#ADF is the formal statistical test with Null Hypothesis(HO) : The data has a trend (Non-stationary).

result = adfuller(ch4)  # Applying ADF Test on MSTA anomaly column
print("ADF Statistic:", result[0])
print("p-value:", result[1])

if result[1] < 0.05:
    print("Reject the null hypothesis (H0) → The data is stationary (No trend).")
else:
    print("Fail to reject the null hypothesis (H0) → The data has a trend (Non-stationary).")

#Comment: 
# ADF Statistic: 0.40951780686081724
# p-value: 0.981847404731031

#Thus, we fail to reject the null hypothesis (H0), which H0 was: The data has a trend (Non-stationary). In other words, the data is non-stationary, and has a trend.

# 2) Test for Seasonality with Autocorrelation Function (ACF) 
plot_acf(df2_cleaned.iloc[:,1], lags=12)  # Check for lags for every year
plt.show()

#Comment: 
#It is known that "Autocorrelations of a stationary time series drop to zero quite quickly." (p.16, Zemkoho)
#The dataset is non-stationary as ACF values decrease slowly, or in other way, does not drop to zero quickly. Changing lags parameter from 12 to 120 (1 year to 10 years) does not seem to change this result.

#Both tests confirm that the data has a trend, does not have any strong seasonality, and it is non-stationary. For such case, the best exponential smoothing forecasting method for MSTA data is Holt Linear Exponential Smoothing Forecasting Method. This method is useful when data involves trend without the presence of seasonality.


############################################################################################################
############## Application of Holt-Winter Exponential Smoothing Forecasting Method to CH4 data #############
############################################################################################################

# Here, alpha = 0.3, beta=0.5, gamma=0.7
fit2 = ExponentialSmoothing(ch4, seasonal_periods=15, trend='add', seasonal='add').fit(smoothing_level = 0.3, smoothing_trend=0.5,  smoothing_seasonal=0.7)
fit2.fittedvalues.plot(color='red')

fit2.forecast(15).rename('Model with additive seasonality').plot(color='green', legend=True)
plt.xlabel('Dates')
plt.ylabel('Values')
plt.title('HW method-based forecasts for CH4')
plt.show()


#====================================
# Evaluating the errors
#====================================
MSE2=mean_squared_error(fit2.fittedvalues, ch4)

#=====================================
# Printing the paramters and errors for each scenario
#=====================================
results=pd.DataFrame(index=[r"alpha", r"beta", r"gamma", r"l0"])
params = ['smoothing_level', 'smoothing_trend', 'smoothing_seasonal']
results["HW model 2"] = [fit2.params[p] for p in params] + [MSE2]
print(results)

#=====================================
# Evaluating and plotting the residual series for each scenario
#=====================================
residuals2= fit2.fittedvalues - ch4
residuals2.rename('residual plot for model 2').plot(color='black', legend=True)
plt.title('Residual plot')
plt.show()

#=====================================
# ACF plots of the residual series for each scenario
#=====================================
plot_acf(residuals2, title='Residual ACF for model 2', lags=50)
plt.show()

#Printing out the Predicted Values
# Generate date range for 14 months from November 2024
forecast_dates3 = pd.date_range(start="2024-10", periods=15, freq="ME")

# Convert forecast to DataFrame
forecast_df2 = pd.DataFrame({
    "Date": forecast_dates3.strftime("%Y-%m"),
    "Forecasted Value": fit2.forecast(15).values
})

# Display the table
print(forecast_df2)

