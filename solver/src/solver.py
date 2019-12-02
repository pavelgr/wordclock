#!/usr/loca/bin/python3

#['it is teneleven', 'twelvethirteen', 'fourteenquarter', 'sixteenseventeen', 'eighteennineteen', 'twentyhalf one', 'twothreefourfive', 'sixseveneight', 'nine topast one', 'twothreefourfive', 'sixseveneight', 'nineteneleven', 'noonmidnight ', 'oclock in the ', 'morningafternoon']
#['it is twenty one', 'twothreefourfive', 'sixseveneight', 'nineteneleven', 'twelvethirteen', 'fourteenquarter', 'sixteenseventeen', 'eighteennineteen', 'half topast one', 'twothreefourfive', 'sixseveneight', 'nineteneleven', 'noonmidnight ', 'oclock in the ', 'morningafternoon']

itis = ("it is",)
# itis = ("it is twenty",)
# minutes1 = ("twenty", "quarter", "half", "ten", "eleven", "twelve", "thirteen", "fourteen", "sixteen", "seventeen", "eighteen", "nineteen")
minutes1 = ("ten", "eleven", "twelve", "thirteen", "fourteen", "quarter", "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "half")
minutes2 = ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
# minutes = ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "quarter", "sixteen", "seventeen", "eighteen", "nineteen", "half")
# minutes = ("five", "ten", "quarter", "half")
topast = ("to", "past")
hours = ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "noon", "midnight")
# hours = ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve")
oclock = ("oclock",)
inthe = ("in the",)
# when = ("morning", "evening", "at night")
when = ("morning", "afternoon")

lineLength = 16
words = (itis, minutes1, minutes2, topast, hours, oclock, inthe, when)
# words = (itis, minutes, topast, hours, oclock, inthe, when)
wordsLength = []

def prepare():
    for i in range(len(words)):
        wordsSetLength = []
        for j in range(len(words[i])):
            wordsSetLength.append(len(words[i][j]))

        wordsLength.append(wordsSetLength)

    print(str(wordsLength))


def getMemoKey(wordsLengthSelected):
    for i in range(len(wordsLengthSelected)):
        wordsLengthSelected[i].sort()
    
    return str(wordsLengthSelected)


def solvePart(words, wordsLength, wordsLengthSelected, wordsSelectedIndices, memo, result):
    # print(">>solvePart: wordsSelectedIndices: %s" % (str(wordsSelectedIndices)))

    nextIndices = [-1] * len(words)
    while True:
        hasSlice = False

        for i in range(len(words)):
            wordsSet = words[i]

            if (nextIndices[i] < len(wordsSet)) and (len(wordsSelectedIndices[i]) < len(wordsSet)):
                prevIndex = nextIndices[i]
                for j in range(nextIndices[i] + 1, len(wordsSet)):
                    if j not in wordsSelectedIndices[i]:
                        nextIndices[i] = j
                        hasSlice = True

                        break
                
                if prevIndex == nextIndices[i]:
                    nextIndices[i] = len(wordsSet)

        if not hasSlice:
            break

        nextWordsLengthSelected = []
        nextWordsSelectedIndices = []
        for i in range(len(words)):
            nextWordsLengthSelected.append(wordsLengthSelected[i][:])
            nextWordsSelectedIndices.append(wordsSelectedIndices[i][:])

        calculate = True

        for i in range(len(words)):
            if (nextIndices[i] >= 0) and (nextIndices[i] < len(words[i])):
                nextWordsLengthSelected[i].append(wordsLength[i][nextIndices[i]])
                nextWordsSelectedIndices[i].append(nextIndices[i])

            calculate &= (len(nextWordsSelectedIndices[i]) == len(words[i]))

        if calculate:
            lines = [""]

            for i in range(len(words)):
                nextWordsSetSelectedIndices = nextWordsSelectedIndices[i]

                for j in range(len(nextWordsSetSelectedIndices)):
                    lastLine = lines[len(lines) - 1]
                    if (len(lastLine) + wordsLength[i][nextWordsSetSelectedIndices[j]]) <= lineLength:
                        lines[len(lines) - 1] = lastLine + words[i][nextWordsSetSelectedIndices[j]]
                    else:
                        lines.append(words[i][nextWordsSetSelectedIndices[j]])
                
                lastLine = lines[len(lines) - 1]
                if len(lastLine) < lineLength:
                    lines[len(lines) - 1] = lastLine + " "

            if (result[0] == None) or (len(result[0]) > len(lines)):
                # print(str(wordsSelectedIndices))
                # print(str(nextIndices))
                # print(str(nextWordsSelectedIndices))
                print(str(lines))
                result[0] = lines

        else:
            key = getMemoKey(nextWordsLengthSelected)
            if key not in memo:
                solvePart(words, wordsLength, nextWordsLengthSelected, nextWordsSelectedIndices, memo, result)
                memo.append(key)

    # print("<<solvePart: wordsSelectedIndices: %s" % (str(wordsSelectedIndices)))



