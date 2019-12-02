#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from PIL import Image, ImageDraw, ImageFont

scriptDir = sys.path[0] #os.path.dirname(os.path.realpath(__file__))
outputDir = scriptDir + "/../images/"
fontsDir = scriptDir + '/../resources/fonts/'


def getImageFileName(hour, minute):
    return "%02d_%02d.png" % (hour, minute)


fontFile = fontsDir + 'RubikMonoOne-Regular.ttf'

imageWidth, imageHeight = (800 * 10, 600 * 10)
offsetX, offsetY = (40 * 10, 5 * 10)

#exteriorWidth = 6 * 10
#majorWidth = 6 * 10
#majorLength = 40 * 10
#minorWidth = 2 * 10
#minorLength = 30 * 10

exteriorWidth = 0 * 10
majorWidth = 8 * 10
majorLength = 33 * 10
minorWidth = 2 * 10
minorLength = 15 * 10

spacing = 5 * 10

colorBackground = "white"
colorForeground = "black"
colorHour = "grey"
colorMinute = "black"
colorTransparent = (255,255,255,0)

centerX = (imageWidth - offsetX * 2) / 2
centerY = (imageHeight - offsetY * 2) / 2
radius = min(centerX - offsetX, centerY - offsetY)

# handHourLegth = radius * 0.65
# handHourWidth = 15 * 10
# handMinuteLegth = radius - exteriorWidth - spacing * 2 - majorLength
# handMinuteWidth = 7 * 10
# handLengthExtend = 0.33
# handHoleRadius = 5 * 10

handHourLegth = radius * 0.65
handHourWidth = 16 * 10
handMinuteLegth = radius - exteriorWidth - spacing * 2 - majorLength
handMinuteWidth = 8 * 10
handLengthExtend = 0.33
handHoleRadius = 5 * 10

def render():
    image = Image.new('RGBA', (imageWidth, imageHeight), colorBackground)
    draw = ImageDraw.Draw(image)
    #draw.arc([(offsetX + centerX - radius, offsetY + centerY - radius), (offsetX + centerX + radius, offsetY + centerY + radius)], start=0, end=360, fill=colorForeground, width=exteriorWidth)

    minutes = Image.new('RGBA', (minorWidth, int(radius * 2 - exteriorWidth * 2 - spacing * 2)), colorTransparent)
    minutesDraw = ImageDraw.Draw(minutes)
    minutesDraw.rectangle([(0, 0), (minutes.width, minorLength)], fill=colorForeground)
    minutesDraw.rectangle([(0, minutes.height - minorLength), (minutes.width, minutes.height)], fill=colorForeground)

    for i in range(60):
        minutesRotated = minutes.rotate(6 * i, resample=Image.BILINEAR, expand=True, fillcolor=colorTransparent)
        image.alpha_composite(minutesRotated, (offsetX + int(centerX - minutesRotated.width / 2), offsetY + int(centerY - minutesRotated.height / 2)))
    
    hours = Image.new('RGBA', (majorWidth, int(radius * 2 - exteriorWidth * 2 - spacing * 2)), colorTransparent)
    hoursDraw = ImageDraw.Draw(hours)
    hoursDraw.rectangle([(0, 0), (hours.width, majorLength)], fill=colorForeground)
    hoursDraw.rectangle([(0, hours.height - majorLength), (hours.width, hours.height)], fill=colorForeground)

    for i in range(6):
        hoursRotated = hours.rotate(30 * i, resample=Image.BILINEAR, expand=True, fillcolor=colorTransparent)
        image.alpha_composite(hoursRotated, (offsetX + int(centerX - hoursRotated.width / 2), offsetY + int(centerY - hoursRotated.height / 2)))

    handHour = Image.new('RGBA', (int(handHourWidth * 2 + handHoleRadius * 2), int(handHourLegth * 2)), colorTransparent)
    handHourDraw = ImageDraw.Draw(handHour)
    handHourDraw.rectangle([((handHour.width - handHourWidth) / 2, 0), (((handHour.width - handHourWidth) / 2) + handHourWidth, handHourLegth * (1 + handLengthExtend))], fill=colorHour)
    handHourDraw.pieslice([(0, handHourLegth - handHoleRadius - handHourWidth), (handHour.width, handHourLegth + handHoleRadius + handHourWidth)], start=0, end=360, fill=colorHour)
    handHourDraw.pieslice([(handHour.width / 2 - handHoleRadius, handHourLegth - handHoleRadius), (handHour.width / 2 + handHoleRadius, handHourLegth + handHoleRadius)], start=0, end=360, fill=colorBackground)

    handMinute = Image.new('RGBA', (int(handMinuteWidth * 2 + handHoleRadius * 2), int(handMinuteLegth * 2)), colorTransparent)
    handMinuteDraw = ImageDraw.Draw(handMinute)
    handMinuteDraw.rectangle([((handMinute.width - handMinuteWidth) / 2, 0), (((handMinute.width - handMinuteWidth) / 2) + handMinuteWidth, handMinuteLegth * (1 + handLengthExtend))], fill=colorMinute)
    handMinuteDraw.pieslice([(0, handMinuteLegth - handHoleRadius - handMinuteWidth), (handMinute.width, handMinuteLegth + handHoleRadius + handMinuteWidth)], start=0, end=360, fill=colorMinute)
    handMinuteDraw.pieslice([(handMinute.width / 2 - handHoleRadius, handMinuteLegth - handHoleRadius), (handMinute.width / 2 + handHoleRadius, handMinuteLegth + handHoleRadius)], start=0, end=360, fill=colorBackground)


    for hour in range(12):
        for minute in range(60):
            imageCopy = image.copy()

            handHourRotated = handHour.rotate(- (30 * hour + 30 * (minute / 60)), resample=Image.BILINEAR, expand=True, fillcolor=colorTransparent)
            handMinuteRotated = handMinute.rotate(- (6 * minute), resample=Image.BILINEAR, expand=True, fillcolor=colorTransparent)

            imageCopy.alpha_composite(handHourRotated, (offsetX + int(centerX - handHourRotated.width / 2), offsetY + int(centerY - handHourRotated.height / 2)))
            imageCopy.alpha_composite(handMinuteRotated, (offsetX + int(centerX - handMinuteRotated.width / 2), offsetY + int(centerY - handMinuteRotated.height / 2)))

            imageCopy = imageCopy.resize((800, 600), resample=Image.BICUBIC) #LANCZOS)
            imageCopy = imageCopy.convert(mode='L')
            imageCopy = imageCopy.transpose(Image.ROTATE_90)
            imageCopy.save(outputDir + getImageFileName(hour, minute))
            imageCopy.save(outputDir + getImageFileName(hour + 12, minute))


def main():
    os.makedirs(outputDir, exist_ok=True)
    render()

if __name__ == '__main__':
   main()
