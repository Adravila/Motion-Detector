# Motion-Detector
Sistema dedicado para la detección de objectos con un sensor de movimiento Arduino en el cuál realiza una captura de imagen a partir de una webcam, posteriormente lo sube a imgur y finalmente se publica un mensaje a partir de una cuenta de Twitter con la fecha, hora y la imagen con el enlace de imgur.

![](http://i.imgur.com/5S0eWoE.png)

## ¿Qué hemos utilizado?
### Hardware:
- Sensor de movimiento (Arduino)
- Raspberry Pi 3 Model B+
- Componentes del Ultimate Starter Kit de la Raspberry Pi

### Sofware:
- Raspbian
- Python 2.7
- imgurpython

## Acceso a la Raspberry Pi
### Configuración de la red
Para ello tendremos que instalar en una tarjeta microSD el SO Raspbian, una vez hecho tendremos que añadir dos ficheros de configuración durante el boot. Nos situamos en /media/usuario/boot para añadir los siguientes ficheros:
- Un fichero llamado *ssh*, que esté vacío y sin extensión.
- Creamos un fichero *wpa_supplicant.conf* y editamos:
```
# /etc/wpa_supplicant/wpa_supplicant.conf

ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev 
update_config=1

network={
 ssid="my ssid"
 psk="my psk"
 key_mgmt=WPA-PSK 
}
```
Con ello, de forma automática el *boot* generará los ficheros necesarios dentro de */media/usuario/rootfs*. Dentro de este directorio añadimos unas líneas al fichero */media/saged/rootfs/etc/dhcpd.conf* para que podamos conectar de forma estática, por ejemplo:
```
interface wlan0 
static ip_address=192.168.0.3/24 
static routers=192.168.0.1
static domain_name_servers=192.168.0.1
```
Esto ya dependerá de la red que dispongas.

Una vez listo entramos por la terminal, escribiendo:
```
ssh pi@tu_ip_local
```
La contraseña por defecto será raspberry.

## Código Python necesario para la ejecución del ESB Mule y la detección de movimiento

Se debe crear una carpeta en el directorio /home/pi llamado *motionDetector*, dentro del directorio se debe crear dos ficheros necesarios, uno dentro de al ejecución del app *motiondetector* de Mule y otro independientemente para detectar el movimiento y lanzar la petición a la dirección *http://localhost:8081/update*.

File: movementmonitor.py                                                                      
```
import urllib2
import RPi.GPIO as GPIO    #Importamos la libreria GPIO
import time                #Importamos time
from time import gmtime, strftime  #importamos gmtime y strftime
GPIO.setmode(GPIO.BCM)             #Configuramos los pines GPIO como BCM
PIR_PIN = 18                        #Usaremos el pin GPIO n7
GPIO.setup(PIR_PIN, GPIO.IN)       #Lo configuramos como entrada
 
GPIO.setup(17, GPIO.OUT)          #Configuramos el pin 17 como salida (para un led)

try:
        while True:  #Iniciamos un bucle infinito
                if GPIO.input(PIR_PIN):  
                        GPIO.output(17,True) #Encendemos el led
                        time.sleep(1)
                        timex = strftime("%d-%m-%Y %H:%M:%S", gmtime()) #Creamos una cadena de texto con la hora
                        print timex + " MOVIMIENTO DETECTADO"  #La sacamos por pantalla
                        time.sleep(1)
                        GPIO.output(17,False)  #Apagamos el led
                        print urllib2.urlopen("http://localhost:8081/update").read() #Hacemos la peticion a mule
                time.sleep(1)              #Pausa de 1 segundo y vuelta a empezar
except KeyboardInterrupt:   #Si el usuario pulsa CONTROL + C...
    print "quit"            #Anunciamos que finalizamos el script
    GPIO.cleanup()          #Limpiamos los pines GPIO y salimos
```
File: imgurScript.py                                                                      
```
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
```
Para hacerlo más simple sin necesidad de crear un álbum, hacer diez capturas de pantalla y subir esas diez imágenes en imgur, en su lugar, eliminamos la opción de crear un álbum y se sube una única foto. Así se realizará todo el proceso de manera más rápida y óptima.

File: imgurScript.py (version 2.0)                                                                  
```
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
```

## Por completar
Standalone Mule 3.9.0
https://developer.mulesoft.com/download-mule-esb-runtime

mule@raspberrypi:/opt/mule/mule-standalone-3.9.0/bin$ sudo ./mule -app proyecto -M-Dpython.path=/home/pi/.local/lib/python2.7/site-packages

Enlace del proyecto de Mule (ver 3.9.0)
https://drive.google.com/open?id=1rt4swIM7tdoJAjRu6q5YySFOWAcjxdwz

## Fuentes externas
- http://fpaez.com/sensor-de-movimiento-infrarojo-hc-sr501/
