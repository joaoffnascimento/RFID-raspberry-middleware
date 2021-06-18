import boto3
import MFRC522
import RPi.GPIO as GPIO
import time
import datetime

dynamodb = boto3.resource('dynamodb')

tag_table = dynamodb.Table('tag')

reader_module = MFRC522.MFRC522()


def tag_reader():
    while True:
        # Checks for TAG on the reader
        (status, TagType) = reader_module.MFRC522_Request(reader_module.PICC_REQIDL)

        # TAG reading
        if status == reader_module.MI_OK:
            print('TAG Detected!')
            (status, uid) = reader_module.MFRC522_Anticoll()
            uid = ''.join(str(reg) for reg in uid)
            break
    return uid


def save_tag(uid):
    timestamp = str(datetime.datetime.now())
    tag_table.put_item(
        Item={
            'id': uid,
            'timestamp': timestamp,
            'local': 'CBSI'
        }
    )
    print('TAG saved!')


try:
    while True:
        uid = tag_reader()
        save_tag(uid)
        time.sleep(.5)
except KeyboardInterrupt:
    GPIO.cleanup()
