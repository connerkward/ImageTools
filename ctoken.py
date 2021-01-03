import re
from collections import defaultdict
# from nltk.stem import SnowballStemmer
STOPWORDS = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll",
             "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's",
             'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
             'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was',
             'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an',
             'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with',
             'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to',
             'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
             'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most',
             'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
             's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o',
             're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't",
             'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't",
             'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't",
             'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"}

# @ and $ are excluded from TABLE because they add important context to numbers and email addresses, respectively
# replace_string = "\n\t\r^_`{|}~?<=>*+#%!;:/[]\'\",()_”“‘’\\"
replace_string = "\n\t\r^_`{|}~?<=>*+#%!;:/[]\'\",()_”“‘’\\&$"
TABLE2 = str.maketrans(replace_string, " "*len(replace_string))
TABLE_NOSPACE = str.maketrans("", "", "-")
# stemmer = SnowballStemmer("english")
NO_NUMERIC = True

def tokenize(line: str, trim_stopwords=False) -> list:
    tokenlist = list()
    line = re.sub(r"\. ", ' ', line) # strips periods at the end of sentences
    for word in line.lower().translate(TABLE2).split():
        # lower:O(N) + translate:O(N) + split:O(N) + forloop:O(N) = O(4N) = O(N)
        try:
            word = word.strip(".@").translate(TABLE_NOSPACE)
            if word == '' or len(word) < 2 or word in STOPWORDS:
                pass
            else:
                if NO_NUMERIC and any(map(str.isdigit, word)):
                    pass
                else:
                    # tokenlist.append(word.encode("ascii").decode())
                    tokenlist.append(word.encode("ascii").decode())
        except UnicodeEncodeError:  # for handling bad characters in word
            pass
    return tokenlist

if __name__ == '__main__':
    stri= "master of software engineering"
    print(tokenize(stri))