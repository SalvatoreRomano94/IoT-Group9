# P2
# Created at 2017-06-03 09:25:35.872708

#----------------------------
#Libreries of Zerynth
#----------------------------
import adc
import streams
import pwm
import timers
from wireless import wifi
from stm.spwf01sa import spwf01sa
from zerynthapp import zerynthapp
import i2c

streams.serial()

#----------------------------
# This function sets frequency for buzzer and uses PWM 
#----------------------------
def play(pin,hz):
    freq=1000000//hz
    duty=freq//2
    pwm.write(pin,freq,duty,MICROS)
    sleep(1000)

#----------------------------
# This function checks the value of alarm and security and plays buzzer or opens shutter depending on the results of if conditions
#----------------------------   
def buzzer_cycle():
    global alarm
    global security
    if alarm == True:
        open_shutter(-90)
    for x  in range(0, 10):
        if alarm == False and security==False:
            break
        play(pin_buzzer,1000)
        sleep(500)
        play(pin_buzzer,1000000)
    play(pin_buzzer,1000000)
    alarm=False
    zapp.event({'modality':modality,'state':angle,'alarm':alarm})

#----------------------------
# This function calculates pulse for the servo motor depending on angle value
#---------------------------- 
def position2pulse(angle):
    if angle<-90:
        angle=-90
    elif angle>90:
        angle=90
    pulse=590+(angle+90)*1830/180
    return int(pulse)

#----------------------------
# This function open shutter at the desired angle
#---------------------------- 
def open_shutter(angle_desired):
    global angle
    while angle>angle_desired:
        angle-=5
        pwm.write(pin_servo, PWM_PERIOD, position2pulse(angle), MICROS)
        print("ANGLE_OPEN=",angle," PHR=",phr)
        sleep(100)

#----------------------------
# This function close shutter at the desired angle
#----------------------------
def close_shutter(angle_desired):
    global angle
    while angle<angle_desired:
        angle+=5
        pwm.write(pin_servo, PWM_PERIOD, position2pulse(angle), MICROS)
        print("ANGLE_CLOSE=",angle," PHR=",phr)
        sleep(100)

#----------------------------
# This function sets modality depending on desired modality and pin depending on modality value
#----------------------------
def set_mod(desired_mod_app):
    global modality
    global led_pin_mod
    modality=desired_mod_app
    if modality == "automatic":
        digitalWrite(led_pin_mod,HIGH)
    else:
        digitalWrite(led_pin_mod,LOW)
        
    print(desired_mod_app)
    return modality

#----------------------------
# This function open shutter at the desidered angle
#----------------------------
def set_angle(desired_angle_app):
    global desired_angle
    desired_angle=desired_angle_app
    if angle>desired_angle:
        open_shutter(desired_angle)
    else:
        close_shutter(desired_angle)
    print("ANGLE=",angle)
    return angle

#----------------------------
# This function sets alarm at the time inserted on the app
#----------------------------
def set_alarm(delay):
    global alarm
    global t
    alarm=True
    t.one_shot(delay,buzzer_cycle)
    print("Alarm clock setted")
    return True

#----------------------------
# This function stops the alarm
#----------------------------
def stop_alarm(*args):
    global alarm
    global t
    t.clear()
    alarm=False
    print("Alarm clock stopped")
    return False

#----------------------------
# This function allows the user to open and close shutter manually if manual mod is active
#----------------------------
def manual_button():
    global modality, angle, mode_button
    if modality == "manual":
        while digitalRead(btn_pin)==LOW:
            if mode_button and angle>-90:
                open_shutter(angle-5)
            elif not mode_button and angle<90:
                close_shutter(angle+5)
        mode_button=not mode_button
    else:
        print("The modality is not setted to manual!")
        sleep(1000)
    zapp.event({'modality':modality,'state':angle,'alarm':alarm})

#----------------------------
# This function changes the modality from automatic to manual and vice versa 
#----------------------------
def button_mod():
    global modality
    global led_pin_mod
    if modality == "automatic":
        modality="manual"
        digitalWrite(led_pin_mod,LOW)
    else:
        modality="automatic"
        digitalWrite(led_pin_mod,HIGH)
    print(modality)
    zapp.event({'modality':modality,'state':angle,'alarm':alarm})
    sleep(500)

