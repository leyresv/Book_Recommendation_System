import sys
import os
cur_file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(cur_file_path, '..'))
pkg_root = os.path.join(cur_file_path, '..')

from models.book_recommendation import BookRetriever


if __name__ == "__main__":
    print("Welcome to the book recommendation system. Loading the data...")
    book_retriever = BookRetriever()
    search = ""

    while search.lower() != "end":
        mode = input("If you want to find books whose content is similar to a specific title, type 'title'. \n"
                     "If you prefer to introduce a brief description of the kind of books you would like to find, type 'description': ")
        while mode.lower() != "title" and mode.lower() != "description":
            mode = input("Please, type 'title' or 'description'")

        if mode == "title":
            title = input("Introduce the book's title: ")
            k = input("How many recommendations do you want?: ")
            while not k.isdigit():
                k = input("Please, introduce the number of book recommendations you want (e.g.: 5): ")
            k = int(k)
            genre = input("Do you want recommendations of the same genre as your title? (Type 'yes' or 'no'): ")
            while genre.lower() != "yes" and genre.lower() != "no":
                genre = input("Please, introduce 'yes' or 'no': ")
            if genre.lower() == "yes":
                same_genre = True
            else:
                same_genre = False
            results = book_retriever.retrieve_top_k(k, title=title, same_genre=same_genre)

        else:
            description = input("Introduce a brief description: ")
            k = input("How many recommendations do you want?: ")
            while not k.isdigit():
                k = input("Please, introduce the number of book recommendations you want (e.g.: 5): ")
            k = int(k)
            results = book_retriever.retrieve_top_k(k, description=description)

        recommendations = [(t, a, s) for t, a, s in zip(results["title"], results["author"], results["summary"])]
        print("These are our recommendations for your next readings:")
        print("--------------------------------------------------------")
        for t, a, s in recommendations:
            print("Title:", t)
            print("Author:", a)
            print("Summary:", s)
            print("-----------------------------------------------------------")
        print()
        search = input("Type 'end' to exit or any key to make another search.")
