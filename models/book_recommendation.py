import json
import os.path
import pandas as pd
import numpy as np
from data.utils import get_document_embedding, cosine_similarity

cur_file_path = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.join(cur_file_path, "../data")


class BookRetriever:
    """
    Class to recommend books based on their content
    """

    def __init__(self):
        self.vocab = json.load(open(os.path.join(data_path, "vocab.json")))
        self.dataset = pd.read_pickle(os.path.join(data_path, "books_dataset.pkl"))

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
        titles_emb = self.dataset["title_emb"].tolist()

        if (not title and not description) or (title and description):
            return("Please, introduce either title or description")

        # Look for books whose summary is similar to the summary of the introduced book
        if title:
            # Retrieve dataset entry for the desired title
            target_book = self.dataset.loc[self.dataset["title_lower"] == title.lower()]
            # If the title is not found,find the most similar title in the dataset
            if target_book.empty:
                possible_titles = [t for t in titles if title.lower() in t.lower()]
                if possible_titles:
                    title = possible_titles[0]
                    print("You mean:", title)
                    target_book = self.dataset.loc[self.dataset["title_lower"] == title.lower()]
                else:
                    target_title_emb = get_document_embedding(title, self.vocab)
                    titles_similarity = [cosine_similarity(target_title_emb, title_emb) for title_emb in titles_emb]
                    title = titles[np.argmax(titles_similarity)]
                    print("Retrieved title:", title)
                    target_book = self.dataset.loc[self.dataset["title_lower"] == title.lower()]

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