#----------------------------
# This function sends the parameters to the app
#----------------------------
def init(*args):
    global modality
    global alarm
    global angle
    global security
    return [modality,angle,alarm,security]

#----------------------------
# This function reads the proximity values and converted them
#----------------------------
def proximity():
    data = port.write_read(0x87,2)
    conv = data[1]|(data[0]<<8)
    return conv

#----------------------------
# This function stops the buzzer after the housebreak
#----------------------------
def stop_security(*args):
    global security
    global func_but
    print("Alarm stopped")
    security=False
    onPinFall(btn_pin,manual_button)
    zapp.event({'modality':modality,'state':angle,'alarm':alarm,'security':security})
    return False



alarm=False #set the default value of alarm variable
t=timers.timer() #initialize timer variable

#initialize proximity sensor
port = i2c.I2C(I2C1,0x13)
port.start()
port.write([0x80,0xFF])
port.write([0x82,0x00])

security=False #initialize the default value of security variable

btn_pin=BTN0
pinMode(btn_pin,INPUT_PULLUP)
mode_button=True #initialize the button for manual opening/closing shutter


modality="automatic" #initialize the default value of modality variable

led_pin_mod=D11 #set digital pin 11 for modality led
pinMode(led_pin_mod,OUTPUT)
digitalWrite(led_pin_mod,HIGH)

pin_but_mod=D12 #set digital pin 12 for modality button
pinMode(pin_but_mod,INPUT_PULLUP)


onPinFall(btn_pin,manual_button) #associate the manual_button function to the button btn_pin
onPinFall(pin_but_mod,button_mod) #associate the button_mod function to the button pin_but_mod

#initiaize servo motor
PWM_PERIOD=20000
pin_servo=D13.PWM
pinMode(pin_servo,OUTPUT)

#initiaize buzzer
pin_buzzer=D14.PWM
pinMode(pin_buzzer,OUTPUT)

#initialize photoresistor sensor
pin_fot=A5
pinMode(pin_fot, INPUT_ANALOG)

#initialize desired_angle variable
desired_angle=-90

uid='UlTCl0LLT4eKiFeX7JmAxg'
token='QGCGXn4bSL2zoFz6BNVUXA'




sleep(7000)
print("Start")

try:
    #trying to connect to internet
    spwf01sa.init(SERIAL2,D15)
    print("Connecting...")
    wifi.link('OnePlus3',wifi.WIFI_WPA2,'avellino')
    print("Connected")
    sleep(1000)
    
    # trying to connect to the app
    print('Connecting to Zerynth App...')
    zapp = zerynthapp.ZerynthApp(uid, token)
    print('zapp object created!')
    print('Start the app instance...')
    zapp.run()
    print('Instance started.')
    
    # association to the function called in javascript
    zapp.on('set_angle', set_angle)
    zapp.on('set_mod',set_mod)
    zapp.on('set_alarm',set_alarm)
    zapp.on('stop_alarm',stop_alarm)
    zapp.on('init',init)
    zapp.on('stop_security',stop_security)
    
    # first time initialization
    phr=adc.read(pin_fot)
    angle=0
    if phr>1000:
        open_shutter(-90)
    elif phr<700:
        close_shutter(90)
        
    zapp.event({'modality':modality,'state':angle,'alarm':alarm})

    while True:
        #This "if" checks the value of modality and begin the procedure of automatic/manual
        if modality=="automatic":
            phr = adc.read(pin_fot)
            #This "if" checks the value of photoresistor and angle for open shutter
            if phr>1000 and angle!=-90:
                open_shutter(-90)
                zapp.event({'modality':modality,'state':angle,'alarm':alarm})
            #This "if" checks the value of photoresistor and angle for close shutter
            elif phr<700 and angle!=90:
                close_shutter(90)
                zapp.event({'modality':modality,'state':angle,'alarm':alarm})
            sleep(500)
        else:   
            sleep(500)
        # This "if" checks the value of proximity sensor and angle for begin procedure  after housebreak
        if proximity() < 2800 and angle == 90:
            print(proximity(),"Start ALARM")
            security=True
            onPinFall(btn_pin,stop_security)
            zapp.event({'modality':modality,'state':angle,'alarm':alarm,'security':security})
            while security:
                buzzer_cycle()
except Exception as e:
    print(e)
