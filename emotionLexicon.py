
import preprocessing

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.classify import NaiveBayesClassifier
from nltk.tokenize import word_tokenize

def loadPreprocessedData(filename):
    inputData = preprocessing.loadFromFile(filename)
    dataExamples = preprocessing.generateExamples(inputData)      
    emojis = preprocessing.convertEmojisToText(dataExamples)
    emoji = preprocessing.convertSymbolEmojisToText(emojis)
    transformedData = preprocessing.removePunctuation(emoji)
    withoutStopWords = preprocessing.removeStopWords(transformedData)    
    slanglessData = preprocessing.translateSlangWords(withoutStopWords)
    data = preprocessing.removeWhiteSpace(slanglessData)
    return data

def loadData(filename):
    inputData = preprocessing.loadFromFile(filename)
    dataExamples = preprocessing.generateExamples(inputData)  
    return dataExamples

def groupData(data):
    examples = []
    for example in data:
        dialogue = ""
        for i in range(3):
            dialogue += "".join(example[i])
            dialogue += "\t"
        pair = (dialogue, example[3])
        examples.append(pair)
    return examples

def dataOneVsAll(className, data, dictionary):
    train = []
    FICTION_CLASS = "FICTION_CLASS"
    for example in data:
        realDictionary = {}
        for word in dictionary:
            isContainingResult = word in word_tokenize(example[0])
            realDictionary.update({word: isContainingResult})
        if example[1] == className:
            pair = (realDictionary, example[1])
        else:
            pair = (realDictionary, FICTION_CLASS)
        train.append(pair)
    
    return train
    
# Vader and SentimenIntensityAnalyzer gives us whether the sentiment is positive, negative or neutral. Gonna use these result, assuming and matching positive for rather happy, 
# negative for rather angry or sad and neutral would be others
# Gonna be used for data that has been preprocessed and  one that has not to compare the results
# Using original data too, because Vader is very good when there is some emphasis on the text.
def loadDataDependingOnType(dataType):
    if dataType == "preprocessed":
        return loadData("./starterkitdata/train.txt")
    elif dataType == "original":
        return loadPreprocessedData("./starterkitdata/train.txt")

def classifyExample(dictionary):
    result = float(dictionary["compound"])
    if result >= 0.05:
        return "possitive"
    if result < 0.05 and result > -0.05:
        return "neutral"
    if result <= -0.05:
        return "negative"

def countCorrectExamples(data):
    correct = 0
    for line in data:
        result = clasаsifyExample(line[0])
        if result == "positive" and line[1] == "happy\n":
            correct += 1
        if result == "negative" and (line[1] == "angry\n" or line[1] == "sad\n"):
            correct += 1
        if result == "neutral" and line[1] == "others\n":
            correct += 1
    return correct

def storeData(name):
    data = []
    with open(name, "r", encoding="utf-8") as fileDoc:
        for line in fileDoc:
            parts = line.split(", ")
            dictionary = {}
            size = len(parts) - 1
            for part in parts[:size]:
                splitted = part.split(": ")
                dictionary.update({splitted[0]: splitted[1]})
            pair = (dictionary, parts[size])
            data.append(pair)
    return data
    
def algorithmVaderData(dataType):
    trainingData = loadDataDependingOnType(dataType)
        
    sentences = []
    for example in trainingData:
        dialogue = ""
        for i in range(3):
            dialogue += " ".join(example[i])
        pair = (dialogue, example[3])
        sentences.append(pair)
        
    analyzer = SentimentIntensityAnalyzer()
    name = dataType + "-vader-results.txt"    
    with open(name, "w", encoding="utf-8") as file:
        for sentence in sentences:
            polarityScores = analyzer.polarity_scores(sentence[0])
            for k in sorted(polarityScores):
                file.write('{0}: {1}, '.format(k, polarityScores[k]))
            file.write(sentence[1])
            file.write("\n")
            
    data = storeData(name)
    correct = countCorrectExamples(data)
    total = len(data)
    accuracy = correct / total    
    return accuracy
         
# Using preprocessed training and testing data for NBC
def naiveBayesAlgorithmPreData():
    training = loadPreprocessedData("./starterkitdata/train.txt")
    training = groupData(training)
    
    dictionary = set()
    for example in training:
        for word in word_tokenize(example[0]):
            dictionary.add(word)
    
    classes = ["happy", "sad", "angry", "others"]
    correct = 0
    for classEmotion in classes:
        print(classEmotion)
        trainData = dataOneVsAll(classEmotion, training, dictionary)
        classifier = NaiveBayesClassifier.train(trainData)
        testing = loadPreprocessedData("./starterkitdata/test.txt")
        testing = groupData(testing)
        for example in testing:
            data = {}
            for word in dictionary:
                isContainingResult = word in word_tokenize(example[0])
                data.update({word: isContainingResult})
            guessedClass = classifier.classify(data)
            if guessedClass == example[1]:
                correct += 1
    total = len(testing)
    accuracy = correct / total
    return accuracy