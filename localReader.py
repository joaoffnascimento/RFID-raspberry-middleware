import MFRC522
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)

allowed_tags = {
    (217, 108, 175, 71, 93): 'joao',
    (249, 114, 200, 85, 22): 'felipe'
}

readerModule = MFRC522.MFRC522()


def release_port():
    GPIO.output(7, 1)
    # print('Open Door')
    time.sleep(3)
    # print('Closed Door')
    GPIO.output(7, 0)


try:
    while True:
        # Checks for TAG on the reader module
        (status, TagType) = readerModule.MFRC522_Request(readerModule.PICC_REQIDL)

        # TAG reading
        if status == readerModule.MI_OK:
            print('TAG Detected!')
            (status, uid) = readerModule.MFRC522_Anticoll()
            uid = tuple(uid)

            if uid in allowed_tags.keys():
                print('ID: {} - Access released!'.format(allowed_tags[uid]))
                release_port()
            else:
                print('ID: invalid - Access Denied!')

        time.sleep(.5)

except KeyboardInterrupt:
    GPIO.cleanup()
