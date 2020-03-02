#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy
import os

from pamface import MODELS_FILE

# Checks for a given OpenCV version.
def checkOpenCVVersion(major, minor = 0):

    return ((int(cv2.__version__[0]) >= major) and (int(cv2.__version__[2]) >= minor))

# Wrapper around OpenCV FaceRecognizer to support OpenCV 2 and 3.
class PamFaceRecognizer(object):

    __faceRecognizer = None
    __videoCapture = None
    __faceCascade = None

    def __init__(self, camera):

        try:
            camera = int(camera)

        except ValueError:
            pass

        self.__videoCapture = cv2.VideoCapture(camera)
        self.__faceCascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml')

        ## Initialize Face Recognizer
        if (checkOpenCVVersion(3, 3)):
            self.__faceRecognizer = cv2.face.LBPHFaceRecognizer_create()
        elif (checkOpenCVVersion(3)):
            self.__faceRecognizer = cv2.face.createLBPHFaceRecognizer()
        else:
            self.__faceRecognizer = cv2.createLBPHFaceRecognizer()

        ## Check if models.xml is readable
        if (os.access(MODELS_FILE, os.R_OK) == False):
            raise Exception('The models file "' + MODELS_FILE + '" is not readable!')

        ## Any model trained?
        if (os.path.getsize(MODELS_FILE) > 0):
            if (checkOpenCVVersion(3, 3)):
                self.__faceRecognizer.read(MODELS_FILE)
            else:
                self.__faceRecognizer.load(MODELS_FILE)

    def __del__(self):
    # Destructor for destroying a PamFaceRecognizer instance.

        if (self.__videoCapture != None):
            self.__videoCapture.release()

    def detectFaces(self):
    # Detects all faces in front of video device.

        result, image = self.__videoCapture.read()

        if (result == False):
            raise Exception('Failed to read from video device!')

        grayScaleImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return (self.__faceCascade.detectMultiScale(grayScaleImage, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE), grayScaleImage)

    def predict(self, image):
    #Tries to predict a user on a specified image.

        return self.__faceRecognizer.predict(image)

    def update(self, faces, labels):
    # Updates face model of a specified user.

        self.__faceRecognizer.update(numpy.array(faces), numpy.array(labels))

        ## Store model
        if (checkOpenCVVersion(3, 3)):
            self.__faceRecognizer.write(MODELS_FILE)
        else:
            self.__faceRecognizer.save(MODELS_FILE)

    def showImage(self, image):
    # Shows the specified image in a window.

        cv2.imshow('PAM Face', image)
        cv2.waitKey(100)
