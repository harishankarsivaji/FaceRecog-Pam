#!/usr/bin/env python
# -*- coding: utf-8 -*-

import syslog
import os
import ConfigParser

from pamface import __version__ as VERSION
from pamface import CONFIG_FILE
from pamface import MODELS_FILE
from pamface.facerecognizer import PamFaceRecognizer

class UserUnknownException(Exception):

    pass

def showPAMTextMessage(pamh, message, errorMessage=False):
## Shows a PAM conversation text info. 

    try:
        if (errorMessage == True):
            style = pamh.PAM_ERROR_MSG
        else:
            style = pamh.PAM_TEXT_INFO

        msg = pamh.Message(style, 'PAM Face ' + VERSION + ': '+ str(message))
        pamh.conversation(msg)
        return True

    except Exception as e:
        auth_log(str(e), syslog.LOG_ERR)
        return False


def auth_log(message, priority=syslog.LOG_INFO):
## Sends errors to default authentication log

    syslog.openlog(facility=syslog.LOG_AUTH)
    syslog.syslog(priority, 'PAM Face: ' + message)
    syslog.closelog()


def pam_sm_authenticate(pamh, flags, argv):
## PAM service function for user authentication.

    ## The authentication service should return [PAM_AUTH_ERROR] if the user has a null authentication token
    flags = pamh.PAM_DISALLOW_NULL_AUTHTOK

    ## Initialize authentication progress
    try:
        ## Tries to get user which is asking for permission
        userName = pamh.ruser

        ## Fallback
        if (userName == None):
            userName = pamh.get_user()

        ## Be sure the user is set
        if (userName == None):
            raise UserUnknownException('The user is not known!')

        ## No user trained yet 
        if (os.path.getsize(MODELS_FILE) == 0):
            raise Exception('No user trained yet!')

        ## Check if file is readable
        if (os.access(CONFIG_FILE, os.R_OK) == False):
            raise Exception('The configuration file "' + CONFIG_FILE + '" is not readable!')

        configParser = ConfigParser.ConfigParser()
        configParser.read(CONFIG_FILE)

        ## Log the user
        auth_log('The user "' + userName + '" is asking for permission for service "' + str(pamh.service) + '".', syslog.LOG_DEBUG)

        ## Checks if the the user was added in configuration
        if (configParser.has_option('Users', userName) == False):
            raise Exception('The user was not added!')

        ## Read configuration data
        userLabel = int(configParser.get('Users', userName))
        threshold = int(configParser.get('Authentication', 'Threshold'))
        faceRecognizer = PamFaceRecognizer(configParser.get('Global', 'Camera'))

        ## Authentication progress
        showPAMTextMessage(pamh, 'Recognizing face ...')

        ## Try to predict user
        for _ in range(30):
            faces, grayScaleImage = faceRecognizer.detectFaces()
            face = grayScaleImage

            for (x, y, w, h) in faces:
                face = grayScaleImage[y:y+h,x:x+w]
                break

            predict = faceRecognizer.predict(face)

            if (predict[1] <= threshold):
                break

        ## Is the User found?
        if ((predict[0] == userLabel) and (predict[1] <= threshold)):
            auth_log('Access granted!')
            showPAMTextMessage(pamh, 'Access granted!')
            return pamh.PAM_SUCCESS
        else:
            auth_log('Face not recognized!', syslog.LOG_WARNING)
            showPAMTextMessage(pamh, 'Access denied!', True)
            return pamh.PAM_AUTH_ERR

    except UserUnknownException as e:
        auth_log(str(e), syslog.LOG_ERR)
        showPAMTextMessage(pamh, 'Access denied!', True)
        return pamh.PAM_USER_UNKNOWN

    except Exception as e:
        auth_log(str(e), syslog.LOG_ERR)
        return pamh.PAM_IGNORE

    ## Denies for default
    return pamh.PAM_AUTH_ERR


def pam_sm_setcred(pamh, flags, argv):
## PAM service function to alter credentials.

    return pamh.PAM_SUCCESS

def pam_sm_acct_mgmt(pamh, flags, argv):
## PAM service function for account management.

    return pamh.PAM_SUCCESS

def pam_sm_open_session(pamh, flags, argv):
## PAM service function to start session.

    return pamh.PAM_SUCCESS

def pam_sm_close_session(pamh, flags, argv):
## PAM service function to terminate session.

    return pamh.PAM_SUCCESS

def pam_sm_chauthtok(pamh, flags, argv):
## PAM service function for authentication token management.

    return pamh.PAM_SUCCESS
