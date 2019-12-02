#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import json
import urllib.request
import shutil
import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

import config

locationKey = config.env[config.ACCUWEATHER_LOCATION_KEY]
apiKey = config.env[config.ACCUWEATHER_API_KEY]

imageWidth, imageHeight = (800, 600)
offsetX, offsetY = (40, 40)
marginXstart, marginXend,  marginY = (10, 3, 0)
spacerWidth = 2
maxSections = 4

colorBackground = 'white'
colorBlack = 'black'
colorGray1 = '#1F1F1F'
colorGray2 = '#A7A7A7'
colorGray3 = '#E7E7E7'

iconWidth, iconHeight = (110, 110)

fontSizeSmall = 16
fontSizeRegular = 19
fontSizeLarge = 20
fontSizeTemperature = 38

fontFileRegular = config.fontsDir + 'LiberationSans-Regular.ttf'
fontFileBold = config.fontsDir + 'LiberationSans-Bold.ttf'

def getForecasts():
    try:
        url = 'http://dataservice.accuweather.com/forecasts/v1/hourly/1hour/{0}?apikey={1}&metric=true&details=true'.format(locationKey, apiKey)
        response = urllib.request.urlopen(url)
        hourlyForecast = json.loads(response.read())

        forecastCurrent = hourlyForecast[0]

        current={}
        current['title'] = 'Current' 
        current['date'] = forecastCurrent['DateTime']
        current['temperature'] = forecastCurrent['Temperature']['Value']
        current['icon'] = forecastCurrent['WeatherIcon']
        current['text'] = forecastCurrent['IconPhrase']
        current['textLong'] = forecastCurrent['IconPhrase']
        current['precipitationProbability'] = forecastCurrent['PrecipitationProbability']
        current['wind'] = forecastCurrent['Wind']['Speed']['Value']

        url = 'http://dataservice.accuweather.com/forecasts/v1/daily/5day/{0}?apikey={1}&metric=true&details=true'.format(locationKey, apiKey)
        response = urllib.request.urlopen(url)
        dailyForecast = json.loads(response.read())

        forecastToday = dailyForecast['DailyForecasts'][0]
        forecastTomorrow = dailyForecast['DailyForecasts'][1]

        today={}
        today['title'] = 'Today' 
        today['date'] = forecastToday['Date']
        today['high'] = forecastToday['Temperature']['Maximum']['Value'] #assumption?..
        today['icon'] = forecastToday['Day']['Icon']
        today['text'] = forecastToday['Day']['ShortPhrase']
        today['textLong'] = forecastToday['Day']['LongPhrase']
        today['precipitationProbability'] = forecastToday['Day']['PrecipitationProbability']
        today['wind'] = forecastToday['Day']['Wind']['Speed']['Value']

        tonight={}
        tonight['title'] = 'Tonight' 
        tonight['date'] = forecastToday['Date']
        tonight['low'] = forecastToday['Temperature']['Minimum']['Value'] #assumption?..
        tonight['icon'] = forecastToday['Night']['Icon']
        tonight['text'] = forecastToday['Night']['ShortPhrase']
        tonight['textLong'] = forecastToday['Night']['LongPhrase']
        tonight['precipitationProbability'] = forecastToday['Night']['PrecipitationProbability']
        tonight['wind'] = forecastToday['Night']['Wind']['Speed']['Value']

        tomorrow={}
        tomorrow['title'] = 'Tomorrow'
        tomorrow['date'] = forecastTomorrow['Date']
        tomorrow['high'] = forecastTomorrow['Temperature']['Maximum']['Value'] #assumption?..
        tomorrow['low'] = forecastTomorrow['Temperature']['Minimum']['Value'] #assumption?..
        tomorrow['icon'] = forecastTomorrow['Day']['Icon']
        tomorrow['text'] = forecastTomorrow['Day']['ShortPhrase']
        tomorrow['textLong'] = forecastTomorrow['Day']['LongPhrase']
        tomorrow['precipitationProbability'] = forecastTomorrow['Day']['PrecipitationProbability']
        tomorrow['wind'] = forecastTomorrow['Day']['Wind']['Speed']['Value']

        return (current, today, tonight, tomorrow)
    
    except Exception:
        return ()


