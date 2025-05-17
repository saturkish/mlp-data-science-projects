
#Title: Multiple Regression Model for MSTA using CH4, GMAF, and ET12 - Until December 2025
#Author: 36536989



#################################
######## Library Imports ########
#################################
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime
# OLS
from statsmodels.formula.api import ols
from statsmodels.tsa.api import Holt
#plot
import matplotlib.pyplot as plt
from statsmodels.tsa.api import ExponentialSmoothing
import seaborn as sns
######################################
## Defining the Path for Data Files ##
######################################
my_path = "C:\\Users\\Engin-Eer\\OneDrive - University of Southampton\\Semester 2\\MATH6011 - Forecasting\\Assignment\\"
######################################


############################################################################################################
############## Multiple Regression Model for MSTA using CH4, GMAF, and ET12 - Until December 2025 ##########
############################################################################################################
##############################################################
########### ETL Processes (Extract, Transform, Load) #########
##############################################################

####################
####### MSTA #######
####################
##Extract & Import
df1 = pd.read_excel(my_path + "Data_36536989.xls", sheet_name = "MSTA")

##Data Transformation Process
#Only getting the related columns to df1_cleaned dataframe
df1_cleaned = df1.iloc[:,[0,1]].reset_index(drop=True)
#Converting 1850-01 type of data to datetime.dt.date
df1_cleaned.iloc[:,0] = pd.to_datetime(df1_cleaned.iloc[:,0], format="%Y-%m").dt.date #To convert 2025-02 data to datetime
#Replacing Name
df1_cleaned.rename(columns={"Time": "Date"}, inplace=True)
#Setting starting  date to 1995: the common starting date for all
df1_cleaned = df1_cleaned[df1_cleaned.iloc[:,0] >= datetime(1995, 1, 1).date()]
#Assigning numeric value to a variable msta for ease of use.
msta = df1_cleaned.iloc[:,1]


####################
####### CH4 ########
####################
##Extract & Import
df2 = pd.read_excel(my_path + "Data_36536989.xls", sheet_name = "CH4")

##Data Transformation Process
#Merging Year&Month, and converting it to datetime
df2["Date"] = df2["Year"].astype(str) + "-" + df2["Month"].astype(str)
#Converting 1850-1 type of data to datetime.dt.date
df2.iloc[:,4] = pd.to_datetime(df2.iloc[:,4], format="%Y-%m").dt.date #To convert 2025-2 data to datetime
#Only getting the related columns to df2_cleaned dataframe
df2_cleaned = df2.iloc[:,[4,2]].reset_index(drop=True)
#Setting starting  date to 1995: the common starting date for all
df2_cleaned = df2_cleaned[df2_cleaned.iloc[:,0] >= datetime(1995, 1, 1).date()]

# Creating a new DataFrame with the additional data points
new_data = pd.DataFrame({
    df2_cleaned.columns[0]: pd.to_datetime(pd.Series(['2024-10', '2024-11', '2024-12']), format="%Y-%m").dt.date, #To convert 2025-2 data to datetime
    df2_cleaned.columns[1]: [1927.384238, 1934.768029, 1942.826338]
})

# Appending to df2_cleaned
df2_cleaned = pd.concat([df2_cleaned, new_data], ignore_index=False).reset_index(drop=True)

#Assigning numeric value to a variable noaa for ease of use.
ch4 = df2_cleaned.iloc[:,1]

####################
####### GMAF #######
####################
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
#Setting starting  date to 1995: the common starting date for all
df3_cleaned = df3_cleaned[df3_cleaned.iloc[:,0] >= datetime(1995, 1, 1).date()]

# Creating a new DataFrame with the additional 12 data points
new_data = pd.DataFrame({
    df3_cleaned.columns[0]: pd.to_datetime(pd.Series([
        '2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06',
        '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12'
    ]), format="%Y-%m").dt.date,  

    df3_cleaned.columns[1]: [
        3.100717e+06, 2.317635e+06, 1.683955e+06, 1.373733e+06, -3.917493e+05,
        -4.494491e+05, -1.611117e+06, 3.667535e+05, -6.141615e+05, -1.727846e+06,
        -4.469104e+06, -4.988030e+06
    ]
})

# Appending to df3_cleaned
df3_cleaned = pd.concat([df3_cleaned, new_data], ignore_index=True)

#Assigning numeric value to a variable msta for ease of use.
gmaf = df3_cleaned.iloc[:,1]
# Convert to numeric (forcing errors='coerce' to handle any non-numeric values)
gmaf = pd.to_numeric(gmaf, errors='coerce')

####################
####### ET12 #######
####################
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


# Creating a new DataFrame with the additional data points for df4_cleaned
new_data_df4 = pd.DataFrame({
    df4_cleaned.columns[0]: pd.to_datetime(pd.Series(['2024-11', '2024-12']), format="%Y-%m").dt.date,  
    df4_cleaned.columns[1]: [12.447538, 13.405162]
})

# Appending to df4_cleaned
df4_cleaned = pd.concat([df4_cleaned, new_data_df4], ignore_index=True)

#Assigning numeric value to a variable msta for ease of use.
et12 = df4_cleaned.iloc[:,1]
# Convert to numeric (forcing errors='coerce' to handle any non-numeric values)
et12 = pd.to_numeric(et12, errors='coerce')

##############################################################################################################
########### Rewriting Exponential Smoothing Codes to be used as X value in multiple regression model #########
##############################################################################################################
#Data for CH4
fit2 = ExponentialSmoothing(ch4, seasonal_periods=15, trend='add', seasonal='add').fit(smoothing_level = 0.3, smoothing_trend=0.5,  smoothing_seasonal=0.7)

