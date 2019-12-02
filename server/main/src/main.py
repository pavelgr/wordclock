#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import signal
import json
from io import BytesIO
import paho.mqtt.client as paho

import config
import utils
import image
import weather

logging.basicConfig(format='%(asctime)s, %(name)s, %(levelname)s, %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

mqttClient = None


def signalHandler(signum, frame):
    mqttClient.disconnect()


def mqttOnConnect(client, userdata, flags, rc):
    client.subscribe(config.env[config.MQTT_TOPIC_REQUEST])


def mqttOnMessage(client, userdata, message):
    # print('mqttOnMessage:' + message.topic + ": " + message.payload.decode("utf-8")[0:20])

    try:
        data = json.loads(message.payload.decode("utf-8"), encoding='utf-8')
        requestTypeSwitcher[data['type']](data['value'])

    except Exception as exception:
        logger.exception('mqttOnMessage: failed to process request: %s', utils.getExceptionMessage(exception))


def mqttPublish(topic, message):
    # print('mqttPublish: ' + topic + ': ' + message[0:20])

    mqttClient.publish(topic, message) #.wait_for_publish()


def requestClock(data):
    try:
        output = data

        topic = config.env[config.MQTT_TOPIC_CONTROL]
        message = json.dumps({'type': 'clock', 'value': output})
        mqttPublish(topic, message)

    except Exception as exception:
        logger.exception('requestClock: failed to process request: %s', utils.getExceptionMessage(exception))


def requestWeather(data):
    try:
        output = BytesIO()
        weather.prepareWeatherForecast(output)

        topic = config.env[config.MQTT_TOPIC_RESPONSE]
        message = json.dumps({'type': 'image', 'value': utils.base64Encode(output.getvalue())})
        mqttPublish(topic, message)

        output.seek(0)
        input = output
        output = BytesIO()
        image.rotateImage(input, output)

        topic = config.env[config.MQTT_TOPIC_CONTROL]
        message = json.dumps({'type': 'weather', 'value': utils.base64Encode(output.getvalue())})
        mqttPublish(topic, message)

    except Exception as exception:
        logger.exception('requestWeather: failed to process request: %s', utils.getExceptionMessage(exception))


def requestImage(data):
    try:
        output = ''

        if (data != ''):
            data = utils.base64Decode(data)
        
            input = BytesIO(data)
            output = BytesIO()
            image.prepareImage(input, output)

            topic = config.env[config.MQTT_TOPIC_RESPONSE]
            message = json.dumps({'type': 'image', 'value': utils.base64Encode(output.getvalue())})
            mqttPublish(topic, message)

            output.seek(0)
            input = output
            output = BytesIO()
            image.rotateImage(input, output)

            output = utils.base64Encode(output.getvalue())

        topic = config.env[config.MQTT_TOPIC_CONTROL]
        message = json.dumps({'type': 'image', 'value': output})
        mqttPublish(topic, message)

    except Exception as exception:
        logger.exception('requestImage: failed to process request: %s', utils.getExceptionMessage(exception))


def requestText(data):
    try:
        output = ''

        if (data != ''):
            output = BytesIO()
            image.renderText(data, output)

            topic = config.env[config.MQTT_TOPIC_RESPONSE]
            message = json.dumps({'type': 'image', 'value': utils.base64Encode(output.getvalue())})
            mqttPublish(topic, message)

            output.seek(0)
            input = output
            output = BytesIO()
            image.rotateImage(input, output)

            output = utils.base64Encode(output.getvalue())

        topic = config.env[config.MQTT_TOPIC_CONTROL]
        message = json.dumps({'type': 'text', 'value': output})
        mqttPublish(topic, message)

    except Exception as exception:
        logger.exception('requestText: failed to process request: %s', utils.getExceptionMessage(exception))


requestTypeSwitcher = {'clock': requestClock, 'weather': requestWeather, 'image': requestImage, 'text': requestText}


def main():
    global mqttClient

    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGABRT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
    # signal.signal(signal.SIGKILL, signalHandler)

    os.makedirs(config.outputDir, exist_ok=True)

    mqttClient = paho.Client()
    mqttClient.on_connect = mqttOnConnect
    mqttClient.on_message = mqttOnMessage
    mqttClient.connect(config.env[config.MQTT_HOST], int(config.env[config.MQTT_PORT]))

    mqttClient.loop_forever(timeout=5.0, max_packets=1, retry_first_connection=True)

if __name__ == '__main__':
   main()
