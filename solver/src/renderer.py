import os
import sys
from PIL import Image, ImageDraw, ImageFont

scriptDir = sys.path[0] #os.path.dirname(os.path.realpath(__file__))
outputDir = scriptDir + "/../images/"
fontsDir = scriptDir + '/../resources/fonts/'

fontFile = fontsDir + 'RubikMonoOne-Regular.ttf'

imageWidth, imageHeight = (800, 600)
offsetX, offsetY = (40, 10)
spacingX, spacingY = (0, 0)
letterPaddingLeft, letterPaddingRight = (0, 0)
#letterPaddingLeft, letterPaddingRight = (3, 1)

colorBackground = "white"
colorText = "lightgrey"
colorTextSelected = "black"

itis = ("it is",)
# minutes1 = ("ten", "eleven", "twelve", "thirteen", "fourteen", "quarter", "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "half")
# minutes2 = ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
# topast = ("to", "past")
# hours = ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "noon", "midnight")
oclock = ("o'clock",)
inthe = ("in the",)
# when = ("morning", "afternoon")

minutesValuesWords = tuple(["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "quarter", "sixteen", "seventeen", "eighteen", "nineteen", "twenty"] + [("twenty", i) for i in ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]] + ["half"])
topastValuesWords = ("to", "past")
hoursValuesWords = ("midnight", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "noon", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven")
whenValuesWords = ("morning", "afternoon")

#['it is teneleven', 'twelvethirteen', 'fourteenquarter', 'sixteenseventeen', 'eighteennineteen', 'twentyhalf one', 'twothreefourfive', 'sixseveneight', 'nine topast one', 'twothreefourfive', 'sixseveneight', 'nineteneleven', 'noonmidnight ', 'oclock in the ', 'morningafternoon']
solvedWords = ("it is teneleven ", "twelve thirteen ", "fourteen quarter", "sixteenseventeen", "eighteennineteen", "twenty half one ", "twothreefourfive", "six seven eight ", "nine to past one", "twothreefourfive", "six seven eight ", "nine ten eleven ", "noon    midnight", "o'clock in the  ", "morningafternoon")
fillerLetters = "qwertyuiopasdfghjklzxcvbnm".upper()

bitmapFont = ((
(0,1,1,1,0),(1,0,0,1,1),(1,0,1,0,1),(1,0,1,0,1),(1,1,0,0,1),(0,1,1,1,0),
),(
(0,0,1,0,0),(0,1,1,0,0),(1,0,1,0,0),(0,0,1,0,0),(0,0,1,0,0),(1,1,1,1,1),
),(
(0,1,1,1,0),(1,0,0,0,1),(0,0,0,0,1),(0,1,1,1,0),(1,0,0,0,0),(1,1,1,1,1),
),(
(0,1,1,1,0),(1,0,0,0,1),(0,0,1,1,0),(0,0,0,0,1),(1,0,0,0,1),(0,1,1,1,0),
),(
(0,0,0,1,0),(0,0,1,1,0),(0,1,0,1,0),(1,0,0,1,0),(1,1,1,1,1),(0,0,0,1,0),
),(
(1,1,1,1,1),(1,0,0,0,0),(1,1,1,1,0),(0,0,0,0,1),(1,0,0,0,1),(0,1,1,1,0),
),(
(0,0,1,1,0),(0,1,0,0,0),(1,1,1,1,0),(1,0,0,0,1),(1,0,0,0,1),(0,1,1,1,0),
),(
(1,1,1,1,1),(0,0,0,0,1),(0,0,0,1,0),(0,0,1,0,0),(0,1,0,0,0),(0,1,0,0,0),
),(
(0,1,1,1,0),(1,0,0,0,1),(0,1,1,1,0),(1,0,0,0,1),(1,0,0,0,1),(0,1,1,1,0),
),(
(0,1,1,1,0),(1,0,0,0,1),(1,0,0,0,1),(0,1,1,1,1),(0,0,0,0,1),(0,1,1,1,0),
),(
(0,0,0,1),(0,0,1,0),(0,0,1,0),(0,1,0,0),(0,1,0,0),(1,0,0,0),
),(
(0,0,0,0),(0,0,1,0),(0,0,1,0),(0,0,0,0),(0,0,1,0),(0,0,1,0),
),(
(0,1,1,0),(1,0,0,1),(1,0,0,1),(0,1,1,0),(0,0,0,0),(0,0,0,0),
),(
(0,0,0,0),(0,0,0,0),(0,0,0,0),(1,1,1,0),(0,0,0,0),(0,0,0,0),
))
characterMapping ={"0":0, "1":1, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "/":10, ":":11, "degree":12, "minus":13}

os.makedirs(outputDir, exist_ok=True)

def getTimeKey(hour, minute):
    return "%02d_%02d" % (hour, minute)

def filterWord(word, x):
    return x.find(word) >= 0

def filterWordMinutes(word, x):
    index = x.find(word)

    if index >= 0:
        if word.endswith("teen"):
            return True

        return (index != x.find(word + "teen")) and (index != x.find(word + "een"))

    return False

def filterWordHours(word, x):
    index = x.find(word)

    if index >= 0:
        if word != "noon":
            return True

        else:
            afternoonIndex = x.find("afternoon")
            if afternoonIndex < 0:
                return True

            return afternoonIndex + 5 != index

    return False

def getTimeToSolvedWords(solvedWords):
    timeToSolvedWords = {}

    solvedWordsReversed = list(solvedWords)
    solvedWordsReversed.reverse()
    solvedWordsReversed = tuple(solvedWordsReversed)

    for hour in range(24):
        for minute in range(60):
            hourIndex = (hour + (0 if (minute <= 30) else 1)) % len(hoursValuesWords)

            itisWord = itis[0]
            minuteWord = "none" if minute == 0 else (minutesValuesWords[minute - 1] if minute <= 30 else minutesValuesWords[59 - minute])
            topastWord = "none" if minute == 0 else topastValuesWords[1 if (minute <=  30) else 0]
            hourWord = hoursValuesWords[hourIndex]
            oclockWord = "none" if ((hourIndex == 0) or (hourIndex == 12)) else oclock[0]
            intheWord = "none" if ((hourIndex == 0) or (hourIndex == 12)) else inthe[0]
            whenWord = "none" if ((hourIndex == 0) or (hourIndex == 12)) else whenValuesWords[int(hourIndex / 12)]

            timeMapping = []
            
            minuteTuple = minuteWord if isinstance(minuteWord, tuple) else (minuteWord,)
            hourTuple = hourWord if isinstance(hourWord, tuple) else (hourWord,)
            words = (itisWord, minuteTuple, topastWord, hourTuple, oclockWord, intheWord, whenWord)
            words = tuple((i if isinstance(i, tuple) else (i,)) for i in words)
            
            # print(words)

            for wordTuple in words:
                for word in wordTuple:
                    filterFunction = filterWord

                    if wordTuple is minuteTuple:
                        filterFunction = filterWordMinutes

                    elif wordTuple is hourTuple:
                        filterFunction = filterWordHours

                    wordFilterList = list(filter(lambda x: (filterFunction(word, x)), solvedWords))

                    if len(wordFilterList) == 0:
                        continue

                    # print(wordFilterList)

                    try:
                        wordIndex = (len(solvedWordsReversed) - 1 - solvedWordsReversed.index(wordFilterList[-1])) if (wordTuple is hourTuple) else solvedWords.index(wordFilterList[0])
                        wordStart = letterPaddingLeft + solvedWords[wordIndex].find(word)
                        wordEnd = wordStart + len(word)

                        timeMapping.append((wordIndex, wordStart, wordEnd))
                    except ValueError:
                        pass

            # print(timeMapping)

            timeToSolvedWords[getTimeKey(hour, minute)] = tuple(timeMapping)

        # print(timeToSolvedWords)

    return timeToSolvedWords


def getIsSelectedSolvedWords(timeMapping, wordIndex, letterIndex):
    for mapping in timeMapping:
        if (mapping[0] == wordIndex) and (mapping[1] <= letterIndex) and (letterIndex < mapping[2]):
            return True

    return False


def getTimeToCharacters(characterMapping):
    timeToCharacters = {}

    for hour in range(24):
        for minute in range(60):
            hourCharacters = "%02d" % hour
            minuteCharacters = "%02d" % minute

            hourCharacters = ((3 + letterPaddingLeft, 1), tuple([bitmapFont[characterMapping[i]] for i in hourCharacters]))
            minuteCharacters = ((3 + letterPaddingLeft, 1 + 6 + 1), tuple([bitmapFont[characterMapping[i]] for i in minuteCharacters]))

            timeMapping = (hourCharacters, minuteCharacters)

            # print(timeMapping)

            timeToCharacters[getTimeKey(hour, minute)] = timeMapping

        # print(timeToSolvedWords)

    return timeToCharacters


def getIsSelectedCharacters(timeMapping, wordIndex, letterIndex):
    for mapping in timeMapping:
        offsetX, offsetY = mapping[0]

        if (offsetY <= wordIndex) and (wordIndex < (offsetY + 6)):
            spacingX = 0
            for character in mapping[1]:
                if ((offsetX + spacingX) <= letterIndex) and (letterIndex < (offsetX + spacingX + 5)):
                    if character[wordIndex - offsetY][letterIndex - (offsetX + spacingX)] == 1:
                        return True

                spacingX += (5 + 1)

    return False


def getImageFileName(hour, minute):
    return "%02d_%02d.png" % (hour, minute)

def render(words, mapping, getIsSelected):
    global spacingX

    fontSize = int((imageHeight - offsetY * 2 - spacingY * (len(words) - 1)) / float(len(words)))
    font = ImageFont.truetype(fontFile, fontSize)
    # w, h = draw.textsize(txt) # not that accurate in getting font size
    letterWidth, letterHeight = font.getsize("A")
    letterOffsetX, letterOffsetY = font.getoffset("A")
    spacingX = (imageWidth - offsetX * 2 - letterWidth * len(words[0])) / float(len(words[0]) - 1)

    adjustmentY = (imageHeight - offsetY * 2 - spacingY * (len(words) - 1) - letterHeight * len(words)) / float(2)  - letterOffsetY / float(2)

    filler = {}
    fillerIndex = 0

    for hour in range(24):
        for minute in range(60):
            timeMapping = mapping[getTimeKey(hour, minute)]

            image = Image.new('L', (imageWidth, imageHeight), colorBackground)
            draw = ImageDraw.Draw(image)

            x, y = (offsetX, offsetY + adjustmentY)
            for i in range(len(words)):
                word = words[i]

                for j in range(len(word)):
                    letter = word[j]
                    color = colorTextSelected if getIsSelected(timeMapping, i, j) else colorText

                    if letter == " ":
                        color = colorText

                        fillerKey = str(i) + ":" + str(j)
                        try:
                            letter = filler[fillerKey]
                        except KeyError:
                            letter = filler[fillerKey] = fillerLetters[fillerIndex]
                            fillerIndex = (fillerIndex + 1) % len(fillerLetters)

                    draw.text((x, y), letter, fill=color, font=font)
                    x += letterWidth + spacingX

                x = offsetX
                y += letterHeight + spacingY

            image = image.transpose(Image.ROTATE_90)
            image.save(outputDir + '/' + getImageFileName(hour, minute))


render(tuple([" " * letterPaddingLeft + i.upper() + " " * letterPaddingRight for i in solvedWords]), getTimeToSolvedWords(solvedWords), getIsSelectedSolvedWords)
# render(tuple([" " * letterPaddingLeft + i.upper() + " " * letterPaddingRight for i in solvedWords]), getTimeToCharacters(characterMapping), getIsSelectedCharacters)

# 10001
# 01100
# 01010
# 01010
# 00110
# 10001

# 11011
# 10011
# 01011
# 11011
# 11011
# 00000

# 10001
# 01110
# 11110
# 10001
# 01111
# 00000

# 10001
# 01110
# 11001
# 11110
# 01110
# 10001

# 11101
# 11001
# 10101
# 01101
# 00000
# 11101

# 00000
# 01111
# 00001
# 11110
# 01110
# 10001

# 11001
# 10111
# 00001
# 01110
# 01110
# 10001

# 00000
# 11110
# 11101
# 11011
# 10111
# 10111

# 10001
# 01110
# 10001
# 01110
# 01110
# 10001

# 10001
# 01110
# 01110
# 10000
# 11110
# 10001

# 1110
# 1101
# 1101
# 1011
# 1011
# 0111

# 1111
# 1101
# 1101
# 1111
# 1101
# 1101

# 1001
# 0110
# 0110
# 1001
# 1111
# 1111

# 1111
# 1111
# 1111
# 0001
# 1111
# 1111
