import emotionLexicon

import pandas
from matplotlib import pyplot

vaderAccuracyOriginal = emotionLexicon.algorithmVaderData("original")
vaderAccuracyPreprocessed = emotionLexicon.algorithmVaderData("preprocessed")

data = {"Vader": ["original", "preprocessed"], "probabilities": [vaderAccuracyOriginal, vaderAccuracyPreprocessed]}
dataframe = pandas.DataFrame(data=data)
dataframe.plot(kind="bar", x ="Vader", y = "probabilities", color="blue")
pyplot.xticks(rotation=0)
pyplot.savefig("vader-output.png")