# import the necessary packages
#It provides a range of tools and functions for tasks such as classification, regression, clustering, and dimensionality reduction.
from sklearn.preprocessing import LabelEncoder
# It is used to train a support vector machine (SVM) classifier for supervised learning tasks.
from sklearn.svm import SVC
#provides functions for serializing and deserializing objects.
import pickle

# load the face embeddings
print("[INFO] loading face embeddings...")
#to deserialize an object from a file called "output/embeddings.pickle". 
data = pickle.loads(open("output/embeddings.pickle", "rb").read())
# encode the labels
print("[INFO] encoding labels...")
#utility class that can be used to encode categorical variables as integers.
le = LabelEncoder()
#fits the label encoder on the input data and returns the encoded values.
labels = le.fit_transform(data["names"])

# train the model used to accept the 128-d embeddings of the face and
# then produce the actual face recognition
print("[INFO] training model...")
recognizer = SVC(C=1.0, kernel="linear", probability=True)
recognizer.fit(data["embeddings"], labels)

# write the actual face recognition model to disk
f = open("output/recognizer", "wb")
f.write(pickle.dumps(recognizer))
f.close()

# write the label encoder to disk
f = open("output/le.pickle", "wb")
f.write(pickle.dumps(le))
f.close()