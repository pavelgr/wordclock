#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import dotenv

# TELEGRAM_TOKEN="TELEGRAM_TOKEN"
# TELEGRAM_CONTROL_GROUP_ID="TELEGRAM_CONTROL_GROUP_ID"

STORAGE_DIR="STORAGE_DIR"

MQTT_HOST="MQTT_HOST"
MQTT_PORT="MQTT_PORT"
MQTT_TOPIC_CONTROL="MQTT_TOPIC_CONTROL"
MQTT_TOPIC_REQUEST="MQTT_TOPIC_REQUEST"
MQTT_TOPIC_RESPONSE="MQTT_TOPIC_RESPONSE"

ACCUWEATHER_API_KEY='ACCUWEATHER_API_KEY'
ACCUWEATHER_LOCATION_KEY='ACCUWEATHER_LOCATION_KEY'


scriptDir = sys.path[0] #os.path.dirname(os.path.realpath(__file__))
envPath = scriptDir + '/../.env'
env = dotenv.dotenv_values(dotenv_path=envPath)

outputDir = env[STORAGE_DIR]
outputDir = outputDir if outputDir.startswith('/') else (scriptDir + '/' + outputDir)
fontsDir = scriptDir + '/../resources/fonts/'
iconsDir = scriptDir + '/../resources/icons/'
