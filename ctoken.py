import re
from collections import defaultdict
# from nltk.stem import SnowballStemmer
# from nltk.corpus import stopwords

# @ and $ are excluded from TABLE because they add important context to numbers and email addresses, respectively
# replace_string = "\n\t\r^_`{|}~?<=>*+#%!;:/[]\'\",()_”“‘’\\"
replace_string = "\n\t\r^_`{|}~?<=>*+#%!;:/[]\'\",()_”“‘’\\&$"
TABLE2 = str.maketrans(replace_string, " "*len(replace_string))
TABLE_NOSPACE = str.maketrans("", "", "-")
# stemmer = SnowballStemmer("english")
# STOPWORDS = set(stopwords.words('english'))
NO_NUMERIC = False

def tokenize(line: str, trim_stopwords=False) -> list:
    tokenlist = list()
    line = re.sub(r"\. ", ' ', line) # strips periods at the end of sentences
    for word in line.lower().translate(TABLE2).split():
        # lower:O(N) + translate:O(N) + split:O(N) + forloop:O(N) = O(4N) = O(N)
        try:
            word = word.strip(".@").translate(TABLE_NOSPACE)
            if word != '':
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