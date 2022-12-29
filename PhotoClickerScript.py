import cv2
import sys
import time 

video_capture = cv2.VideoCapture(0) # selecting camera uisng opencv
image_count = 0 
while True:
    if not video_capture.isOpened():
        # Check if camera opened successfully
        print('Unable to load camera.')
        pass

    # Capture image-by-image
    ret, image = video_capture.read()
   
    if image_count <= 16:  # 52 images will be taken
        time.sleep(0.5) # wait 0.3 second
        cv2.imwrite('dataset/{}-Aaryan.jpg'.format(image_count), image)
    if image_count >= 16:
        # stop after 52 images
        print("Done")
        break
    
    image_count += 1 # increment image count    
    cv2.imshow('Video', image) # show video feed


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break # press q to quit
    

    

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()