forecast_dates3 = pd.date_range(start="2024-10", periods=15, freq="ME")

# Convert forecast to DataFrame
forecast_df2 = pd.DataFrame({
    "Date": forecast_dates3.strftime("%Y-%m"),
    "Forecasted Value": fit2.forecast(15).values
})

#Data for GMAF
fit3 = ExponentialSmoothing(gmaf, seasonal_periods=24, trend='add', seasonal='add').fit(smoothing_level = 0.3, smoothing_trend=0.5,  smoothing_seasonal=0.7)
forecast_dates4 = pd.date_range(start="2024-01", periods=24, freq="ME")

# Convert forecast to DataFrame
forecast_df3 = pd.DataFrame({
    "Date": forecast_dates4.strftime("%Y-%m"),
    "Forecasted Value": fit3.forecast(24).values
})

#Data for ET12
fit4 = ExponentialSmoothing(et12, seasonal_periods=14, seasonal='add').fit(smoothing_level=0.3, smoothing_seasonal=0.7)
forecast_dates2 = pd.date_range(start="2024-11", periods=14, freq="ME")

# Convert forecast to DataFrame
forecast_df4 = pd.DataFrame({
    "Date": forecast_dates2.strftime("%Y-%m"),
    "Forecasted Value": fit4.forecast(14).values
})


##############################################################
########### Application of Multiple Regression Model #########
##############################################################

df1_cleaned = df1_cleaned.rename(columns={df1_cleaned.columns[0]: "Date"})  # Ensure Date column exists
df2_cleaned = df2_cleaned.rename(columns={df2_cleaned.columns[0]: "Date"})
df3_cleaned = df3_cleaned.rename(columns={df3_cleaned.columns[0]: "Date"})
df4_cleaned = df4_cleaned.rename(columns={df4_cleaned.columns[0]: "Date"})


df_final = df1_cleaned[['Date', df1_cleaned.columns[1]]].merge(
    df2_cleaned, on="Date", how="outer"
).merge(
    df3_cleaned, on="Date", how="outer"
).merge(
    df4_cleaned, on="Date", how="outer"
)


# Rename columns properly
df_final.columns = ['Date', 'MSTA', 'CH4', 'GMAF', 'ET12']


df_final['GMAF'] = pd.to_numeric(df_final['GMAF'], errors='coerce')
df_final['ET12'] = pd.to_numeric(df_final['ET12'], errors='coerce')


# Convert "Date" to datetime format (just in case)
df_final['Date'] = pd.to_datetime(df_final['Date'])
#df_final = df_final.drop(columns=['Date'])

# Building the regression based forecast for main variable, DEOM
# Regression model(s)
formula = 'MSTA ~ CH4 + GMAF + ET12'

# ols generate statistics and the parameters b0, b1, etc., of the model
results = ols(formula, data=df_final).fit(disp=0)
#results.summary()

#Capturing Parameters
b0 = results.params.Intercept
b1 = results.params.CH4
b2 = results.params.GMAF
b3 = results.params.ET12

#Printing out the Parameters
print("Intercept (b0):", b0)
print("CH4 Coefficient (b1):", b1)
print("GMAF Coefficient (b2):", b2)
print("ET12 Coefficient (b3):", b3)

# R-squared and p-values
print("R-squared:", results.rsquared)
print("P-values:", results.pvalues)


# Create a DataFrame for future predictions
future_dates = pd.date_range(start=df_final['Date'].max() + pd.DateOffset(months=1), periods=12, freq='MS')

# Create future DataFrame (assuming CH4, GMAF, ET12 are known or estimated)
future_df = pd.DataFrame({
    'Date': future_dates,
    'CH4': forecast_df2.iloc[-12:, 1].values,  
    'GMAF': forecast_df3.iloc[-12:, 1].values,
    'ET12': forecast_df4.iloc[-12:, 1].values
})

# Convert to numeric types (just in case)
future_df['CH4'] = pd.to_numeric(future_df['CH4'], errors='coerce')
future_df['GMAF'] = pd.to_numeric(future_df['GMAF'], errors='coerce')
future_df['ET12'] = pd.to_numeric(future_df['ET12'], errors='coerce')

# Predict MSTA using the regression model
future_df['Predicted_MSTA'] = results.predict(future_df)

# Display the future predictions
#print(future_df[['Date', 'Predicted_MSTA']]

# Combine actual and predicted data
df_combined = pd.concat([
    df1_cleaned[['Date', df1_cleaned.columns[1]]],  # Use correct column name
    future_df[['Date', 'Predicted_MSTA']]
], ignore_index=True)




# Plot the actual vs predicted MSTA values
plt.figure(figsize=(10, 5))

# Plot actual data
plt.plot(df1_cleaned["Date"], df1_cleaned.iloc[:, 1], color='black', label='Actual MSTA Data')

# Plot predicted data
plt.plot(future_df["Date"], future_df["Predicted_MSTA"], color='red', label='Predicted MSTA')

# Step 5: Formatting the plot
plt.xlabel('Date')
plt.ylabel('MSTA')
plt.title('MSTA Forecast')
plt.legend()
plt.xticks(rotation=45)
plt.grid(True)

# Show plot
plt.show()


# Compute correlation matrix
corr_matrix = df_final[['MSTA', 'CH4', 'GMAF', 'ET12']].corr()

# Plot heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
plt.title("Correlation Matrix")
plt.show()




# Perform an F-test to check overall model significance
f_stat = results.fvalue  # F-statistic
f_p_value = results.f_pvalue  # p-value for the F-test

print("F-statistic:", f_stat)
print("F-test p-value:", f_p_value)
