import imgurpython
from imgurpython import ImgurClient
from datetime import datetime
from time import gmtime, strftime
import calendar
import time
import sys 
import os 

z = 1 
while z<10: 
        os.system("fswebcam -r 800x600 -d /dev/video0 /home/pi/motionDetector/screenshots/image_"+str(z)+".jpg")
        z = z + 1

client_id = 'client_id a insertar'
client_secret = 'client_secret a insertar'
access_token = 'access_token a insertar'
refresh_token = 'refresh_token a insertar'

client = ImgurClient(client_id, client_secret, access_token, refresh_token)
fields = {}
fields['title'] = "Otro album de Copernico - "+strftime("%a, %d %b %Y %H:%M:%S", gmtime())
fields['privacy'] = 'public'

album = client.create_album(fields)
str = "https://imgur.com/a/"+album['id']

def ImgUR(): 
        z = [1]
        while z[0] < 10:
                imagen = client.upload_from_path("/home/pi/motionDetector/screenshots/image_%01d.jpg"% z[0],None,False)
                client.album_add_images(album['id'], imagen['id'])
                z[0] = z[0] + 1
                if z[0] == 10:
                        return strftime("%a, %d %b %Y %H:%M:%S", gmtime())+ " - "+str+" https://imgur.com/"+imagen['id']
result = ImgUR()
