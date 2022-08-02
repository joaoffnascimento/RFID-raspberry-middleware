import boto3
import MFRC522
import RPi.GPIO as GPIO
import time
import datetime
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from decouple import config #pip install python-decouple

reader_module = MFRC522.MFRC522()

endpoint = config('AWS_IOT_ENDPOINT')
readerLocal = config('READER_LOCAL')
topic = "/home/tag-touch-events"
aws_access_key_id = config('aws_access_key_id')
aws_secret_access_key = config('aws_secret_access_key')

client = boto3.client('dynamodb', aws_access_key_id, aws_secret_access_key)

dynamodb = boto3.resource('dynamodb', aws_access_key_id, aws_secret_access_key)

log = dynamodb.Table('log')

myMQTTClient = AWSIoTMQTTClient("RaspberryIotId")
myMQTTClient.configureEndpoint(endpoint, 8883)
myMQTTClient.configureCredentials("/home/pi/aws-credentials/AmazonRootCA1.pem",
                                  "/home/pi/aws-credentials/private.pem.key",
                                  "/home/pi/aws-credentials/certificate.pem.crt")

myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

print('Starting Realtime Data Transfer From Raspberry Pi...')

myMQTTClient.connect()

print('Connected to topic: ' + topic)
print('The reader is set up on site: : ' + readerLocal)


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


def save_tag_log(uid, timestamp):
    log.put_item(
        Item={
            'tag_uid': uid,
            'timestamp': timestamp,
            'local': readerLocal
        }
    )
    print('Saved TAG read log!')


def publish_event(uid, timestamp, local):
    print("Publishing MQTT Message from RaspberryPI on topic " + topic)
    myMQTTClient.publish(
        topic,
        QoS=1,
        payload='{"tag_uid":"' + str(uid) + '", "timestamp":"' + timestamp + '", "local":"' + local + '"}'
    )


def main():
    while True:
        uid = tag_reader()
        save_tag_log(uid, str(datetime.datetime.now()))
        publish_event(uid, str(datetime.datetime.now()), readerLocal)
        time.sleep(.5)


try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()

