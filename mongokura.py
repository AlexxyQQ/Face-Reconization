# import libraries
import os
import cv2
import imutils
import time
import pickle,re
import numpy as np
from imutils.video import FPS
from imutils.video import VideoStream
import copyreg as copy_reg 
import datetime
from pymongo import MongoClient
from random import randint

# MongoDB initialization


# Connect to the database
client = MongoClient(
    "mongodb+srv://alexxy:test@cluster0.qiqirmp.mongodb.net/softwarica?retryWrites=true&w=majority")
db = client["softwarica"]
 

# Day of the week

date = str(datetime.datetime.today())[0:10]
 
print(date)
present = []

def get_students(L_cid):
    col = db.get_collection("students")
    filter =  {"classes": {"$in":L_cid}} 
    r = list(col.find(filter)) 
    return r
    
def fetch_student_info(SID):
    col = db.get_collection("students") 
    filter = {"name" : SID}
    r = list(col.find(filter))
    return r

 
def new_day():
    today = "2023-02-22"
    # check time
    if(str(datetime.datetime.today()) [0:10]!= today):
        col = db.get_collection("students")  
        today = str(datetime.datetime.today()) [0:10] 
        filter = { } 
        update = {"$set":{f"{date}":{"datetime":today,"attendance": "Absent" }  }} 
        col.update_many(filter, update)
    #starts a day and absents all students

 


def is_present(SID, CID, date):
    col = db.get_collection("students") 
    filter = {"name" : SID, "classes" : {"$in":CID} }
    r = list(col.find(filter))
    ras = r[0] 
    try:
        if(ras[date]['attendance']== "Present" ):
            return True
        else:
            return False    
    except:
        return False     
 
#print(is_present("Student 72",["STA103IAE"],"2023-02-17"))
# fetch_student_info("Student 0")
# print(get_students(["STA103IAE"]))     





def attendance(SID, CID ):
    date = str(datetime.datetime.today())[0:10]
    current_time = str(datetime.datetime.now())[11:19] 
    current_time = "10:10:10" 
    date_time = str(datetime.datetime.today())
    
    col = db.get_collection("students") 
    filter = {"name" : SID, "classes" : {"$in":[CID]} }

    r = list(col.find(filter))
    class_date= list(db.get_collection("classes").find({"cid":CID}))[0]["date"]
    class_time= list(db.get_collection("classes").find({"cid":CID}))[0]["time"]
    start_class_time = class_time["start"]
    end_class_time = class_time["end"]  
    start_time_24 = datetime.datetime.strptime(start_class_time, "%I:%M %p").strftime("%H:%M")
    end_time_24 = datetime.datetime.strptime(end_class_time, "%I:%M %p").strftime("%H:%M")
 
    # Check if given time falls within start and end time
    if start_time_24 <= current_time <= end_time_24: 
        update = {"$set":{f"{date}":{"datetime":date_time,"attendance": "Present","cid":CID}  }} 
        col.update_one(filter,update) 
    else:
        print("Given time does not fall within start and end time.")
        pass
    #if current time falls inside class time then do the attendance
    
        #update the student document to mark present {dateandtime, attendance , cid }
    #else mark the student as absent
#attendance("Student 72", "STA103IAE" )
 