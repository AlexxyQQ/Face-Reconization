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
from flask import Flask, render_template, Response

app = Flask(__name__)


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
vs = cv2.VideoCapture(0)


def gen_frames():

	# loop over frames from the video file stream
	while True:
		
		# grab the frame from the threaded video stream
		success,frame = vs.read()
		if not success:
			break
		else:
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

				
						
					cv2.rectangle(frame, (startX, startY), (endX, endY),
						(255, 0, 0), 2)
					cv2.putText(frame, text, (startX, y),
						cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

			# update the FPS counter

			# show the output frame
			# cv2.imshow("Frame", frame)
			key = cv2.waitKey(1) & 0xFF

			# if the `q` key was pressed, break from the loop
			if key == ord("q"):
				break

			ret, buffer = cv2.imencode('.jpg', frame)
			frame = buffer.tobytes()
			# yield the frame as an http response
			yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

			

# cleanup
cv2.destroyAllWindows()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
