# -*- coding: utf-8 -*-
"""
Created on Mon May 26 13:17:05 2025

@author: Engin-Eer
---

must be placed somewhere; if not, create a list of non-assigned applicants to be notified.
must be placed according to their preferences. If no solution exist, create a list to be clarified with applicants.
must be placed in preferred room type as a priority.

should be placed as best as possible according to their preference list.
should be placed next to same nationality, where possible.
should be placed in Single rooms with priority if a Master's student.

Be careful to ensure an equal nationality distribution among halls to promote diversity.
---
"""
###################################
###################################
##Steps
###################################
###################################


###################################
##0)Imports
#Class Imports
import pandas as pd
#file imports
path = "C:/Users/Engin-Eer/Desktop/Python/Project 1/"
students = pd.read_excel(path + "student_2_halls_assignment_data.xlsx", sheet_name= "Sheet1", header=0, dtype = {"StudentId": str})
halls    = pd.read_excel(path + "student_2_halls_assignment_data.xlsx", sheet_name= "Sheet2", header=0)
#Cleaning unnecessary environment items.
del(path)
###################################
students = students.sample(frac=1).reset_index(drop=True)
###################################
##1)Data Cleaning
#Clean Nationalities to remove duplications; UK,Great Britain, Turkey,Türkiye, etc.
distinctCountries = pd.DataFrame(students.Nationality.unique(),columns= ["Nat"]) #Creating a distinct list
#duplicating column to create a VlookUp Table
distinctCountries["Nat2"] = distinctCountries["Nat"]
distinctCountries["Nat2"] = distinctCountries["Nat2"].replace({"British":"UK","Türkiye":"Turkey","American":"USA","Irish":"UK","Great Britain":"UK","U.S":"USA"})
#Cleaning columns that are identical to run a counter accurately
for i in range(len(distinctCountries)):
    if distinctCountries.loc[i,"Nat"] == distinctCountries.loc[i,"Nat2"]:
        distinctCountries = distinctCountries.drop(i)
distinctCountries = distinctCountries.reset_index(drop=True)
del(i)


#VlookUp operation in students table
counter = 0
numchange=0
while counter < len(students):
    for i in range(len(distinctCountries)):
        if students.loc[counter,"Nationality"] == distinctCountries.loc[i,"Nat"]:
            students.loc[counter,"Nationality"] = distinctCountries.loc[i,"Nat2"]
            numchange += 1
    counter += 1


#print(str(numchange) + " changes are made to cleanse redundant Nationalities in Students Table.")
del(counter,numchange,i)
#Updating students table to change from "Halls A", to "A".
students["Preference1"] = students["Preference1"].str.replace("Halls " , "")
students["Preference2"] = students["Preference2"].str.replace("Halls " , "")
students["Preference3"] = students["Preference3"].str.replace("Halls " , "")

del(distinctCountries)
###################################

###################################
#2)Data Quality Check & General Controls
#Check if total capacity is enough for all applicants.
#if len(students) - sum(halls.Capacity) > 0:
    #print(str(len(students) - sum(halls.Capacity)) + " people can not be placed due to lack of capacity.")
    
#Count single & Doubles to see if a feasible assignment is possible.
 
ApplicationsSummary = {
    "Single" : [(students["RoomPreference"] == "Single").sum(),halls.loc[halls["RoomType"]=="Single","Capacity"].sum()],
    "Double" : [(students["RoomPreference"] == "Double").sum(),halls.loc[halls["RoomType"] == "Double","Capacity"].sum()]
    }
#Applications
#Halls Capacity
ApplicationsSummary = pd.DataFrame(ApplicationsSummary, index = ["Applications","Halls Capacity"])
#print("---")
#print(ApplicationsSummary)
#print("Status Report: Out of 226 Applications who have chosen `Double`, 19 of them will be placed to Single Rooms, 3 will be eliminated. All 22 Applicants shall be notified to see if they are willing to pay the extra fee for `Single` room upgrade.")


#Create a more detailed summary table showing the decomposition for halls buildings.

#A perfect case scenario where everyone wants where they want to be placed.
students["BestCaseScenario"] = students["Preference1"] + "_" + students["RoomPreference"]
halls["BestCaseScenario"] = halls["Halls"] + "_" + halls["RoomType"]

StudentsSummary1 = students.groupby("BestCaseScenario")["BestCaseScenario"].agg("count")
StudentsSummary1 = pd.DataFrame(StudentsSummary1)
StudentsSummary1 = (StudentsSummary1.rename(columns={"BestCaseScenario":"ApplicationsBest"}))

HallsSummary1 = pd.DataFrame(halls["Capacity"].values, index=halls["BestCaseScenario"], columns=["Capacity"])

BestCaseScenario = pd.concat([HallsSummary1, StudentsSummary1], axis=1)
#print("---")
#print(BestCaseScenario)
#print("Status Report: After seeing the detailed table, I can guarantee that there will be many disputes, and arrangements.")
del(HallsSummary1,StudentsSummary1)

