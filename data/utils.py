import wget
import tarfile
import pandas as pd
import nltk
import string
import json
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from torchtext.vocab import GloVe

# Download nltk resources
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)


def import_books_dataset():
    """
    Download and extract the CMU book summaries dataset
    """
    url = "http://www.cs.cmu.edu/~dbamman/data/booksummaries.tar.gz"
    books_dataset_tar = wget.download(url)
    books_dataset = tarfile.open(books_dataset_tar)
    books_dataset.extractall()
    books_dataset.close()


def process_doc(doc):
    """
    Tokenize, remove stopwords, punctuations and lemmatize

    :param doc: Input text (String)
    :return: tokenized text (list)
    """
    doc_tok = word_tokenize(doc)
    stopwords_eng = stopwords.words("english")
    lemmatizer = WordNetLemmatizer()
    processed_doc = [lemmatizer.lemmatize(token.lower()) for token in doc_tok
                     if token not in stopwords_eng and token not in string.punctuation]
    return processed_doc


def create_embeddings_vocab(docs, glove):
    """
    Create dictionary with words as keys and their glove embeddings as values

    :param docs: dataset to extract the vocabulary from (list of strings)
    :param glove: GloVe embeddings
    :return: vocabulary dictionary
    """
    vocab = {}
    tok_docs = [process_doc(doc) for doc in docs]
    for doc in tok_docs:
        for token in doc:
            if token in glove.stoi:
                vocab[token] = glove.get_vecs_by_tokens(token).tolist()
    return vocab


def get_document_embedding(doc, vocab):
    """
    Embed text

    :param doc: text (string)
    :param vocab: vocabulary dictionary {word: embedding}
    :return: embedded text
    """
    doc_embedding = np.zeros(300)

    processed_doc = process_doc(doc)
    for word in processed_doc:
        # add the word embedding to the running total for the document embedding
        doc_embedding += np.array(vocab.get(word, 0))
    return np.array(doc_embedding)


def process_books_dataset():
    """
    Process CMU books summaries dataset to be used by the book recommendation system
    """
    col_names = ["wiki_id", "freebase_id", "title", "author", "date", "genre", "summary"]

    # Import dataset as dataframe
    books_dataset = pd.read_csv("booksummaries/booksummaries.txt", names=col_names, sep="\t")

    # Remove entries with summaries shorter than 10 words
    books_dataset["length"] = books_dataset["summary"].apply(lambda x: len(x.split()))
    books_dataset.drop(books_dataset[books_dataset.length < 10].index, inplace=True)

    summaries = books_dataset["summary"].tolist()

    # Load Glove embeddings
    glove = GloVe(dim='300', name='6B', cache="/glove")
    print("Creating vocab")
    # Create embeddings dictionary (Keep only tokens present in pre-trained Glove vocabulary)
    vocab = create_embeddings_vocab(summaries, glove)
    print(type(vocab))
    json.dump(vocab, open("vocab.json", 'w'))

    books_dataset["summary_emb"] = books_dataset["summary"].apply(lambda x: get_document_embedding(x, vocab))
    books_dataset["title_lower"] = books_dataset["title"].apply(lambda x: x.lower())
    books_dataset["title_emb"] = books_dataset["title"].apply(lambda x: get_document_embedding(x, vocab))
    books_dataset.to_pickle("books_dataset.pkl")


def cosine_similarity(A, B):
    """
    Calculate cosine similarity between two vectors

    :param A: a numpy array which corresponds to a word or doc vector
    :param B: a numpy array which corresponds to a word or doc vector
    :return: cosine similarity between A and B (float)
    """
    dot = np.dot(A, B)
    norma = np.linalg.norm(A)
    normb = np.linalg.norm(B)
    cos = dot / (norma * normb)
    return cos


if __name__ == "__main__":
    process_books_dataset()