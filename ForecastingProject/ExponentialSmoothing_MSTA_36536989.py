
#Title:MSTA | Exponential Smoothing for (A) Global Mean Surface Temperature Anomaly (MSTA) in ◦C: [1850/01 - 2024/12]
#Author: 36536989

#################################
######## Library Imports ########
#################################

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from statsmodels.tsa.api import Holt
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_squared_error

######################################
## Defining the Path for Data Files ##
######################################

my_path = "C:\\Users\\Engin-Eer\\OneDrive - University of Southampton\\Semester 2\\MATH6011 - Forecasting\\Assignment\\"

######################################


############################################################
########### ETL Process (Extract, Transform, Load) #########
############################################################

##Extract & Import
df1 = pd.read_excel(my_path + "Data_36536989.xls", sheet_name = "MSTA")

##Data Transformation Process
#Only getting the related columns to df1_cleaned dataframe
df1_cleaned = df1.iloc[:,[0,1]].reset_index(drop=True)
#Converting 1850-01 type of data to datetime.dt.date
df1_cleaned.iloc[:,0] = pd.to_datetime(df1_cleaned.iloc[:,0], format="%Y-%m").dt.date #To convert 2025-02 data to datetime
#Replacing Name
df1_cleaned.rename(columns={"Time": "Date"}, inplace=True)
#Assigning numeric value to a variable msta for ease of use.
msta = df1_cleaned.iloc[:,1]

##Checking Data Integrity
#Checking if there is any NA data in the time & anomaly columns
print("Number of Errors in MSTA data (date&anomaly combined): " , df1_cleaned.iloc[:,0].isna().sum() + df1_cleaned.iloc[:,1].isna().sum())  # Count missing values
print(msta.head())
print(msta.dtypes)
print("---")


##########################################
########### Preliminary Analysis #########
##########################################
# 1) Test to Stationarity & Trend with Augmented Dickey-Fuller (ADF)
#ADF is the formal statistical test with Null Hypothesis(HO) : The data has a trend (Non-stationary).

result = adfuller(msta)  # Applying ADF Test on MSTA anomaly column
print("ADF Statistic:", result[0])
print("p-value:", result[1])

if result[1] < 0.05:
    print("Reject the null hypothesis (H0) → The data is stationary (No trend).")
else:
    print("Fail to reject the null hypothesis (H0) → The data has a trend (Non-stationary).")

#Comment: 
#ADF Statistic: -0.0742450811332073
#p-value: 0.9519441645991623
#Thus, we fail to reject the null hypothesis (H0), which H0 was: The data has a trend (Non-stationary). In other words, the data is non-stationary, and has a trend.

# 2) Test for Seasonality with Autocorrelation Function (ACF) 
plot_acf(df1_cleaned.iloc[:,1], lags=12)  # Check for lags for every year
plt.show()

#Comment: 
#It is known that "Autocorrelations of a stationary time series drop to zero quite quickly." (p.16, Zemkoho)
#The dataset is non-stationary as ACF values decrease slowly, or in other way, does not drop to zero quickly. Changing lags parameter from 12 to 120 (1 year to 10 years) does not seem to change this result.

#Both tests confirm that the data has a trend, does not have any strong seasonality, and it is non-stationary. For such case, the best exponential smoothing forecasting method for MSTA data is Holt Linear Exponential Smoothing Forecasting Method. This method is useful when data involves trend without the presence of seasonality.

############################################################################################################
############## Application of Holt Double Exponential Smoothing Forecasting Method to MSTA data ############
############################################################################################################
#Holt's double forecasting basically works by adding a trend component to SES method, and it only predicts one step ahead.
#Here, Exponential,Damped or Auto-optimized models are not used as anomaly data flactuates between +-1.5, and so, anomalies can be negative.
#a) The goal is to forecast monthly behaviour until December 2025.
# Holt model 1: alpha = 0.8, beta=0.2
fit1 = Holt(msta).fit(smoothing_level=0.8, smoothing_trend=0.2, optimized=False)
fcast1 = fit1.forecast(12).rename("Holt's linear trend")

plt.figure(figsize=(12, 6))

# Plot original data
plt.plot(df1_cleaned["Date"], df1_cleaned.iloc[:, 1], color='black', label='MSTA Data')

# Plot Holt’s fitted values
plt.plot(df1_cleaned["Date"], fit1.fittedvalues, color='blue', label="Fitted Values")

# # Plot forecasted values for 12 months (until 2025 december)
plt.plot(pd.date_range(df1_cleaned["Date"].iloc[-1], periods=12, freq='ME'), 
         fcast1, 
         color='red', 
         linewidth=2.5, 
         linestyle='solid', 
         label="The Forecast")

# Formatting
plt.legend()
plt.xlabel("Date")
plt.ylabel("MSTA Anomaly")
plt.title("Holt Linear Exponential Smoothing Forecasting Method to MSTA data")
plt.show()

##Evaluating the error
MSE1=mean_squared_error(fit1.fittedvalues, msta)


print('Summary of errors resulting from the SES model')

#Printing Errors for each model using MSE
cars = {'Model': ['MSE'],
        'LES model 1': [MSE1],
        }
AllErrors = pd.DataFrame(cars, columns = ['Model', 'LES model 1'])
print(AllErrors)

#Comments
# MSE indicates forecasting error, so lower the better. By looking at MSE errors, the goal is minimizing forecasting errors. 
#The data is about Temperature anomalies. Since it tend to fluctuate rather than follow a strict increasing or decreasing trend, this model logically makes sense.


## ACF of the residuals is created for each method to test the performance of each method.
# Calculate residuals (Actual - Fitted)
residuals1 = msta - fit1.fittedvalues


#Plots for Residuals
plt.figure(figsize=(12, 6))
plt.subplot(3, 1, 1)
plt.plot(residuals1, color='blue')
plt.title("Residuals of Holt's Linear Trend Model")
plt.tight_layout()
plt.show()

# ACF Plots for Residuals
plt.figure(figsize=(12, 6))

plt.subplot(3, 1, 1)
plot_acf(residuals1.dropna(), lags=50, title="ACF of Residuals (Holt's Linear Trend)", ax=plt.gca())

plt.tight_layout()
plt.show()

#Comment
#Visuals show that significantly majority of the points in the ACF plot fall within the blue shaded area (confidence bounds). Thus, there is no significant autocorrelation in the residuals. It is promising, as it means that the model effectively captured most of the patterns in data.

#Output for Forecasted Values
forecast_dates = pd.date_range(start="2025-01", periods=12, freq='ME')

# Create DataFrame for forecasted values
forecast_df = pd.DataFrame({"Date": forecast_dates, "Forecasted Value": fcast1.values})

# Print the DataFrame
print(forecast_df)