def solve():
    memo = []
    result = [None]

    nextIndices = [-1] * len(words)
    while True:
        hasSlice = False

        for i in range(len(words)):
            wordsSet = words[i]

            if nextIndices[i] < len(wordsSet):
                prevIndex = nextIndices[i]

                for j in range(nextIndices[i] + 1, len(wordsSet)):
                    nextIndices[i] = j
                    hasSlice = True
                    break

                if prevIndex == nextIndices[i]:
                    nextIndices[i] = len(wordsSet)

        if not hasSlice:
            break

        wordsLengthSelected = [[]] * len(words)
        wordsSelectedIndices = [[]] * len(words)

        for i in range(len(words)):
            if (nextIndices[i] >= 0) and (nextIndices[i] < len(words[i])):
                wordsLengthSelected[i] = [wordsLength[i][nextIndices[i]]]
                wordsSelectedIndices[i] = [nextIndices[i]]

        print("solve: wordsSelectedIndices: %s" % (str(wordsSelectedIndices)))

        solvePart(words, wordsLength, wordsLengthSelected, wordsSelectedIndices, memo, result)

    print(result[0])

prepare()
solve()


# lineLength = 16
# words = ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten")
# wordsLength = []


# def prepare():
#     for word in words:
#         wordsLength.append(len(word))


# def solvePart(words, wordsLength, wordsLengthSelected, wordsLengthSelectedIndices, lines, memo, result):
#     for index in range(len(wordsLength)):
#         if index not in wordsLengthSelectedIndices:
#             print("solvePart index: %d, selectedLengths: %s" % (index, str(wordsLengthSelectedIndices)))

#             nextWordsLengthSelected = wordsLengthSelected.copy()
#             nextWordsLengthSelectedIndices = wordsLengthSelectedIndices.copy()
#             nextLines = lines.copy()

#             nextWordsLengthSelected.append(wordsLength[index])
#             nextWordsLengthSelectedIndices.append(index)
#             lastLine = nextLines[len(nextLines) - 1]
#             if (len(lastLine) + wordsLength[index]) <= lineLength:
#                 nextLines[len(nextLines) - 1] = lastLine + words[index]
#             else:
#                 nextLines.append(words[index])

#             if (len(nextWordsLengthSelectedIndices) == len(wordsLength)):
#                 if (result[0] == None) or (len(result[0]) > len(nextLines)):
#                     print(str(nextLines))
#                     result[0] = nextLines
#             else:
#                 nextWordsLengthSelected.sort()
#                 key = str(nextWordsLengthSelected)
#                 if key not in memo:
#                     solvePart(words, wordsLength, nextWordsLengthSelected, nextWordsLengthSelectedIndices, nextLines, memo, result)
#                     memo.append(key)


# def solve():
#     memo = []
#     result = [None]

#     for index in range(len(wordsLength)):
#         print("solve index: %d" % index)

#         wordsLengthSelected = [wordsLength[index]]
#         wordsLengthSelectedIndices = [index]
#         lines = [words[index]]
#         solvePart(words, wordsLength, wordsLengthSelected, wordsLengthSelectedIndices, lines, memo, result)

#     print(result[0])

# prepare()
# solve()