#Generate ModerateCaseScenario
students["ModerateCaseScenario"] = students["Preference2"] + "_" + students["RoomPreference"]
halls = (halls.rename(columns={"BestCaseScenario":"ModerateCaseScenario"}))


StudentsSummary2 = students.groupby("ModerateCaseScenario")["ModerateCaseScenario"].agg("count")
StudentsSummary2 = pd.DataFrame(StudentsSummary2)
StudentsSummary2 = (StudentsSummary2.rename(columns={"ModerateCaseScenario":"ApplicationsModerate"}))

HallsSummary2 = pd.DataFrame(halls["Capacity"].values, index=halls["ModerateCaseScenario"], columns=["Capacity"])

ModerateCaseScenario = pd.concat([HallsSummary2, StudentsSummary2], axis=1)
del(HallsSummary2,StudentsSummary2)
#Generate WorseCaseScenario
students["WorseCaseScenario"] = students["Preference3"] + "_" + students["RoomPreference"]
halls = (halls.rename(columns={"ModerateCaseScenario":"WorseCaseScenario"}))
StudentsSummary3 = students.groupby("WorseCaseScenario")["WorseCaseScenario"].agg("count")
StudentsSummary3 = pd.DataFrame(StudentsSummary3)
StudentsSummary3 = (StudentsSummary3.rename(columns={"WorseCaseScenario":"ApplicationsWorse"}))

HallsSummary3 = pd.DataFrame(halls["Capacity"].values, index=halls["WorseCaseScenario"], columns=["Capacity"])

WorseCaseScenario = pd.concat([HallsSummary3, StudentsSummary3], axis=1)
del(HallsSummary3,StudentsSummary3)
###################################
#3)The algorithm

#Generate an assignment list to be filled by multiplying halls table.
assignment = halls
assignment = assignment.drop(columns=["WorseCaseScenario","isSoundProof","Capacity"])
RoomNumA = 1000
RoomNumB = 1000
RoomNumC = 1000
RoomNumD = 1000
RoomNumE = 1000
RoomNumF = 1000
rowCountt = 0
assignment["RoomId"] = 0
sayac = 0
for i in range(len(assignment)):
    if assignment.loc[0,"RoomId"] == 0:
        if assignment.loc[0,"RoomType"] == "Single":
            rowCountt = assignment.loc[0,"RoomCount"] 
        else:
            rowCountt = assignment.loc[0,"RoomCount"] * 2    
        j=0
        rows_to_duplicate = assignment.iloc[[0]]
        while j < rowCountt:
            # Duplicate rows based on 'RoomCount' column
            assignment = pd.concat([assignment, rows_to_duplicate], ignore_index=True)
            if rows_to_duplicate.loc[0,"Halls"] == "A":
                assignment.loc[len(assignment)-1,"RoomId"] = RoomNumA
                RoomNumA += 1
            elif rows_to_duplicate.loc[0,"Halls"] == "B":
                assignment.loc[len(assignment)-1,"RoomId"] = RoomNumB
                RoomNumB += 1
            elif rows_to_duplicate.loc[0,"Halls"] == "C":
                assignment.loc[len(assignment)-1,"RoomId"] = RoomNumC
                RoomNumC += 1
            elif rows_to_duplicate.loc[0,"Halls"] == "D":
                assignment.loc[len(assignment)-1,"RoomId"] = RoomNumD
                RoomNumD += 1
            elif rows_to_duplicate.loc[0,"Halls"] == "E":
                assignment.loc[len(assignment)-1,"RoomId"] = RoomNumE
                RoomNumE += 1
            elif rows_to_duplicate.loc[0,"Halls"] == "F":
                assignment.loc[len(assignment)-1,"RoomId"] = RoomNumF
                RoomNumF += 1
            j +=1
        assignment = assignment.drop(assignment.index[0]).reset_index(drop=True)

del(i,sayac,RoomNumA,RoomNumB,RoomNumC,RoomNumD,RoomNumE,RoomNumF,rowCountt,j,rows_to_duplicate)
assignment = assignment.drop(columns=["RoomCount"])

#Do the assignment as iterations, from BestCase to Moderate, to Worse.
assignment["StudentId"] = '0'






##BestCaseScenario Assignment

#Creating Unique id
assignment["Type"] = assignment["Halls"] + "_" + assignment["RoomType"]
#Setting default quantity
BestCaseScenario["QuantityToBeAssigned"] = 0
#Creating new column to decide how many quantitiy to assign.
for i in range(len(BestCaseScenario)):
    i = BestCaseScenario.index[i]
    if BestCaseScenario.loc[i,"ApplicationsBest"] > BestCaseScenario.loc[i,"Capacity"]:
        BestCaseScenario.loc[i,"QuantityToBeAssigned"] = BestCaseScenario.loc[i,"Capacity"]
    else:
        BestCaseScenario.loc[i,"QuantityToBeAssigned"] = BestCaseScenario.loc[i,"ApplicationsBest"]
del(i)

