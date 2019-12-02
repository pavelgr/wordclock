#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from PIL import Image, ImageDraw, ImageFont

import config

def prepareImage(input, output, size = (800, 600)):
    outputWidth, outputHeight = size
    aspectRatio = float(outputWidth / float(outputHeight))

    image = Image.open(input)
    format = image.format
    imageWidth, imageHeight = image.size
    imageAspectRatio = float(imageWidth / float(imageHeight))
    
    if (imageAspectRatio != aspectRatio):
        cropWidth, cropHeight = (0, 0)
        offsetX, offsetY = (0, 0)

        if (imageAspectRatio > aspectRatio):
            cropWidth, cropHeight = (int(imageHeight * aspectRatio),  imageHeight)
            offsetX, offsetY = (int((imageWidth - cropWidth) / 2), 0)

        else:
            cropWidth, cropHeight = (imageWidth,  int(imageWidth / aspectRatio))
            offsetX, offsetY = (0, int((imageHeight - cropHeight) * 0.3))

        image = image.crop((offsetX, offsetY, offsetX + cropWidth, offsetY + cropHeight))
        imageWidth, imageHeight = image.size
        imageAspectRatio = aspectRatio

    if ((imageWidth, imageHeight) != size):
        image = image.resize(size, Image.LANCZOS) #Image.BICUBIC

    if (image.mode != 'L'):
        image = image.convert('L')

    # image = image.transpose(Image.ROTATE_90)
    image.save(output, format)


def rotateImage(input, output):
    image = Image.open(input)
    format = image.format

    image = image.transpose(Image.ROTATE_90)
    image.save(output, format)


# result = subprocess.run('convert -quality 100 -size 700x -background white -font'.split(' ') + [config.fontsDir + 'RobotoMono-Bold.ttf'] + '-pointsize 25 -fill black -gravity NorthWest'.split(' ') + ['caption:{0}'.format(update.message.text)] + '-trim -gravity center -extent 800x600 -set colorspace Gray -separate -average -rotate -90'.split(' ') + [outputImagePath]).returncode
# if result != 0:
#     raise Exception('failed to convert text: {0}'.format(update.message.text))

def renderText(text, output, size = (800, 600)):
    imageWidth, imageHeight = size
    # marginX, marginY = (40, 40)

    colorBackground = 'white'
    colorBlack = 'black'

    fontFileRegular = config.fontsDir + 'LiberationSans-Bold.ttf'
    fontSizeRegular = 22
    fontRegular = ImageFont.truetype(fontFileRegular, fontSizeRegular)

    image = Image.new('L', (imageWidth, imageHeight), colorBackground)
    imageDraw = ImageDraw.Draw(image)

    textWidth, textHeight = fontRegular.getsize(text)
    # textOffsetX, textOffsetY = fontRegular.getoffset(text)
    imageDraw.text(((imageWidth - textWidth) / 2, (imageHeight - textHeight) / 2), text, fill=colorBlack, font=fontRegular)
    
    # spaceWidth, spaceHeight = fontRegular.getsize(' ')
    # for word in text.split(' '):
    #     textWidth, textHeight = fontRegular.getsize(word)
    #     # textOffsetX, textOffsetY = font.getoffset(word)
        
    #     if (x != marginXstart) and ((x + textWidth) > drawWidth):
    #         x = marginXstart
    #         y += textHeight + 2

    #     sectionDraw.text((x, y), word, fill=colorBlack, font=fontRegular)

    #     if (x + textWidth + spaceWidth) <= drawWidth:
    #         x += textWidth + spaceWidth

    #     else:
    #         x = marginXstart
    #         y += textHeight + 2

    # image = image.transpose(Image.ROTATE_90)
    image.save(output, 'PNG')
