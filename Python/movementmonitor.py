# Autor original: http://fpaez.com/sensor-de-movimiento-infrarojo-hc-sr501/
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
