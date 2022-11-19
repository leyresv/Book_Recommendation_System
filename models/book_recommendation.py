import json
import os.path
import pandas as pd
import numpy as np
from data.utils import get_document_embedding, cosine_similarity

cur_file_path = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.join(cur_file_path, "../data")

from utils.spell_checker import SpellChecker


class BookRetriever:
    """
    Class to recommend books based on their content
    """

    def __init__(self):
        self.vocab = json.load(open(os.path.join(data_path, "vocab.json")))
        self.dataset = pd.read_pickle(os.path.join(data_path, "books_dataset.pkl"))
        self.spell_checker = SpellChecker(dataset = " ".join(self.dataset["title"].tolist()))

    def get_title_options(self, title):
        """
        Check the spelling of a title

        :param title: title (string) to be spell-checked
        :return: list of all the possible title variations
        """
        titles_vocab = self.spell_checker.get_vocab()
        word_options = []
        # For each word on the title:
        for word in title.split():
            # Keep it if it's part of the vocabulary
            if word.lower() in titles_vocab:
                word_options.append(word)
            # If not, find similar words that are part of the vocabulary
            else:
                word_suggestions = self.spell_checker.get_suggestions(word.lower(), n=10)
                word_options.append([suggestion[0] for suggestion in word_suggestions])

        # Get all the possible word combinations
        titles = [""]
        for item in word_options:
            if isinstance(item, list):
                options = []
                for title in titles:
                    options.extend([" ".join([title, i]) for i in item])
                titles = options.copy()
            else:
                titles = [" ".join([title, item]) for title in titles]
        titles = [title.strip() for title in titles]
        return titles

    def retrieve_top_k(self, k, title=None, description=None, same_genre=False):
        """
        Retrieve the k most similar books to the introduced one (content-based)

        :param k: desired number of recommendations (int)
        :param title: title of the target book (String)
        :param description: description of the target book (String)
        :param same_genre: True to keep recommendations from the same genre to the one of the introduced title
        :return: k book recommendations
        """
        summaries = self.dataset["summary_emb"].tolist()
        genres = self.dataset["genre"].tolist()
        titles = self.dataset["title"].tolist()
        titles_lower = self.dataset["title_lower"].tolist()
        titles_emb = self.dataset["title_emb"].tolist()

        if (not title and not description) or (title and description):
            return("Please, introduce either title or description")

        # Look for books whose summary is similar to the summary of the introduced book
        if title:
            # Retrieve dataset entry for the desired title
            target_book = self.dataset.loc[self.dataset["title_lower"] == title.lower()]
            # If the title is not found,find the most similar title in the dataset
            if target_book.empty:
                # Check if the introduced title is a part of a title in the dataset
                possible_titles = [t for t in titles if title.lower() in t.lower()]
                if possible_titles:
                    distances = [self.spell_checker.min_edit_distance(option, title) for option in possible_titles]
                    title = possible_titles[np.argmin(distances)]
                    print("You mean:", title)
                    target_book = self.dataset.loc[self.dataset["title_lower"] == title.lower()]

                # Check the spelling of the introduced title
                else:
                    title_options = [option for option in self.get_title_options(title) if option in titles_lower]

                    # If there is only one title option present in the dataset, keep it
                    if len(title_options) == 1:
                        target_book = self.dataset.loc[self.dataset["title_lower"] == title_options[0]]
                        print("One retrieved option:", title_options[0])

                    # If there are more than one title options, keep the closest one to the introduced title
                    elif len(title_options) > 1:
                        distances = [self.spell_checker.min_edit_distance(option, title) for option in title_options]
                        title = title_options[np.argmin(distances)]
                        target_book = self.dataset.loc[self.dataset["title_lower"] == title]
                        print("Multiple title options retrieved:", title_options)
                        print("Most similar one to input:", title)

                    # If there are no options, get the closest dataset's title that shares the most words with the input
                    else:
                        distances = [len(set(title.split()).intersection(option.split())) for option in titles_lower]
                        title = titles_lower[np.argmax(distances)]
                        target_book = self.dataset.loc[self.dataset["title_lower"] == title]
                        print("No title options")
                        print("Most similar dataset title to input:", title)

            target_summary = target_book.summary_emb.values[0]

        # Look for books whose summary is similar to the provided description
        else:
            target_summary = get_document_embedding(description, self.vocab)

        # Retrieve only books with the same genre to the provided one
        if title and same_genre:
            # If the provided book has no genre in our dataset, retrieve the books with the most similar summaries
            if isinstance(target_book.genre.values[0], float):
                print("No specified genre")
                cos_scores = [cosine_similarity(target_summary, summary) for summary in summaries]

            # If the provided book has a genre, retrieve books with the most similar summaries and the same genre
            else:
                target_genre = json.loads(target_book.genre.values[0])
                cos_scores = []
                for (summary, genre) in zip(summaries, genres):
                    if isinstance(genre, float):
                        cos_scores.append(0)
                    else:
                        genre = json.loads(genre)
                        cos_sim = 0
                        for key, value in target_genre.items():
                            if (key, value) in genre.items():
                                cos_sim = cosine_similarity(target_summary, summary)
                                break
                        cos_scores.append(cos_sim)

        else:
            cos_scores = [cosine_similarity(target_summary, summary) for summary in summaries]

        # Get the top k context with the highest cosine similarity with the query
        sorted_ids = np.argsort(cos_scores)

        # Get the indices of the k most similar candidate vectors
        n_idx = list(sorted_ids[-(k+1):-1])
        n_idx.reverse()

        return self.dataset.iloc[n_idx].drop(["wiki_id", "freebase_id", "summary_emb", "length", "title_lower"], axis=1)
