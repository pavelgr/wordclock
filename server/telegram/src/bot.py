#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import hashlib
import base64
import subprocess
import datetime
import json
import shutil
from io import StringIO
from io import BytesIO
import paho.mqtt.client as paho
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import config
import utils

logging.basicConfig(format='%(asctime)s, %(name)s, %(levelname)s, %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

mqttClient = None
dispatcher = None
chatId = None

def mqttOnConnect(client, userdata, flags, rc):
    client.subscribe(config.env[config.MQTT_TOPIC_RESPONSE])


def mqttOnMessage(client, userdata, message):
    # print('mqttOnMessage:' + message.topic + ": " + message.payload.decode("utf-8")[0:20])

    try:
        data = json.loads(message.payload.decode("utf-8"), encoding='utf-8')

        if (data['type'] == 'image'):
            postImage(utils.base64Decode(data['value']))

    except Exception as exception:
        print('mqttOnMessage: failed to process request: ' + utils.getExceptionMessage(exception))


def mqttPublish(topic, message):
    # print('mqttPublish: ' + topic + ': ' + message[0:20])

    mqttClient.publish(topic, message) #.wait_for_publish()


def checkUser(bot, user):
    try:
        groupMember = bot.get_chat_member(int(config.env[config.TELEGRAM_CONTROL_GROUP_ID]), user.id)
        ['creator', 'administrator', 'member'].index(groupMember.status)
    except Exception as e:
        raise Exception("failed to check user")


def updateChatId(chatIdNew):
    global chatId
    chatId = chatIdNew


def commandStart(update, context):
    checkUser(context.bot, update.message.from_user)
    updateChatId(update.message.chat.id)

    update.message.reply_text('Hi!')


def commandHelp(update, context):
    checkUser(context.bot, update.message.from_user)
    updateChatId(update.message.chat.id)

    helpText="""
    Help!
    Usage:
    /clock
    /image
    /weather
    /text
    [text]
    [image]
    """
    update.message.reply_text(helpText)


def commandClock(update, context):
    checkUser(context.bot, update.message.from_user)
    updateChatId(update.message.chat.id)

    try:
        topic = config.env[config.MQTT_TOPIC_REQUEST]
        message = json.dumps({'type': 'clock', 'value': ' '.join(context.args)})
        mqttPublish(topic, message)

        update.message.reply_text('ok')

    except Exception as exception:
        logger.exception('clock: failed to process command: %s', utils.getExceptionMessage(exception))
    
        update.message.reply_text('Something went wrong...')


def commandImage(update, context):
    checkUser(context.bot, update.message.from_user)
    updateChatId(update.message.chat.id)

    try:
        topic = config.env[config.MQTT_TOPIC_REQUEST]
        message = json.dumps({'type': 'image', 'value': ''})
        mqttPublish(topic, message)

        update.message.reply_text('ok')

    except Exception as exception:
        logger.exception('image: failed to process command: %s', utils.getExceptionMessage(exception))
    
        update.message.reply_text('Something went wrong...')


def commandWeather(update, context):
    checkUser(context.bot, update.message.from_user)
    updateChatId(update.message.chat.id)

    try:
        topic = config.env[config.MQTT_TOPIC_REQUEST]
        message = json.dumps({'type': 'weather', 'value': ''})
        mqttPublish(topic, message)

        update.message.reply_text('ok')

    except Exception as exception:
        logger.exception('weather: failed to process command: %s', utils.getExceptionMessage(exception))
    
        update.message.reply_text('Something went wrong...')


def commandText(update, context):
    checkUser(context.bot, update.message.from_user)
    updateChatId(update.message.chat.id)

    try:
        topic = config.env[config.MQTT_TOPIC_REQUEST]
        message = json.dumps({'type': 'text', 'value': ''})
        mqttPublish(topic, message)

        update.message.reply_text('ok')

    except Exception as exception:
        logger.exception('text: failed to process command: %s', utils.getExceptionMessage(exception))
    
        update.message.reply_text('Something went wrong...')


def contentText(update, context):
    checkUser(context.bot, update.message.from_user)
    updateChatId(update.message.chat.id)

    logger.info('text: from: {0}/{1}, message: {2}'.format(update.message.from_user.name, update.message.from_user.id, update.message.text))

    try:
        topic = config.env[config.MQTT_TOPIC_REQUEST]
        message = json.dumps({'type': 'text', 'value': update.message.text})
        mqttPublish(topic, message)

        update.message.reply_text('ok')

    except Exception as exception:
        logger.exception('photo: failed to process text: %s', utils.getExceptionMessage(exception))
    
        update.message.reply_text('Something went wrong...')


def contentPhoto(update, context):
    checkUser(context.bot, update.message.from_user)
    updateChatId(update.message.chat.id)

    image = update.message.photo[-1]

    logger.info('image: from: {0}/{1}, image: {2}'.format(update.message.from_user.name, update.message.from_user.id, image.file_id))

    try:
        imageFile = context.bot.get_file(image.file_id)
        imagePath = config.outputDir + 'image.jpg'
        imageFile.download(imagePath)

        output = BytesIO()
        with open(imagePath, "rb") as image:
            shutil.copyfileobj(image, output)
            output.seek(0)

        topic = config.env[config.MQTT_TOPIC_REQUEST]
        message = json.dumps({'type': 'image', 'value': utils.base64Encode(output.getvalue())})
        mqttPublish(topic, message)
        
        update.message.reply_text('ok')

    except Exception as exception:
        logger.exception('photo: failed to process photo: %s', utils.getExceptionMessage(exception))
    
        update.message.reply_text('Something went wrong...')


def postImage(image):
    if (chatId != None):
        try:
            dispatcher.bot.send_photo(chat_id=chatId, photo=BytesIO(image)) #open('tests/test.png', 'rb'))

        except Exception as exception:
            logger.exception('photo: failed to send photo: %s', utils.getExceptionMessage(exception))


def handlerError(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    global mqttClient    
    global dispatcher

    os.makedirs(config.outputDir, exist_ok=True)

    mqttClient = paho.Client()
    mqttClient.on_connect = mqttOnConnect
    mqttClient.on_message = mqttOnMessage
    mqttClient.connect(config.env[config.MQTT_HOST], int(config.env[config.MQTT_PORT]))


    updater = Updater(config.env[config.TELEGRAM_TOKEN], use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", commandStart))
    dispatcher.add_handler(CommandHandler("help", commandHelp))
    dispatcher.add_handler(CommandHandler("clock", commandClock))
    dispatcher.add_handler(CommandHandler("image", commandImage))
    dispatcher.add_handler(CommandHandler("weather", commandWeather))
    dispatcher.add_handler(CommandHandler("text", commandText))

    dispatcher.add_handler(MessageHandler(Filters.text & Filters.language('en'), contentText))
    dispatcher.add_handler(MessageHandler(Filters.photo, contentPhoto))

    dispatcher.add_error_handler(handlerError)

    updater.start_polling()


    # mqttClient.loop_forever(timeout=5.0, max_packets=1, retry_first_connection=True)
    mqttClient.loop_start()


    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


    mqttClient.loop_stop()


if __name__ == '__main__':
   main()
