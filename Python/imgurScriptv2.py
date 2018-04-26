import imgurpython
from imgurpython import ImgurClient
from datetime import datetime
from time import gmtime, strftime
import calendar
import time
import sys 
import os 

os.system("fswebcam -r 800x600 -d /dev/video0 /home/pi/motionDetector/screenshots/image.jpg")

client_id = 'client_id a insertar'
client_secret = 'client_secret a insertar'
access_token = 'access_token a insertar'
refresh_token = 'refresh_token a insertar'

client = ImgurClient(client_id, client_secret, access_token, refresh_token)

def ImgUR(): 
        imagen = client.upload_from_path("/home/pi/motionDetector/screenshots/image.jpg",None,False)
        return strftime("%a, %d %b %Y %H:%M:%S", gmtime())+ " - https://imgur.com/"+imagen['id']
result = ImgUR()
