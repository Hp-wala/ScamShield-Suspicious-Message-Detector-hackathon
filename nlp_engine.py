# ==========================================================
# JARVIS AI
# NLP ENGINE
# Python 3.12
# ==========================================================

import re  # It is used to find, search, replace, or match text patterns.
import nltk  # it helps computers to understand human language. With nltk you can split sentences, split words, remove stop words, stem words, lemitization etc.
import pandas as pd #Python library used for working with tables and datasets.Read CSV files , Read Excel files, View datasets Filter data Analyze data 

from nltk.tokenize import (  #sent_tokenize() This function breaks a paragraph into sentences.
    sent_tokenize,  #Instead of importing the whole tokenization module, you import only the two functions you need
    word_tokenize
)


#It stores important settings in one place so you don't have to write them repeatedly in different files. Instead of writing the dataset path everywhere, you keep it in config.py and import it whenever needed.

from config import (  
    DATASET_PATH,
    NLTK_RESOURCES
)

# ==========================================================
# GLOBAL VARIABLES
# ==========================================================

data = None #Creates a variable named data. None means it is empty or no value is stored yet. Later, the dataset will be stored in this variable.

dataset_loaded = False   #Creates a variable named dataset_loaded. False means the dataset has not been loaded yet. After loading the dataset successfully, it will become True.


# ==========================================================
# DOWNLOAD NLTK RESOURCES
# ==========================================================

def initialize_nltk():   #We create this function so that all the NLTK setup happens in one place before the program starts using NLTK.

    print("=" * 60)   #These lines print a heading to show that the NLTK setup process has started. It makes the program output easier to read.
    print("Initializing NLTK...")
    print("=" * 60)

    for resource in NLTK_RESOURCES:  # for looops handels nltk resources seperately one by one

        try: #try tells Python to attempt running the code. If an error happens, the program won't crash immediately

            nltk.download(resource, quiet=True)   #This downloads the current NLTK resource so that NLTK functions (like tokenization) can work properly

            print(f"{resource} : OK") # If the download is successful, it prints OK so that the user get to know what is happening

        except Exception as e: # ode kiba error hoi program to jatatop hoi najie instead loop ot run hoi thaka

            print(f"{resource} : Failed") # These lines tell you which resource failed to download and display the error message.

            print(e)

    print("NLTK Ready.")  # These lines show that the initialization process has finished
    print("=" * 60)


# ==========================================================
# LOAD DATASET
# ==========================================================

def load_dataset():  # Loads the dataset into the program.

    global data  # Allows the function to update the global 'data' variable.
    global dataset_loaded  # Allows the function to update the global loading status.

    print("=" * 60)  # Prints a heading for better readability.
    print("Loading Dataset...")
    print("=" * 60)

    try:  # Tries to load the dataset. If an error occurs, the program won't crash.

        data = pd.read_csv(DATASET_PATH)  # Reads the CSV file and stores it in 'data'.

        print("Dataset Loaded Successfully.")  # Indicates that the dataset was loaded successfully.

    except Exception as e:  # Runs if any error occurs while loading the dataset.

        print("Dataset Loading Failed.")  # Indicates that the dataset could not be loaded.

        print(e)  # Displays the error message.

        return  # Stops the function because loading failed.

    dataset_loaded = True  # Marks the dataset as successfully loaded.# ==========================================================
# PREPARE DATASET
# ==========================================================

def prepare_dataset():  # Cleans and prepares the dataset for NLP processing.

    global data  # Allows the function to update the global 'data' variable.

    if data is None:  # Checks if the dataset has been loaded.

        return  # Stops the function if no dataset is available.

    try:  # Tries to organize the dataset columns.

        if len(data.columns) == 4:  # Checks if the dataset has exactly 4 columns.

            data.columns = [  # Assigns meaningful names to the columns.

                "ID",

                "Entity",

                "Sentiment",

                "Tweet"

            ]

    except:  # Runs if any error occurs while renaming the columns.

        pass  # Ignores the error and continues the program.

    if "Tweet" in data.columns:  # Checks if the 'Tweet' column exists.

        data.rename(

            columns={

                "Tweet": "Text"  # Renames 'Tweet' to 'Text' for consistency.

            },

            inplace=True  # Updates the original dataset directly.

        )

    if "Sentiment" in data.columns:  # Checks if the 'Sentiment' column exists.

        data["Sentiment"] = data["Sentiment"].replace({  # Converts text labels into numeric values.

            "Negative": 0,

            "Positive": 1,

            "Neutral": 2,

            "Irrelevant": 3

        })

    print("Dataset Prepared.")  # Indicates that the dataset is ready to use.
# ==========================================================
# SHOW DATASET INFO
# ==========================================================

def dataset_info():  # Displays basic information about the dataset.

    global data  # Allows the function to access the global 'data' variable.

    if data is None:  # Checks whether the dataset has been loaded.

        print("Dataset Not Loaded.")  # Informs the user that no dataset is available.

        return  # Stops the function because there is no dataset to display.

    print("=" * 60)  # Prints a heading for better readability.

    print("Dataset Information")

    print("=" * 60)

    print()

    print("Columns:")  # Displays the names of all columns.

    print(data.columns)

    print()

    print("Shape:")  # Displays the number of rows and columns.

    print(data.shape)

    print()

    print("First Five Rows")  # Displays the first five rows of the dataset.

    print(data.head())

    print()

    print("Unique Sentiments")  # Displays all unique sentiment values.

    if "Sentiment" in data.columns:  # Checks if the 'Sentiment' column exists.

        print(

            data["Sentiment"].unique()  # Displays unique values from the Sentiment column.

        )

    print("=" * 60)  # Marks the end of the dataset information.

