
#Title: GMAF | Exponential Smoothing for (C) International Passenger Survey, UK visits abroad (GMAF): [1980/01 - 2023/12]
#Author: 36536989


#################################
######## Library Imports ########
#################################
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
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
df3 = pd.read_excel(my_path + "Data_36536989.xls", sheet_name = "GMAF",header=None)

##Data Transformation Process
#Actual header row is set as the header row
df3.columns = df3.iloc[1].values
#Unnecessary rows, annually, quarterly data is removed.
df3 = df3[227:].reset_index(drop=True)
#Converting 1850-Jan type of data to datetime.dt.date
df3.iloc[:,0] = pd.to_datetime(df3.iloc[:,0], format="%Y %b").dt.date #To convert 2025-2 data to datetime
#Replacing Date Column's name to 'Date'
df3.rename(columns={"CDID": "Date"}, inplace=True)
#Only getting the related columns to df3_cleaned dataframe
df3_cleaned = df3.iloc[:,[0,2]]
#Multiply data in GMAF column with 1000 as it is written in thousand format.
df3_cleaned.loc[:, "GMAF"] = df3_cleaned["GMAF"] * 1000
#Assigning numeric value to a variable msta for ease of use.
gmaf = df3_cleaned.iloc[:,1]
# Convert to numeric (forcing errors='coerce' to handle any non-numeric values)
gmaf = pd.to_numeric(gmaf, errors='coerce')
##Checking Data Integrity
#Checking if there is any NA data in the time & anomaly columns
print("Number of Errors in NOAA data (date&value combined): " , df3_cleaned.iloc[:,0].isna().sum() + df3_cleaned.iloc[:,1].isna().sum())  # Count missing values
print(gmaf.head())
print(gmaf.dtypes)
print("----")

##########################################
########### Preliminary Analysis #########
##########################################
# 1) Test to Stationarity & Trend with Augmented Dickey-Fuller (ADF)
#ADF is the formal statistical test with Null Hypothesis(HO) : The data has a trend (Non-stationary).

result = adfuller(gmaf)  # Applying ADF Test on MSTA anomaly column
print("ADF Statistic:", result[0])
print("p-value:", result[1])

if result[1] < 0.05:
    print("Reject the null hypothesis (H0) → The data is stationary (No trend).")
else:
    print("Fail to reject the null hypothesis (H0) → The data has a trend (Non-stationary).")

#Comment: 
# ADF Statistic: -2.2238126569636307
# p-value: 0.1977166211694808

#Thus, we fail to reject the null hypothesis (H0), which H0 was: The data has a trend (Non-stationary). In other words, the data is non-stationary, and has a trend.

# 2) Test for Seasonality with Autocorrelation Function (ACF) 
plot_acf(df3_cleaned.iloc[:,1], lags=60)  # Check for lags for every year
plt.show()

#Comment: 
#It is known that "Autocorrelations of a stationary time series drop to zero quite quickly." (p.16, Zemkoho)
#The dataset is non-stationary as ACF values decrease slowly, or in other way, does not drop to zero quickly. Increasing lags parameter from 12 to greater values caluse waves in ACF graph to interact with the blue zone. Thus, Seasonal or cyclic behavior is present.

#Both tests confirm that the data has a trend, does not have any strong seasonality, and it is non-stationary. For such case, the best exponential smoothing forecasting method for MSTA data is Holt Linear Exponential Smoothing Forecasting Method. This method is useful when data involves trend without the presence of seasonality.



############################################################################################################
############## Application of Holt-Winter Exponential Smoothing Forecasting Method to GMAF data ############
############################################################################################################

# Here, alpha = 0.3, beta=0.5, gamma=0.7
fit3 = ExponentialSmoothing(gmaf, seasonal_periods=24, trend='add', seasonal='add').fit(smoothing_level = 0.3, smoothing_trend=0.5,  smoothing_seasonal=0.7)
fit3.fittedvalues.plot(color='red')

fit3.forecast(24).rename('Model with additive seasonality').plot(color='green', legend=True)
plt.xlabel('Dates')
plt.ylabel('Values')
plt.title('HW method-based forecasts for GMAF')
plt.show()


#====================================
# Evaluating the errors
#====================================
MSE3=mean_squared_error(fit3.fittedvalues, gmaf)

#=====================================
# Printing the paramters and errors for each scenario
#=====================================
results=pd.DataFrame(index=[r"alpha", r"beta", r"gamma", r"l0"])
params = ['smoothing_level', 'smoothing_trend', 'smoothing_seasonal']
results["HW model 3"] = [fit3.params[p] for p in params] + [MSE3]
print(results)

#=====================================
# Evaluating and plotting the residual series for each scenario
#=====================================
residuals3= fit3.fittedvalues - gmaf
residuals3.rename('residual plot for model 3').plot(color='black', legend=True)
plt.title('Residual plot')
plt.show()

#=====================================
# ACF plots of the residual series for each scenario
#=====================================
plot_acf(residuals3, title='Residual ACF for model 3', lags=50)
plt.show()

#Printing out the Predicted Values
# Generate date range for 24 months from Jan 2024
forecast_dates4 = pd.date_range(start="2024-01", periods=24, freq="ME")

# Convert forecast to DataFrame
forecast_df3 = pd.DataFrame({
    "Date": forecast_dates4.strftime("%Y-%m"),
    "Forecasted Value": fit3.forecast(24).values
})

# Display the table
print(forecast_df3)

