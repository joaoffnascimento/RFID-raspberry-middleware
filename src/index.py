import MFRC522
import RPi.GPIO as GPIO
import time
import datetime
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from decouple import config  # pip install python-decouple
from pymongo import MongoClient
import pymongo

reader_module = MFRC522.MFRC522()

endpoint = config('AWS_IOT_ENDPOINT')
readerLocal = config('READER_LOCAL')
topic = 'home/tag-touch-events'
mongo_uri = config('MONGO_URI')
mongo_database = 'rfid'

myMQTTClient = AWSIoTMQTTClient('RaspberryIotId')
myMQTTClient.configureEndpoint(endpoint, 8883)
myMQTTClient.configureCredentials('/home/pi/aws-credentials/AmazonRootCA1.pem',
                                  '/home/pi/aws-credentials/private.pem.key',
                                  '/home/pi/aws-credentials/certificate.pem.crt')

# Infinite offline Publish queueing
myMQTTClient.configureOfflinePublishQueueing(-1)
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

print('STARTING REALTIME DATA TRANSFER FROM RASPBERRY PI...')
print('----------------------------------------------------')

myMQTTClient.connect()

print('CONNECTED TO TOPIC: ' + topic)
print('THE READER IS SET UP ON SITE: : ' + readerLocal)


def tag_reader():
    while True:
        # Checks for TAG on the reader
        (status, TagType) = reader_module.MFRC522_Request(
            reader_module.PICC_REQIDL)

        # TAG reading
        if status == reader_module.MI_OK:
            (status, uid) = reader_module.MFRC522_Anticoll()
            uid = ''.join(str(reg) for reg in uid)
            print('----------------------------------------------------')
            print('TAG Detected : { tagUid:', uid, ' }')
            break
    return uid


def publish_event(uid, timestamp, local):
    print('PUBLISHING EVENT TO ' + topic)
    myMQTTClient.publish(
        topic,
        QoS=1,
        payload='{"tagUid":"' + str(uid) + '", "timestamp":"' +
        timestamp + '", "local":"' + local + '"}'
    )


def get_connection():
    client = MongoClient(mongo_uri)

    return client[mongo_database]


def save_tag_touch_event(uid, timestamp):
    mongoConnection = get_connection()
    mongoRepository = mongoConnection["tagTouchEvents"]

    tag_touch_event = {
        'tagUid': uid,
        'timestamp': timestamp,
        'local': readerLocal
    }

    mongoRepository.insert_one(tag_touch_event)

    print('TAG TOUCH EVENT SAVED: { tagUid:',
          uid, ': timestamp: ', timestamp, ' }')


def main():
    while True:
        uid = tag_reader()
        publish_event(uid, str(datetime.datetime.now()), readerLocal)
        save_tag_touch_event(uid, str(datetime.datetime.now()))
        time.sleep(.5)


try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
