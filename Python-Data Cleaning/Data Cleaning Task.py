# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 11:36:14 2025
 
This code is a data cleaning case study.

@author: Engin-Eer
"""

#

    
import pandas as pd
import os
from datetime import datetime

#Defining a path for the folder
path = "C://Users//Engin-Eer//OneDrive - University of Southampton//Python//Project 3_Data Cleaning//"


#Getting all file names in a folder
#Filtering filenames with xlsx
files = [i for i in os.listdir(path) if i.endswith((".xlsx",".xsl"))]


# loop through and create separate variables
for f in files:
    temp = f.split(".")[0]  # remove .xlsx
    globals()[temp] = pd.read_excel(path + f)
del(temp,f,files,path)

#Cleaning file1:Employee_Master
#print(Employee_Master)

for i in range(0,len(Employee_Master)): #for each row,
    #EmpID column:    
    #Fixing missing "E" at the beginning:    
    if not pd.isna(Employee_Master.loc[i,"EmpID"]):
        if Employee_Master.loc[i,"EmpID"][0] != "E":
            Employee_Master.loc[i,"EmpID"] = ("E"  + Employee_Master.loc[i,"EmpID"])
        #Fixing missing "0":
        if len(Employee_Master.loc[i,"EmpID"]) != 4:
            Employee_Master.loc[i,"EmpID"] = Employee_Master.loc[i,"EmpID"].replace("0","00") 
    if pd.isna(Employee_Master.loc[i, "EmpID"]): #Clearing NaN values: #Note although this is a practice case study, primary key column don't normally have anomalies. Assuming its value as +1 of previous one is not something i'd normally do, as it can be just poor sql join while merging queries.
        #grab the number before, if it is not also not null, add  1, create new the new id
        if not pd.isna(Employee_Master.loc[i-1,"EmpID"]):
            temp = Employee_Master.loc[i-1,"EmpID"]
            newTempId = int(temp[len(temp)-1]) +1
            if newTempId < 10:
                Employee_Master.loc[i,"EmpID"] = "E00" + str(newTempId)
            else:
                Employee_Master.loc[i,"EmpID"] = "E0" + str(newTempId)
        #Note: By the way EmpId has created, it is not expected to exceed 999. In such case, syntax for the whole column needs updating. 
        Employee_Master.loc[i,"FullName"] = Employee_Master.loc[i,"FullName"].title()
    
    #FullName column:
    if not pd.isna(Employee_Master.loc[i,"FullName"]): #leaving NaN as it is 
        Employee_Master.loc[i,"FullName"] = str(Employee_Master.loc[i,"FullName"]).strip() #Strip removes spaces from before&after text
        Employee_Master.loc[i,"FullName"] = Employee_Master.loc[i,"FullName"].title() #Setting Capital Letters to Initials of Each Word
    
    
    #Dept column:
    if not pd.isna(Employee_Master.loc[i,"Dept"]): #leaving NaN as it is 
        if Employee_Master.loc[i,"Dept"] == "acctg":
            Employee_Master.loc[i,"Dept"] = "Accounting"
        elif Employee_Master.loc[i,"Dept"] == "HR":
            Employee_Master.loc[i,"Dept"] = "Human Resources"
        elif Employee_Master.loc[i,"Dept"] == "Fin":
            Employee_Master.loc[i,"Dept"] = "Finance"            
        Employee_Master.loc[i,"Dept"] = Employee_Master.loc[i,"Dept"].title()
        
        
    #Date column:
    if not pd.isna(Employee_Master.loc[i,"StartDate"]): #leaving NaN as it is
        Employee_Master["StartDate"] = Employee_Master["StartDate"].str.replace(r"[\/ ]", "-", regex=True)
        Employee_Master["StartDate"] = Employee_Master["StartDate"].str.replace("Mar","03") # and so on for each 12
        Employee_Master["StartDate"] = Employee_Master["StartDate"].str.replace("-5-","-05-") # and so on  for each 12
        # if not Employee_Master.loc[i,"StartDate"][4] == "-":
        try:
            new_date = datetime.strptime(Employee_Master.loc[i, "StartDate"], "%d-%m-%Y").strftime("%Y-%m-%d")
            Employee_Master.loc[i, "StartDate"] = new_date
        except ValueError:
            continue
        
    #Status column:
    
for q in Employee_Master.index:
    val = str(Employee_Master.loc[q, "Status"]).lower()  # ensure string. #Note: This sets na values as 0, and it is logically accepted.
    if "n" in val:
        Employee_Master.loc[q, "Status"] = 0
    else:
        Employee_Master.loc[q, "Status"] = 1


#Feedback: I have used vectorized operations within a row operation many times, making  my code inefficient from scratch. Using a for loop for each column is not python-friendly, and I shall use more vectors in the future.
#What I learned:
    #You can use .split(" ") to seperate a cell using space as delimiter. a,b = x.split(" ") assigns "A B" to a and b.
    #You can do "from datetime import datetime" and use newDate = datetime.strptime(yourDateColumn, "%d-"m-"Y").strftime("%Y-%m-%d") to replace dmY to Ymd
    #.title convers "abc def" to "Abc Def", capitalizing initials of each word.
    #You can replace multiple items using regex, though it is not na friendly by
        #Column = Column.astype(str).str.replace(r"[\/ ]", "-", regex=True)
    #You can do "import os" and use globals to generate series of objects.
        #Do to import certain files into an object with:
            #files = [i for i in os.listdir(path) if i.endswith((".xlsx",".xsl"))]
        #as use a for loop s.t.:
            # for f in files:
                # temp = f.split(".")[0]  # remove .xlsx
                # globals()[temp] = pd.read_excel(path + f)    
del(temp,val,q,i,new_date,newTempId)

# #Cleaning file3:Timesheet_Q1

#Cleaning the Status column
mask = ~Timesheet_Q1["EmpID"].astype(str).str.startswith("E")
Timesheet_Q1.loc[mask, "EmpID"] = "E" + Timesheet_Q1.loc[mask, "EmpID"].astype(str)

#Cleaning the Date column
#replacing delimiters with dash
Timesheet_Q1["Date"] = Timesheet_Q1["Date"].astype(str).str.replace(r"[/\ .]", "-", regex=True)
#formatting date column anomalies with Y%-m%-d% format
from datetime import datetime
mask = Timesheet_Q1["Date"].astype(str).str[5] == ("-")
Timesheet_Q1.loc[mask, "Date"] = pd.to_datetime(Timesheet_Q1.loc[mask,"Date"], format="%d-%m-%Y",errors="coerce").dt.strftime("%Y-%m-%d")

#Cleaning Timesheet_Q1["HoursWorked"] column
mask2 = []
for i in range(len(Timesheet_Q1["HoursWorked"])):
    try:
        Timesheet_Q1.loc[i,"HoursWorked"] = int(Timesheet_Q1.loc[i,"HoursWorked"])
    except ValueError:
        mask2.append(Timesheet_Q1.loc[i,"HoursWorked"])

#print(mask2)
#This provides a list of anomalies; values that cannot be transformed into integer. From here, considering the sample size, and number of unique anomalies, a unique dim table can be generated to manually interfere.
Timesheet_Q1["HoursWorked"] = Timesheet_Q1["HoursWorked"].replace(mask2, [7.5,9]).infer_objects(copy=False)

#Cleaning Timesheet_Q1["ProjectCode"] column

Timesheet_Q1["ProjectCode"] = Timesheet_Q1["ProjectCode"].str.upper()

#Feedback: I have used vectorized where possibe. Due to the way I learn algorithm, I am naturally tend to use loops within loops, tho forcing myself to use vectorized, although slow and hard to debug, shows how powerful python is.
#Another learning outcome is that I forget faster than I learn, so I gotta integrate this coding exercise in my daily activities.


# #Cleaning file2:Project_Info
#print(Project_Info)
#Project_Info.columns.tolist()

#Budget and ActiveFlag cols need operation.

#removing currency units from the Budget.
Project_Info["Budget"] = Project_Info["Budget"].str.replace(r"[$£€]","",regex=True)
print(Project_Info["Budget"])

#clefaning Active Flag by mapping

AFmapping = {
    "Y":True,
    "Yes":True,
    "true":True,
    "FALSE":False}

Project_Info["ActiveFlag"] = Project_Info["ActiveFlag"].map(AFmapping)