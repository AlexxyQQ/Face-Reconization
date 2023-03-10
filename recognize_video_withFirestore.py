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
import firebase_admin
from firebase_admin import credentials, db,firestore
import datetime


# Firebase initialization

cred = credentials.Certificate("Others/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
firestore_client = firestore.client()
# Day of the week

date = datetime.datetime.now()
att_date =f"{date.year}-{date.month}-{date.day}"

# load serialized face detector
print("Loading Face Detector...")
protoPath = "face_detection_model/deploy.prototxt"
modelPath = "face_detection_model/res10_300x300_ssd_iter_140000.caffemodel"
detector = cv2.dnn.readNetFromCaffe(protoPath, modelPath)

# load serialized face embedding model
print("Loading Face Recognizer...")
embedder = cv2.dnn.readNetFromTorch("Others/openface_nn4.small2.v1.t7")

# load the actual face recognition model along with the label encoder
recognizer = pickle.loads(open("output/recognizer", "rb").read())
le = pickle.loads(open("output/le.pickle", "rb").read())

# initialize the video stream, then allow the camera sensor to warm up
print("Starting Video Stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)

# start the FPS throughput estimator
fps = FPS().start()



students_names = [
	"Aayush",
	"Bishwash",
]


present = []
#

def firebase_set_studets():
	for student in students_names:
		if student == "Aayush":
			doc_ref = firestore_client.collection("Attandance").document(f"{att_date}").collection("Students").document("210226")
			doc_ref.set({
				"Name" : student,
				"Attendance" : "",
			})
		else:
			doc_ref = firestore_client.collection("Attandance").document(f"{att_date}").collection("Students").document("210227")
			doc_ref.set({
					"Name" : student,
					"Attendance" : "",
				})
firebase_set_studets()
def firebase_get_present():
	col_ref = firestore_client.collection("Attandance").document(f"{att_date}").collection("Students")
	query_ref = col_ref.where("Attendance", "==", "Present").stream()
	for doc in query_ref:
		if doc.to_dict()["Name"] not in present:
			present.append(doc.to_dict()["Name"])
	return present
firebase_get_present()

def firebase_store(st_id):
	doc_ref = firestore_client.collection("Attandance").document(f"{att_date}").collection("Students").document(f"{st_id}")

	doc_ref.update({
		"Attendance" : "Present",
		"TIME" : firestore.SERVER_TIMESTAMP
	})

def firebase_get(name):
	st_id = ""
	col_ref = firestore_client.collection("Attandance").document(f"{att_date}").collection("Students")
	query_ref = col_ref.where("Name", "==", name).stream()
	for doc in query_ref:
		st_id = doc.id
	return st_id











# loop over frames from the video file stream
while True:
	if len(present) < 2:
	
		firebase_get_present()
	# grab the frame from the threaded video stream
	frame = vs.read()

	# resize the frame to have a width of 600 pixels (while maintaining the aspect ratio), and then grab the image dimensions
	frame = imutils.resize(frame, width=1200)
	(h, w) = frame.shape[:2]

	# construct a blob from the image
	imageBlob = cv2.dnn.blobFromImage(
		cv2.resize(frame, (300, 300)), 1.0, (300, 300), 
		(104.0, 177.0, 123.0), swapRB=False, crop=False)

	# apply OpenCV's deep learning-based face detector to localize faces in the input image
	detector.setInput(imageBlob)
	detections = detector.forward()

	# loop over the detections
	for i in range(0, detections.shape[2]):
		# extract the confidence (i.e., probability) associated with the prediction
		confidence = detections[0, 0, i, 2]
		# filter out weak detections
		if confidence > 0.95:
			# compute the (x, y)-coordinates of the bounding box for the face
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")

			# extract the face ROI
			face = frame[startY:endY, startX:endX]
			(fH, fW) = face.shape[:2]

			# ensure the face width and height are sufficiently large
			if fW < 20 or fH < 20:
				continue

			# construct a blob for the face ROI, then pass the blob through our face embedding model to obtain the 128-d quantification of the face
			faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255,(96, 96), (0, 0, 0), swapRB=True, crop=False)
			embedder.setInput(faceBlob)
			vec = embedder.forward()

			# perform classification to recognize the face
			preds = recognizer.predict_proba(vec)[0]
			j = np.argmax(preds)
			proba = preds[j]
			name = le.classes_[j]
			if proba < 0.3:
				continue 
			# draw the bounding box of the face along with the associated probability
			text = "{}".format(name)
			
				
			y = startY - 10 if startY - 10 > 10 else startY + 10

			if text != "Unknown":
				if name in students_names:
					if name not in present:
						firebase_store(firebase_get(name))
				
			cv2.rectangle(frame, (startX, startY), (endX, endY),
				(255, 0, 0), 2)
			cv2.putText(frame, text, (startX, y),
				cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

	# update the FPS counter
	fps.update()

	# show the output frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

# stop the timer and display FPS information
fps.stop()
print("Elasped time: {:.2f}".format(fps.elapsed()))
print("Approx. FPS: {:.2f}".format(fps.fps()))

# cleanup
cv2.destroyAllWindows()
vs.stop()