# ==========================================================
# LOWERCASE
# ==========================================================

def lowercase(text):  # Converts all characters in the text to lowercase.

    return str(text).lower()  # Converts the input to a string, then changes it to lowercase.

# ==========================================================
# REMOVE URL
# ==========================================================

def remove_url(text):  # Removes URLs (website links) from the text.

    text = str(text)  # Converts the input into a string.

    url_pattern = re.compile(  # Creates a pattern to identify URLs.

        r"https?://\S+|www\.\S+"

    )

    return url_pattern.sub("", text)  # Replaces all URLs with an empty string.

# ==========================================================
# REMOVE EXTRA SPACES
# ==========================================================

def remove_extra_spaces(text):  # Removes extra spaces from the text.

    text = str(text)  # Converts the input into a string.

    return " ".join(text.split())  # Removes extra spaces and keeps only a single space between words.


# ==========================================================
# REMOVE SPECIAL CHARACTERS
# ==========================================================

def remove_special_characters(text):

    text = str(text)

    text = re.sub(

        r"[^a-zA-Z0-9\s]",

        "",

        text

    )

    return text

# ==========================================================
# CLEAN TEXT
# ==========================================================

def clean_text(text):

    text = lowercase(text)

    text = remove_url(text)

    text = remove_special_characters(text)

    text = remove_extra_spaces(text)

    return text.strip()


# ==========================================================
# SENTENCE TOKENIZATION
# ==========================================================

def sentence_tokenize(text):

    text = clean_text(text)

    return sent_tokenize(text)


# ==========================================================
# WORD TOKENIZATION
# ==========================================================

def word_tokenize_text(text):

    text = clean_text(text)

    return word_tokenize(text)


# ==========================================================
# COMPLETE PREPROCESSING PIPELINE
# ==========================================================

def preprocess_text(text):

    cleaned = clean_text(text)

    sentences = sentence_tokenize(cleaned)

    words = word_tokenize_text(cleaned)

    return {

        "original": text,

        "cleaned": cleaned,

        "sentences": sentences,

        "words": words,

        "total_sentences": len(sentences),

        "total_words": len(words)

    }


# ==========================================================
# SEARCH DATASET
# ==========================================================

def search_dataset(keyword):

    global data

    if data is None:

        print("Dataset not loaded.")

        return pd.DataFrame()

    keyword = str(keyword).lower()

    results = data[

        data["Text"]

        .astype(str)

        .str.lower()

        .str.contains(

            keyword,

            na=False

        )

    ]

    return results


# ==========================================================
# GET RANDOM TWEETS
# ==========================================================

def random_tweets(count=5):

    global data

    if data is None:

        return pd.DataFrame()

    count = min(count, len(data))

    return data.sample(count)


# ==========================================================
# GET TWEETS BY SENTIMENT
# ==========================================================

def tweets_by_sentiment(sentiment):

    global data

    if data is None:

        return pd.DataFrame()

    return data[

        data["Sentiment"] == sentiment

    ]


# ==========================================================
# GET DATASET COLUMNS
# ==========================================================

def get_columns():

    global data

    if data is None:

        return []

    return list(data.columns)


# ==========================================================
# GET DATASET SHAPE
# ==========================================================

def get_shape():

    global data

    if data is None:

        return (0, 0)

    return data.shape


# ==========================================================
# GET FIRST ROWS
# ==========================================================

def first_rows(rows=5):

    global data

    if data is None:

        return pd.DataFrame()

    return data.head(rows)
# ==========================================================
# DATASET STATISTICS
# ==========================================================

def dataset_statistics():

    global data

    if data is None:

        print("Dataset not loaded.")
        return

    print("=" * 60)
    print("DATASET STATISTICS")
    print("=" * 60)

    print(f"Rows    : {data.shape[0]}")
    print(f"Columns : {data.shape[1]}")

    print("\nColumn Names:")

    for column in data.columns:

        print(f"- {column}")

    if "Sentiment" in data.columns:

        print("\nSentiment Counts:")

        print(data["Sentiment"].value_counts())

    print("=" * 60)


# ==========================================================
# PROCESS COMPLETE DATASET
# ==========================================================

def preprocess_dataset():

    global data

    if data is None:

        return

    print("Cleaning Dataset...")

    data["Text"] = (

        data["Text"]

        .astype(str)

        .apply(clean_text)

    )

    print("Dataset Cleaned Successfully.")


# ==========================================================
# GET DATASET
# ==========================================================

def get_dataset():

    global data

    return data


# ==========================================================
# INITIALIZE NLP ENGINE
# ==========================================================

def initialize_nlp():

    initialize_nltk()

    load_dataset()

    prepare_dataset()

    preprocess_dataset()

    print("NLP Engine Ready.")


# ==========================================================
# TEST FUNCTIONS
# ==========================================================

def test():

    initialize_nlp()

    dataset_info()

    dataset_statistics()

    sample = (
        "Hello!! Visit https://google.com "
        "I am learning NLP with Jarvis."
    )

    print("\nOriginal Text:")
    print(sample)

    print("\nClean Text:")
    print(clean_text(sample))

    print("\nSentence Tokenization:")
    print(sentence_tokenize(sample))

    print("\nWord Tokenization:")
    print(word_tokenize_text(sample))

    print("\nPipeline Output:")
    print(preprocess_text(sample))

    print("\nSearch Result (google):")
    print(search_dataset("google").head())


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    test()