for i in range(len(BestCaseScenario)):
    i = BestCaseScenario.index[i]
    getType = i
    getQ    = BestCaseScenario.loc[getType, "QuantityToBeAssigned"]
    #Take a save of students table, #Filter the new students table's BestCaseScenario column with getType
    students_wb = students[students["BestCaseScenario"] == getType].reset_index(drop=True)
    #students_wb = students_wb.sample(frac=1).reset_index()
    if not BestCaseScenario.loc[i, "QuantityToBeAssigned"]  == 0:
        #select randomly getQ amount of students, reduce the list to getQ quantity.
        if len(students_wb) == getQ or len(students_wb) > getQ:
            for j in range(getQ):
                assignment.loc[assignment[assignment["Type"] == getType].index[j], "StudentId"] = students_wb.iloc[j]["StudentId"]
                
                    
del (i,j,getType,getQ,students_wb)
remainingQ = len(assignment[assignment["StudentId"]== '0'])
#print("Out of " + str(len(assignment)) + " capacity, " + str(len(assignment)-remainingQ) + " people are placed according to their First Preference. " + str(remainingQ) + " applications remains to be placed.")
del (remainingQ)

#Assign According to Moderate Case for those who's studentId = '0' in assignment table.
#Create a list of remaining students still waiting to be assigned.
students_wb = students[~students["StudentId"].isin(assignment["StudentId"])].reset_index(drop=True)
#randomly mix students_wb
#students_wb = students_wb.sample(frac=1).reset_index(drop=True)
students_wb["isAssigned"] = 0
#if assignment's StudentId = 0 and Type = student_wb's ModerateCaseScenario, copy Id to assignment.
for i in range(len(assignment)):
    if assignment.loc[i,"StudentId"] == '0':
        for j in range(len(students_wb)):
            if students_wb.loc[j,"ModerateCaseScenario"] == assignment.loc[i,"Type"] and students_wb.loc[j, "isAssigned"] == 0:
                assignment.loc[i,"StudentId"] = students_wb.loc[j,"StudentId"]
                students_wb.loc[j, "isAssigned"] = 1
                break

del(i,j)
remaining_students = students_wb[students_wb["isAssigned"] == 0]

#Add 3 new columns to students to detect which one is assigned at what step.
students["isBest"] = 0
students["isModerate"] = 0
students["isWorse"] = 0

#To add ones assigned from 2nd preference 
for i in range(len(students)):
    for j in range(len(students_wb)):
        if students_wb.loc[j,"isAssigned"] == 1 and students.loc[i,"StudentId"] == students_wb.loc[j,"StudentId"]:
            students.loc[i,"isModerate"] = 1

#write a code to turn students.isBest = 1 for students.studentId if that students.studentId is not in students_wb.studentId        
students["isBest"] = (~students["StudentId"].isin(students_wb["StudentId"])).astype(int)

#Add a new column isAssigned that will turn 0 only if all cases are 0. 1 o.w.
students["isAssigned"] = ((students['isBest'] == 1) | (students['isModerate'] == 1) | (students['isWorse'] == 1)).astype(int)
#YOU ARE HERE!

#Cleaning unnecessary environment items
del(i,j,remaining_students,students_wb)
#non-assigned 71 rooms: assignment[assignment["StudentId"] == '0']
assignment_wb = assignment[assignment["StudentId"] == "0"]
#remove type column
#assignment_wb = assignment_wb.drop(columns=["Type"])

postassignmentSummary = assignment_wb.groupby(("Type"))["StudentId"].agg("count")
#non-assigned 74 students: students[students["isAssigned"] == 0]
remainingStudents = students[students["isAssigned"] == 0][["StudentId", 'RoomPreference',
 'BestCaseScenario',
 'ModerateCaseScenario',
 'WorseCaseScenario']].copy()

remainingStudentsSummary = remainingStudents.groupby(("WorseCaseScenario"))["StudentId"].agg("count")

#print("According to 3rd preferences: 8 students can be placed to B single, 5 students can be placed to D single, 2 to E double, 24 to F double. After the assignment, 36 students shall remain to be placed.")
del(remainingStudentsSummary,postassignmentSummary)

for i in range(len(assignment)):
    if assignment.loc[i,"StudentId"] == '0':
        for j in range(len(students)):    
            if assignment.loc[i,"Type"] == students.loc[j,"WorseCaseScenario"] and students.loc[j,"isAssigned"] == 0:
                assignment.loc[i,"StudentId"] = students.loc[j,"StudentId"] 
                students.loc[j,"isAssigned"] = 1
                students.loc[j,"isWorse"] = 1
                break





temp = students[students["isAssigned"] == 0].groupby("isAssigned")["isAssigned"].agg("count")
print (temp.sum())



#4)Data Quality Tests to be Applied:
#Check if a studentId is shown +1 tems in assignment table
#Check if StudentId to room assignment is accurate.
#Check if RoomType assigment ('must' rule) is violated.
#Check if nationalities are equallity distributed among halls.
#Check if same nationalities are actually placed in same double rooms.

#v0_CreatedOn_Mon May 26 13:17:05 2025_author_Engin-Eer_Siggned and OFF!