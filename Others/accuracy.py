# import libraries 
from imutils import paths
import numpy as np 
import imutils 
import cv2
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC 
# initialize the total number of faces processed
total = 0 # temporary variable 
populations = [52] # to calculate for what sample size
trainpercentages = [  0.5,0.60,0.65,0.75,0.8,0.9,0.95 ] # percentage of dataset to train (out of 1)
for population in populations:  
    for trainpercentage in trainpercentages: 
        # the below codes are the exact replica of embedding image files  
        protoPath = "face_detection_model/deploy.prototxt"
        modelPath = "face_detection_model/res10_300x300_ssd_iter_140000.caffemodel"
        detector = cv2.dnn.readNetFromCaffe(protoPath, modelPath) 
        embedder = cv2.dnn.readNetFromTorch("Others/openface_nn4.small2.v1.t7") 
        imagePaths = list(paths.list_images("dataset")) 
        # initialize our lists of extracted facial embeddings and corresponding people names
        knownEmbeddings = []
        knownNames = [] 
        train = int(trainpercentage * population)
        # loop over the image paths
        complete = False
        # the below code is the exact replica of the code to train the model
        for (i, imagePath) in enumerate(imagePaths): 
            # extract the person name from the image path 
            if i == train-1: 
                break
            name = imagePath.split(os.path.sep)[-1].split("-")[-1].split(".")[0]
            print(name)
            # load the image, resize it to have a width of 600 pixels (while maintaining the aspect ratio), and then grab the image dimensions
            image = cv2.imread(imagePath)
            image = imutils.resize(image, width=600)
            (h, w) = image.shape[:2] 
            # construct a blob from the image
            imageBlob = cv2.dnn.blobFromImage(
                cv2.resize(image, (300, 300)), 1.0, (300, 300),
                (104.0, 177.0, 123.0), swapRB=False, crop=False) 
            # apply OpenCV's deep learning-based face detector to localize faces in the input image
            detector.setInput(imageBlob)
            detections = detector.forward()
            # ensure at least one face was found
            if len(detections) > 0:
                # we're making the assumption that each image has only ONE face, so find the bounding box with the largest probability
                i = np.argmax(detections[0, 0, :, 2])
                confidence = detections[0, 0, i, 2] 
                # ensure that the detection with the largest probability also means our minimum probability test (thus helping filter out weak detections)
                if confidence > 0.5:
                    # compute the (x, y)-coordinates of the bounding box for the face
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int") 
                    # extract the face ROI and grab the ROI dimensions
                    face = image[startY:endY, startX:endX]
                    (fH, fW) = face.shape[:2] 
                    # ensure the face width and height are sufficiently large
                    if fW < 20 or fH < 20:
                        continue 
                    # construct a blob for the face ROI, then pass the blob through our face embedding model to obtain the 128-d quantification of the face
                    faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255,
                                                     (96, 96), (0, 0, 0), swapRB=True, crop=False)
                    embedder.setInput(faceBlob)
                    vec = embedder.forward() 
                    # add the name of the person + corresponding face embedding to their respective lists
                    knownNames.append(name)
                    knownEmbeddings.append(vec.flatten())
                    total += 1 
        # dump the facial embeddings + names to disk
        print("[INFO] serializing {} encodings...".format(total))
        data = {"embeddings": knownEmbeddings, "names": knownNames} 
        # the below code is th exact replica to train the model with the embedded photos 
        # encode the labels 
        le = LabelEncoder()
        labels = le.fit_transform(data["names"]) 
        print("[INFO] training model...")
        recognizer = SVC(C=1.0, kernel="linear", probability=True)
        recognizer.fit(data["embeddings"], labels) 
        teststart = train 
        fullmarks = 0
        accuracies = []  
        # the below code is the exact replica to test/ use the trained model to identify the face  
        for (i, imagePath) in enumerate(imagePaths):
            if(i >= teststart and i < population):
                fullmarks = fullmarks + 1
                image = cv2.imread(imagePath)
                nameactual = imagePath.split(
                    os.path.sep)[-1].split("-")[1].split(".")[0]
                image = imutils.resize(image, width=600)
                (h, w) = image.shape[:2] 
                # construct a blob from the image
                imageBlob = cv2.dnn.blobFromImage(
                    cv2.resize(image, (300, 300)), 1.0, (300, 300),
                    (104.0, 177.0, 123.0), swapRB=False, crop=False) 
                # apply OpenCV's deep learning-based face detector to localize faces in the input image
                detector.setInput(imageBlob)
                detections = detector.forward() 
                # loop over the detections
                for i in range(0, detections.shape[2]):
                    # extract the confidence (i.e., probability) associated with the prediction
                    confidence = detections[0, 0, i, 2]
                    # filter out weak detections
                    if confidence > 0.5:
                        # compute the (x, y)-coordinates of the bounding box for the face
                        box = detections[0, 0, i, 3:7] * \
                            np.array([w, h, w, h])
                        (startX, startY, endX, endY) = box.astype("int") 
                        # extract the face ROI
                        face = image[startY:endY, startX:endX]
                        (fH, fW) = face.shape[:2] 
                        # ensure the face width and height are sufficiently large
                        if fW < 20 or fH < 20:
                            continue 
                        # construct a blob for the face ROI, then pass the blob through our face embedding model to obtain the 128-d quantification of the face
                        faceBlob = cv2.dnn.blobFromImage(
                            face, 1.0 / 255, (96, 96), (0, 0, 0), swapRB=True, crop=False)
                        embedder.setInput(faceBlob)
                        vec = embedder.forward() 
                        # perform classification to recognize the face
                        preds = recognizer.predict_proba(vec)[0]
                        j = np.argmax(preds)
                        proba = preds[j] #probablity of prediction made by the model
                        name = le.classes_[j] # name of the face predicted based on the trained embeddings
                        if str(nameactual) == str(name): 
                            text = "{:.2f}".format(proba * 100) # formatting to nly last 2 decimal points
                            accuracies.append(float(text)) 
        total = 0
        for accuraci in accuracies:
            total = total + accuraci #calculating the accuracies total 
        verd = " \n" # empty verdict to prevent errors
        try:
            verd = "Sample = " + str(population) + "\nTrain Percentage = " + str("{:.2f}".format(trainpercentage*100)) + "%" + "\nGross Accuracy = "+str(
                "{:.2f}".format(total/len(accuracies))) + "%\n" + "Net Accuracy = " + str(
                "{:.2f}".format(total/fullmarks)) + "%\n" + "Detection Rate = "+str(
                "{:.2f}".format(100 * len(accuracies)/fullmarks))+"%\n" 
        except:
            pass
        print(verd)
        fil = open("verdict.txt", "a")
        fil.write(verd)
        fil.close() 