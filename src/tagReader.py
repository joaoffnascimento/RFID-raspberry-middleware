import MFRC522
import RPi.GPIO as GPIO
import time

readerModule = MFRC522.MFRC522()

while True:
    # Checks for TAG on the reader module
    (status, TagType) = readerModule.MFRC522_Request(readerModule.PICC_REQIDL)

    # TAG reading
    if status == readerModule.MI_OK:
        print('TAG Detected!')
        (status, uid) = readerModule.MFRC522_Anticoll()
        print('uid: ', uid)

    time.sleep(.5)