def render(forecasts, output):
    fontTitle = ImageFont.truetype(fontFileBold, fontSizeLarge)
    fontTemperature = ImageFont.truetype(fontFileRegular, fontSizeTemperature)
    fontRegular = ImageFont.truetype(fontFileRegular, fontSizeRegular)

    image = Image.new('L', (imageWidth, imageHeight), colorGray3)
    imageDraw = ImageDraw.Draw(image)

    if len(forecasts) == 0:
        sectionWidth = imageWidth - offsetX * 2
        sectionHeight = imageHeight - offsetY * 2

        section = Image.new('L', (sectionWidth, sectionHeight), colorBackground)
        sectionDraw = ImageDraw.Draw(section)

        text = 'No weather forecast...'
        textWidth, textHeight = fontTitle.getsize(text)
        # textOffsetX, textOffsetY = fontTitle.getoffset(text)
        sectionDraw.text((sectionWidth / 2 - textWidth / 2, sectionHeight / 2 - textHeight / 2), text, fill=colorBlack, font=fontTitle)
        
        image.paste(section, (offsetX, offsetY))

        # image = image.transpose(Image.ROTATE_90)
        image.save(output, 'PNG')

        return

    sectionWidth = int((imageWidth - offsetX * 2 - spacerWidth * (maxSections - 1)) / maxSections)
    sectionHeight = imageHeight - offsetY * 2

    drawWidth = sectionWidth - (marginXstart + marginXend)

    for i in range(min(maxSections, len(forecasts))):
        forecast = forecasts[i]

        section = Image.new('L', (sectionWidth, sectionHeight), colorBackground)
        sectionDraw = ImageDraw.Draw(section)
        x, y = (marginXstart, marginY + 3)

        text = forecast['title']
        textWidth, textHeight = fontTitle.getsize(text)
        # textOffsetX, textOffsetY = fontTitle.getoffset(text)
        sectionDraw.text((x, y), text, fill=colorBlack, font=fontTitle)

        y += fontSizeLarge + 4

        # "2019-10-03T00:00:00-04:00"
        date = datetime.datetime.strptime(re.sub(r'(.*)([-,+][0-9]{2}):([0-9]{2})', r'\1\2\3', forecast['date']), '%Y-%m-%dT%H:%M:%S%z')
        text = date.strftime('%b %d, %a')        
        textWidth, textHeight = fontRegular.getsize(text)
        # textOffsetX, textOffsetY = font.getoffset(text)
        sectionDraw.text((x, y), text, fill=colorBlack, font=fontRegular)

        y += fontSizeRegular + 15

        icon = Image.open('{0}/accuweather_icon{1}.png'.format(config.iconsDir, forecast['icon']))
        icon = icon.resize((iconWidth, iconHeight), Image.LANCZOS)
        section.paste(icon, (x, y))

        y += iconHeight + 20

        high = forecast.get('high', None)
        low = forecast.get('low', None)
        temperature = forecast.get('temperature', None)

        text2 = ''
        if (high != None) and (low != None):
            text = '{0}°'.format(int(high + 0.5))
            text2 = '/{0}°'.format(int(low + 0.5))

        else:
            text = '{0}°'.format(int(high + 0.5) if high != None else (int(low + 0.5) if low != None else int(temperature + 0.5)))
            text2 = 'Hi' if high != None else ('Lo' if low != None else '')

        textWidth, textHeight = fontTemperature.getsize(text)
        # textOffsetX, textOffsetY = fontTemperature.getoffset(text)
        text2Width, text2Height = fontRegular.getsize(text2)
        # text2OffsetX, text2OffsetY = font.getoffset(text2)

        sectionDraw.text((x, y), text, fill=colorBlack, font=fontTemperature)
        sectionDraw.text((x + textWidth - 5, y + textHeight - text2Height), text2, fill=colorGray1, font=fontRegular)

        y += fontSizeTemperature + 5

        text = '{0} km/h'.format(forecast.get('wind'))

        textWidth, textHeight = fontRegular.getsize(text)
        # textOffsetX, textOffsetY = font.getoffset(text)
        sectionDraw.text((x, y), text, fill=colorGray1, font=fontRegular)

        y += fontSizeRegular + 15

        text = forecast.get('text')

        spaceWidth, spaceHeight = fontRegular.getsize(' ')
        for word in text.split(' '):
            textWidth, textHeight = fontRegular.getsize(word)
            # textOffsetX, textOffsetY = font.getoffset(word)
            
            if (x != marginXstart) and ((x + textWidth) > drawWidth):
                x = marginXstart
                y += textHeight + 2

            sectionDraw.text((x, y), word, fill=colorBlack, font=fontRegular)

            if (x + textWidth + spaceWidth) <= drawWidth:
                x += textWidth + spaceWidth

            else:
                x = marginXstart
                y += textHeight + 2

        image.paste(section, (offsetX + sectionWidth * i + spacerWidth * i, offsetY))

    for i in range(1, min(maxSections, len(forecasts))):
        startX = offsetX + sectionWidth * i + spacerWidth * (i - 1)
        startY = offsetY
        imageDraw.rectangle([(startX, startY), (startX + spacerWidth, startY + sectionHeight)], fill=colorGray2)

    # image = image.transpose(Image.ROTATE_90)
    image.save(output, 'PNG')

lastForecastUpdate = None
lastForecastRender = None 

def prepareWeatherForecast(output, cachePeriod = datetime.timedelta(hours=1)):
    global lastForecastUpdate
    global lastForecastRender
    
    if (lastForecastUpdate == None) or ((datetime.datetime.now() - lastForecastUpdate) >= cachePeriod):
        lastForecastUpdate = datetime.datetime.now()
        lastForecastRender = BytesIO()

        forecasts = getForecasts()
        render(forecasts, lastForecastRender)

    lastForecastRender.seek(0)
    shutil.copyfileobj(lastForecastRender, output)


def main():
    os.makedirs(config.outputDir, exist_ok=True)
    prepareWeatherForecast(config.outputDir + '/weather.png')


if __name__ == '__main__':
   main()
