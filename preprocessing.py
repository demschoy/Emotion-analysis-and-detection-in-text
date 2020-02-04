import sys
sys.path.append("C:\\Users\\Lenovo\\Desktop\\FMI\\7 семестър\\Изкуствен интелект\\проект\\emotionDetection\\sms_slang_translator-master\\sms_slang_translator-master")

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

import emoji
import emot 

import Script

def loadFromFile(filename):
    with open(filename, "r", encoding="utf-8") as file:
        firstTurns = []
        secondTurns = []
        thirdTurns = []
        emotionClasses = []
        i = 0
        for line in file:
            if i == 0:
                i += 1
                continue
            else: 
                line = line.lower()
                splittedLine = line.split("\t")
                firstTurns.append(splittedLine[1])
                secondTurns.append(splittedLine[2])
                thirdTurns.append(splittedLine[3])
                if splittedLine[4].endswith('\n'):
                    splitted = splittedLine[4].split('\n')
                    emotionClasses.append(splitted[0])
                else:
                    emotionClasses.append(splittedLine[4])
            i += 1
        return (firstTurns, secondTurns, thirdTurns, emotionClasses)

def generateExamples(data):
    (first, second, third, classEmotion) = data 
    assert len(first) == len(second) == len(third) == len(classEmotion)
    size = len(first)
    examples = []
    for i in range(size):
        examples.append([first[i], second[i], third[i], classEmotion[i]])
    return examples

def generateNGrams(n, sentence):
    tokens = sentence.split(" ")
    ngramCollection = []
    size = len(tokens)
    for i in range(size):
        if i + n <= size:
            currentNGram = ' '.join(tokens[i:i+n])
            print(currentNGram)
            ngramCollection.append(currentNGram) 
    return ngramCollection

def generateNGramData(n, data):
    ngrams = []
    for example in data:
        exampleNgram = []        
        for i in range(3):
            exampleNgram.append(generateNGrams(n, example[i]))
        ngrams.append(exampleNgram)
    return ngrams

def removeStopWords(fromData):
    stopWords = set(stopwords.words('english'))
    size = len(fromData)
    filteredData = []
    for i in range(size):
        filteredExample = []
        for j in range(4):
            wordTokens = word_tokenize(fromData[i][j])
            filtered = []
            for word in wordTokens:
                if word not in stopWords:
                    filtered.append(word)
            filteredSentence = ' '.join(filtered)
            filteredExample.append(filteredSentence)
        filteredData.append(filteredExample)
    return filteredData

def isPunctuationMark(symbol):
    return ((ord(symbol) >= 33 and ord(symbol) <= 38) or (ord(symbol) >= 40 and ord(symbol) <= 47) or (ord(symbol) >= 59 and ord(symbol) <= 64) 
                or (ord(symbol) >= 91 and ord(symbol) <= 94) or ord(symbol) == 96  or (ord(symbol) >= 123 and ord(symbol) <= 126))

def handlePunctuation(sentence):
    transformed = ""
    for i in range(len(sentence)):
        if isPunctuationMark(sentence[i]):
            transformed += ""
        else:
            transformed += sentence[i]
    return transformed
                
def removePunctuation(data):
    for example in data:
        for i in range(3):
            example[i] = handlePunctuation(example[i])
    return data

def removeWhiteSpace(data):
    for example in data:
        for i in range(3):
            example[i] = ' '.join(example[i].split())
    return data

# probably not goint to be used
def extractEmoticonsFromText(sentence):
    emoticonList = []
    for word in sentence:
        for char in word:
            if char in emoji.UNICODE_EMOJI:
                emoticonList.append(word)
    return emoticonList

# probably not goint to be used
def extractEmoticons(data):
    emoticonList = []
    for example in data:
        for i in range(3):
            exampleList = extractEmoticonsFromText(example[i])
            if len(exampleList) > 0:
                for emoticon in exampleList:
                    emoticonList.append(emoticon)
    emoticon = set(emoticonList)
    return emoticon
    
def convertEmojisToText(data):
    for example in data:
        for i in range(3):
            example[i] = emoji.demojize(example[i], delimiters=(" ::",":: "))
    return data

def convertSymbolEmojisToText(data):
    for example in data:
        for i in range(3):
            emoticon = emot.emoticons(example[i])
            if isinstance(emoticon, list):
                continue
            if len(emoticon['value']) == 0:
                continue 
            value = ' '.join(emoticon['value'])
            meaning = ' ::'.join(emoticon['mean'])
            meaning += ':: '
            example[i] = example[i].replace(value, meaning.lower())
            example[i] = example[i].replace("-_-", " ::annoyed:: ")
            example[i] = example[i].replace(":))", " ::smiley_face:: ")
            example[i] = example[i].replace("(:", " ::smiley_face:: ")  
            example[i] = example[i].replace("=‑d", " ::laughing:: ")
            example[i] = example[i].replace(":d", " ::laughing:: ")
            example[i] = example[i].replace("*_*", " ::pleased:: ")
            example[i] = example[i].replace("^_^", " ::pleased:: ")
            example[i] = example[i].replace(";-)", " ::wink:: ")
            example[i] = example[i].replace("8)", " ::wearing_glasses:: ")
            example[i] = example[i].replace(":c", " ::sad:: ")
            example[i] = example[i].replace("xd", " ::laughing:: ")
    return data
    
def modifySlangFile():
    file = open(".\\sms_slang_translator-master\\sms_slang_translator-master\\slang.txt", "r") 
    fileNew = open(".\\sms_slang_translator-master\\sms_slang_translator-master\\slangModified.txt", "w", encoding="utf-8")
    for line in file:
        line = line.lower()
        fileNew.write(line)
    file.close()
    fileNew.close()
    
    oldFile = open(".\\sms_slang_translator-master\\sms_slang_translator-master\\slang.txt", "w", encoding="utf-8")
    oldFileNew = open(".\\sms_slang_translator-master\\sms_slang_translator-master\\slangModified.txt", "r")
    for line in oldFileNew:
        oldFile.write(line)
    oldFile.close()
    oldFileNew.close()      

def translateSlangWords(data):
    modifySlangFile()
    for example in data:
        for i in range(3):
            example[i] = Script.translator(example[i])
            example[i] = example[i].replace("'ve", " have")
            example[i] = example[i].replace("'m", " am")
            example[i] = example[i].replace(" m ", " am")
            example[i] = example[i].replace("n't", "not")
            example[i] = example[i].replace("'s", " is")
            example[i] = example[i].replace(":d", " ::laughing::")
            example[i] = example[i].replace("'r", " are")
            example[i] = example[i].replace("'re", " are")
            example[i] = example[i].replace("4", "for")
            example[i] = example[i].replace("'d", " would")
            example[i] = example[i].replace("'ll", " will")
            example[i] = example[i].replace("'l", " will")
    return data

def stemmingSentence(sentence):
    stemmedSentence = []
    tokenWords = word_tokenize(sentence)
    porter = PorterStemmer()
    for word in tokenWords:
        stemmedWord = porter.stem(word)
        stemmedSentence.append(stemmedWord)
    return ' '.join(stemmedSentence)
    
def stemming(data):
    for example in data:
        for i in range(3):
            example[i] = stemmingSentence(example[i])
    return data 
