# This file was developed with help from PyImagesearch website
# Author: Omar Zayed and Vanessa Lama

from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time
import cv2
import numpy as np
import os
import subprocess
from send_mail import send_mail
from unknownDetection import play_UnknownSound
from detected import play_DetectedSound



# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing tthe stream)
outputFrame = None
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__)

#initialize the cascade xml and the trainer
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')
cascadePath = "Cascades/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath);
font = cv2.FONT_HERSHEY_SIMPLEX

# add the names in this list according to the dataset you have.
# for example ----> name = ["none", "John", "Mark"]
# leave the index of 0 to be none..
names = [] 
#iniciate id counter
id = 0
count = 0
# initialize the video stream and allow the camera sensor to
# warmup
cam = VideoStream(src=0).start()
time.sleep(1.0)

@app.route("/")
def index():
	# return the html template
	return render_template("index.html")

def face_recog(frameCount):
	# grab global references to the video stream, output frame, and
	# lock variables
	global cam, outputFrame, lock

	# loop over frames from the video stream
	while True:
            # read the next frame from the video stream, resize it,
            # convert the frame to grayscale, and blur it
            img = cam.read()
            img = imutils.resize(img, width=400)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (7, 7), 0)
            
            faces = faceCascade.detectMultiScale( 
                gray,
                scaleFactor = 1.2,
                minNeighbors = 5,
                minSize = (20, 20),
               )
    
            for(x,y,w,h) in faces:
                cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
                id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
                # Check if confidence is less them 100 ==> "0" is perfect match 
				#check if the face is recognized and put the the confidence percentage on the video
                if (confidence < 100):
                    name = str(names[id])
                    id = names[id]
                    play_DetectedSound(name)
                    confidence = "  {0}%".format(round(100 - confidence))
                else:
                    id = "unknown"
                    confidence = "  {0}%".format(round(100 - confidence))
                    send_mail(frame=img)
                    play_UnknownSound()

                
                cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
                cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  

            timestamp = datetime.datetime.now()
            cv2.putText(img, timestamp.strftime(
                    "%A %d %B %Y %I:%M:%S%p"), (10, img.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
 

            # acquire the lock, set the output frame, and release the lock
            with lock:
                    outputFrame = img.copy()
		
def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock

	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue

			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

			# ensure the frame was successfully encoded
			if not flag:
				continue

		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

# check to see if this is the main thread of execution
if __name__ == '__main__':
	# construct the argument parser and parse command line arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--ip", type=str, required=True,
		help="ip address of the device")
	ap.add_argument("-o", "--port", type=int, required=True,
		help="ephemeral port number of the server (1024 to 65535)")
	ap.add_argument("-f", "--frame-count", type=int, default=32,
		help="# of frames used to construct the background model")
	args = vars(ap.parse_args())

	# start a thread that will perform face recognition
	t = threading.Thread(target=face_recog, args=(
		args["frame_count"],))
	t.daemon = True
	t.start()

	# start the flask app
	app.run(host=args["ip"], port=args["port"], debug=True,
		threaded=True, use_reloader=False)

# release the video stream pointer
cam.stop()
