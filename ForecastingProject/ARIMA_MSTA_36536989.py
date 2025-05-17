
#Title:MSTA | Arima Analysis: [1850/01 - 2024/12]
#Author: 36536989

############################################################
############ Use of ARIMA Method to pridict MSTA ###########
############################################################
########################################################################################################################
# 0. Set-ups
########################################################################################################################

# Generally required
import pandas as pd
import numpy as np
# Plotting
import matplotlib
import seaborn as sns
import matplotlib.pyplot as plt
#matplotlib.use('Qt5Agg')

#sns.set_style("whitegrid")

# ACF, PACF
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
#Arima
from statsmodels.tsa.arima.model import ARIMA
#white noise test
from statsmodels.stats.diagnostic import acorr_ljungbox

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
#ser = pd.read_excel(file, sheet_name='Data2', header=0, index_col=0, parse_dates=True).squeeze()

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
#print("Number of Errors in MSTA data (date&anomaly combined): " , df1_cleaned.iloc[:,0].isna().sum() + df1_cleaned.iloc[:,1].isna().sum())  # Count missing values
#print(msta.head())
#print(msta.dtypes)

########################################################################################################################
# 2. Create 1st difference
########################################################################################################################

# First difference, then second difference, and so on.
diff = msta.diff().dropna()
diff2 = msta.diff().diff().dropna()  
diff3 = msta.diff().diff().diff().dropna()
diff4 = msta.diff().diff().diff().diff().dropna()
diff5 = msta.diff().diff().diff().diff().diff().dropna()
#It is concluded that first difference (d=1) returns the best AIC resut. Thus currentdiff =diff
currentdiff=diff
########################################################################################################################
# 2. Plotting ACF & PACF to decide on ARIMA Model
########################################################################################################################

# Create figure
fig, ax = plt.subplots(3, 1, figsize=(10, 7))

# Time plot
ax[0].plot(currentdiff)
ax[0].set_title('Time plot of MSTA for the difference')

# ACF
plot_acf(currentdiff, title='ACF of MSTA for the difference', lags=50, ax=ax[1])

# PACF
plot_pacf(currentdiff, title='PACF of MSTA for the difference', lags=50, ax=ax[2])

plt.tight_layout()
plt.show()


################################################
#########    ARIMA (p,d,q) model   #############
################################################


# Define ARIMA model with (p, d, q)
model = ARIMA(currentdiff, order=(1,1,2)) 
model_fit = model.fit()

# Print summary
print(model_fit.summary())

# Convert residuals to Pandas Series
residuals = pd.Series(model_fit.resid)

# Plot residuals
residuals.plot(title="Residuals Plot")
plt.show()

############################################################
#############    ACF & PACF of residuals   #################
############################################################
#Plotting ACF & PACF of residuals
fig, axes = plt.subplots(1, 2, figsize=(15, 5))

# ACF Plot (Checks if residuals are autocorrelated)
plot_acf(residuals, ax=axes[0], lags=40)
axes[0].set_title("ACF of Residuals")

# PACF Plot (Checks if partial autocorrelation exists)
plot_pacf(residuals, ax=axes[1], lags=40, method="ywm")
axes[1].set_title("PACF of Residuals")

plt.show()

############################################
########## Ljung-Box Test    ###############
############################################

# Apply Ljung-Box test (default lags=10) to see if it is white noise
ljung_box = acorr_ljungbox(residuals, lags=[10], return_df=True)
print("Ljung-Box Test Results:")
print(ljung_box)

#################################################################
########## 12-Step Forecasting with ARIMA Model   ###############
#################################################################
# Forecast 12 steps ahead
forecast_steps = 12
forecast_values = model_fit.forecast(steps=forecast_steps)

# Create a date range for the forecasted values
forecast_dates = pd.date_range(start=df1_cleaned["Date"].iloc[-1], periods=forecast_steps + 1, freq='ME')[1:]

# Convert forecast values to DataFrame for better visualization
forecast_df = pd.DataFrame({"Date": forecast_dates, "Forecast": forecast_values})

# Print forecasted values
print(forecast_df)

# Plot forecast
plt.figure(figsize=(10, 5))
plt.plot(df1_cleaned["Date"], msta, label="Actual MSTA")
plt.plot(forecast_df["Date"], forecast_df["Forecast"], marker='o', linestyle="dashed", color="red", label="Forecast")
plt.xlabel("Date")
plt.ylabel("MSTA")
plt.legend()
plt.title("12-Step-Ahead ARIMA Forecast for MSTA")
plt.grid()
plt.show()


########################################################################
#############    Auto-Arima for parameter estimation   #################
########################################################################
!pip install pmdarima
from pmdarima import auto_arima

auto_model = auto_arima(currentdiff, seasonal=False, stepwise=True, trace=True)
print(auto_model.summary())
