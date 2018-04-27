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
