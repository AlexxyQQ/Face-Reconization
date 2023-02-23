from pymongo import MongoClient
from random import randint

# Connect to the database
client = MongoClient(
    "mongodb+srv://alexxy:test@cluster0.qiqirmp.mongodb.net/softwarica?retryWrites=true&w=majority")
db = client["softwarica"]

# Define the classes
classes = [
    {
        "name": "Creative Thinking For Business",
        "cid": "STA103IAE",
        "lecturer": "Arun Phuyal",
        "weeks": 13,
        "lessons": 77,
        "type": "Lecture",
        "cancelled": False,
        "place": "LR-8",
        "year": 1,
        "time": {"start": "9:00 AM", "end": "11:00 AM"},
        "date": "2023-02-17"
    },
    {
        "name": "Be Your Own Boss",
        "cid": "STA201IAE",
        "lecturer": "Samip Pandey",
        "weeks": 13,
        "lessons": 15,
        "type": "Lecture",
        "cancelled": False,
        "place": "LR-12",
        "year": 2,
        "time": {"start": "9:00 AM", "end": "11:00 AM"},
        "date": "2023-02-17"
    },
    {
        "name": "People And Computing",
        "cid": "ST5006CEM",
        "lecturer": "Manish Khanal",
        "weeks": 14,
        "lessons": 55,
        "type": "Lecture",
        "cancelled": False,
        "place": "LR-14",
        "year": 2,
        "time": {"start": "7:00 AM", "end": "8:00 AM"},
        "date": "2023-02-18"
    },
    {
        "name": "Enterprise Project",
        "cid": "ST5010CEM",
        "lecturer": "Shrawan Thakur",
        "weeks": 11,
        "lessons": 9,
        "type": "Lecture",
        "cancelled": False,
        "place": "LR-12",
        "year": 2,
        "time": {"start": "7:00 AM", "end": "9:00 AM"},
        "date": "2023-02-20"
    },
    {
        "name": "Data Science For Developers",
        "cid": "ST5014CEM",
        "lecturer": "Siddhartha Neupane",
        "weeks": 13,
        "lessons": 30,
        "type": "Lecture",
        "cancelled": False,
        "place": "LR-14",
        "year": 2,
        "time": {"start": "8:00 AM", "end": "9:00 AM"},
        "date": "2023-02-16"
    }
]

# Insert the classes into the 'classes' collection
db["classes"].insert_many(classes)

# Define the students
students = []
for i in range(80):
    age = randint(18, 30)
    cc = randint(0, 2)
    counts = randint(1, 5)
    class_ids = []
    if cc == 0:
        # randomly select up to 3 classes for each student
        for j in range(counts):
            class_index = randint(0, len(classes) - 1)
            class_id = classes[class_index]["cid"]
            class_ids.append(class_id)
    student = {
        "name": "Student " + str(i),
        "age": age,
        "classes": class_ids
    }
    students.append(student)

# Insert the students into the 'students' collection
db["students"].insert_many(students)
