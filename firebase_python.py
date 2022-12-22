
import firebase_admin
from firebase_admin import credentials, db,firestore
import datetime



cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
firestore_client = firestore.client()

today_day = datetime.date.today()
days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
print("Today weekday is ",days[today_day.weekday()])

# To create a collection with documents in the database
doc_ref = firestore_client.collection("Attandance").document(f"{days[today_day.weekday()]}")
doc = doc_ref.get()
print(f"{doc.id} => {doc.to_dict()}")

sub_coll = doc_ref.collection("Students")
sub_coll.document("210226").set({
    "Name": "Aayush Pandey",
    "Age": 20,
    "Address": "Biratnagar",
    "Time" : firestore.SERVER_TIMESTAMP,
    "Attendance" : "Present"
})


# #  To get all the documents in the collection
# doc_ref = firestore_client.collection("Students")
# a = doc_ref.stream()
# for i in a:
#     print(f"{i.id} => {i.to_dict()}")

# # To get a specific document in the collection
# doc_ref = firestore_client.collection("Students").document("210226")
# doc = doc_ref.get()
# print(f"{doc.id} => {doc.to_dict()}")

# # To get a specific field in the document
# doc_ref = firestore_client.collection("Students").document("210226")
# doc = doc_ref.get()
# print(f"{doc.id} => {doc.to_dict()['Name']}")



# # To update a document in the database
# doc_ref = firestore_client.collection("Students").document("210226")
# doc_ref.update({
#     "Name": "John",
#     "Age": 20,
#     "Address": "New York"
# })

# # To delete a document in the database
# doc_ref = firestore_client.collection("Students").document("210226")
# doc_ref.delete()

# # to create a document in the database
# doc_ref = firestore_client.collection("Students").document("210226")
# doc_ref.set({
#     "Name": "Aayush Pandey"})


# #To delete a collection in the database
# # doc_ref = firestore_client.collection("Students")
# # docs = doc_ref.stream()
# # for doc in docs:
# #     doc.reference.delete()

# # to delete a field in the database
# doc_ref = firestore_client.collection("Students").document("210226")
# doc_ref.update({
#     "Name": firestore.DELETE_FIELD
# })

