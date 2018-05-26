# Motion-Detector
Sistema dedicado para la detección de objectos con un sensor de movimiento Arduino en el cuál realiza una captura de imagen a partir de una webcam, posteriormente lo sube a imgur y finalmente se publica un mensaje a partir de una cuenta de Twitter con la fecha, hora y la imagen con el enlace de imgur.

## Autores del trabajo
- Cano Canalejas, Esperanza
- Dávila Guerra, Adrián
## ¿Qué hemos utilizado?
### Hardware:
- [Sensor de movimiento Arduino](https://www.amazon.es/Neuftech-Sensor-Motion-Infrarrojos-Piroelectricidad/dp/B01C6O9C38/ref=sr_1_1?ie=UTF8&qid=1524738515&sr=8-1&keywords=sensor+de+movimiento+arduino)
- [Raspberry Pi 3 Model B+](https://www.amazon.es/Raspberry-Pi-RPI-Model-PLUS/dp/B07BDR5PDW/ref=sr_1_9?s=electronics&ie=UTF8&qid=1524738980&sr=1-9&keywords=raspberry+pi+3&dpID=41bqUv%252BKc8L&preST=_SX300_QL70_&dpSrc=srch)
- [Componentes del Ultimate Starter Kit de la Raspberry Pi](https://www.amazon.es/OSOYOO-Raspberry-Electronic-Learning-Beginner/dp/B074YZMRC1/ref=sr_1_1?s=electronics&ie=UTF8&qid=1524739071&sr=1-1&keywords=Ultimate+Starter+Kit+de+la+Raspberry+Pi&dpID=61SV3%252BDv2iL&preST=_SY300_QL70_&dpSrc=srch))
- [WebCam compatible para la Raspberry](https://elinux.org/RPi_USB_Webcams)

### Software:
- [Raspbian](https://www.raspberrypi.org/downloads/raspbian/)
- [Librería de Python de imgurpython](https://github.com/Imgur/imgurpython)
- [API de imgur](https://api.imgur.com/)
- [APP de Twitter](https://apps.twitter.com/)
- [Mule Standalone 3.9.0](https://developer.mulesoft.com/download-mule-esb-runtime)

## Instalación de los componentes de la Raspberry Pi
### Inserción de pines GPIO en Breadboard + sensor de movimiento
![](http://i.imgur.com/Hpd5gwK.png)

En esta imagen podremos ver los slots correspondientes de la tarjeta GPIO (ojo, hemos utilizado este modelo en concreto, puede variar algunos IDs descritos en la placa). Como podéis ver, hemos señalado qué pines vamos a utilizar:
- Utilizaremos el PIN 14 para encender/apagar el LED cuando enviamos datos en él.
- Para el detector de movimiento insertamos tres cables DuPont (macho-macho) para cada uno de los pines correspondientes. Uno en el PIN 18 que será el que enviará datos (output) del sensor de movimiento a la Raspberry Pi, GND que será para la toma de tierra y 5v0 para la corriente.

![](http://i.imgur.com/PcNAd1g.png)

Ahora si queremos ver cuáles son los pines que corresponde a los tres cables DuPont, debemos quitar la capsula del sensor de movimiento y mirar en su interior qué pines corresponden cada una de estos, de izquierda a derecha serían:
 - Corriente (+5V)
 - Envío de datos
 - Toma de tierra
 
## Creación de apps a partir de distintas API
### API de imgur
Debemos seguir una serie de pasos para crear nuestra APP de imgur y obtener la clave de API:
- Necesitamsos registrarnos en imgur https://imgur.com/
- Una vez creada la cuenta de imgur crearemos nuestra propia aplicación https://api.imgur.com/oauth2/addclient. 
- Durante el proceso del registro de la APP, el tipo de autenticación marcamos 'OAuth 2 authorization without a callback URL', lo siguiente sería insertar nuestro correo electrónico y la descripción de la APP.
- Una vez registrada la aplicación, nos vamos a la configuración de la cuenta y a la sección de apps para obtener  el **Client ID** 	**ClientSecret** https://imgur.com/account/settings/apps
- Finalmente, si tenemos Python 2.7 instalado en nuestra PC, debemos insertar en nuestro terminal las siguientes líneas para obtener el **access_token** y **refresh_token**.

```
python 
>> from imgurpython import ImgurClient
client_id = 'YOUR CLIENT ID'
client_secret = 'YOUR CLIENT SECRET'
client = ImgurClient(client_id, client_secret)
authorization_url = client.get_auth_url('pin')
print(authorization_url)

# Con esto nos generará un enlace de la página para obtener dicho PIN

credentials = client.authorize('PIN obtenido para la autenticación', 'pin')
print(credentials)

#Obtenemos el 'access_token' y 'refresh_token'
```

### API de Twitter
Al igual que todo el proceso para obtener la clave API de imgur, debemos seguir una serie de pasos:
- Creamos nuestra aplicación en https://apps.twitter.com/
- Una vez creada, nos vamos a la sección de 'Keys and Access Tokens'
- Necesitaremos las claves de Consumer Key (API Key), Consumer Secret (API Secret). 
- Click en *Create my acccess token* para obtener Access Token y Access Token Secret.
https://apps.twitter.com/
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
 ssid="mi_ssid"
 psk="mi_psk"
 key_mgmt=WPA-PSK 
}
```
Con ello, de forma automática el *boot* generará los ficheros necesarios dentro de */media/usuario/rootfs*. Dentro de este directorio añadimos unas líneas al fichero */media/usuario/rootfs/etc/dhcpd.conf* para que podamos conectar de forma estática, por ejemplo:
```
interface wlan0 
static ip_address=192.168.0.3/24 
static routers=192.168.0.1
static domain_name_servers=192.168.0.1
```
Esto ya dependerá de la red que dispongas.

En caso de que no se detecte la dirección ip escrita de forma estática, ya sea porque quizás está accediendo a una intefaz distinta (en vez de wlan0), escribimos ``` nmap 192.168.0.0/24``` por ejemplo, para localizar todas las direcciones IPs de dicha red.

Una vez listo entramos por la terminal, escribiendo:
```
ssh pi@tu_ip_local
```
La contraseña por defecto será raspberry.

### Código Python necesario para la ejecución del ESB Mule y la detección de movimiento

Se debe crear una carpeta en el directorio /home/pi llamado *motionDetector*, dentro del directorio se debe crear dos ficheros necesarios, uno dentro de al ejecución del app *motiondetection* de Mule y otro independientemente para detectar el movimiento y lanzar la petición a la dirección *http://localhost:8081/update*.

File: movementmonitor.py                                                                      
```python
import urllib2
import RPi.GPIO as GPIO
import time  
from time import gmtime, strftime 
GPIO.setmode(GPIO.BCM)  
PIR_PIN = 18
GPIO.setup(PIR_PIN, GPIO.IN) # Corresponde al sensor de movimiento (cable de datos)
GPIO.setup(17, GPIO.OUT) # Corresponde al LED 

try:
        while True: 
                if GPIO.input(PIR_PIN):  
                        GPIO.output(17,True)
                        time.sleep(1)
                        timex = strftime("%d-%m-%Y %H:%M:%S", gmtime())
                        print timex + " MOVIMIENTO DETECTADO"
                        time.sleep(1)
                        GPIO.output(17,False)
                        print urllib2.urlopen("http://localhost:8081/update").read() #Hacemos la peticion a mule
                time.sleep(1)
except KeyboardInterrupt:  
    print "Salir" 
    GPIO.cleanup()
```
File: imgurScript.py                                                                      
```python
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
Para hacerlo más simple sin necesidad de crear un álbum, hacer nueve capturas de pantalla y subir esas diez imágenes en imgur, en su lugar, eliminamos la opción de crear un álbum y se sube una única foto. Así se realizará todo el proceso de manera más rápida y óptima.

File: imgurScript.py (version 2.0)                                                                  
```python
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

### Configurando el Standalone de Mule y su ejecución.
Standalone Mule 3.9.0

https://developer.mulesoft.com/download-mule-esb-runtime

Para ello, recomiendo la instalación del Standalone de Mule a partir de este tutorial, teniendo en cuenta de que se está utilizando otra versión, por lo que es recomendable seguir los pasos con cuidado.

https://dzone.com/articles/running-mule-4-on-raspberry-pi

Una vez hecho, insertamos la línea ```su - mule``` y entramos en la siguiente dirección:
```cd /opt/mule/mule-standalone-3.9.0/app```

Pondremos nuestro proyecto comprimido con un .zip, no será necesario descomprimirlo dado que MuleSoft lo realiza de forma automática cuando ejecute dicha app. Acto seguido, nos movemos a la siguiente ruta:
```cd /opt/mule/mule-standalone-3.9.0/bin/```

Ejecutamos mule vía sh, añadimos dos argumentos: uno para arrancar la aplicación y el otro para que ejecute el código de Python en Cpython en lugar de Jpython, para que podamos utilizar los módulos de imgurpython y requests necesarios.
```
mule@raspberrypi:/opt/mule/mule-standalone-3.9.0/bin$ sudo ./mule -app motiondetection -M-Dpython.path=/home/pi/.local/lib/python2.7/site-packages
```

Una vez hecho esto, el archivo comprimido *motiondetection.zip* se descomprimirá en el directorio */app* de *mule-standalone-3.9.0*.
Cuando aparezca la siguiente imagen, se debe ejecutar otro terminal (se tendría que acceder otro terminal por ssh) el comando ```python movementmonitor.py``` para activar la detección de movimiento.

## Fuentes externas
- http://fpaez.com/sensor-de-movimiento-infrarojo-hc-sr501/
