from tkinter import *
from tkinter.scrolledtext import ScrolledText
import sys
import os
cur_file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(cur_file_path, '..'))
pkg_root = os.path.join(cur_file_path, '..')

from models.book_recommendation import BookRetriever


class MyWindow:
    def __init__(self, win):
        self.book_retriever = BookRetriever()

        self.mode_variable = IntVar()
        self.mode_variable.set(1)
        self.mode_label = Label(win, text="Search by:")
        self.mode_label.place(x=100, y=50)
        self.mode_label.config(bg="#9fb9e3")
        self.mode = ""

        self.search_label = Label(win, text='Title')
        self.search_label.place(x=100, y=100)
        self.search_label.config(bg="#9fb9e3")
        self.search_entry = Entry(width=150)
        self.search_entry.place(x=300, y=100)

        self.search_button = Button(win, text='Search', command=self.title_search)
        self.search_button.place(x=100, y=200)

        self.mode_button_title = Radiobutton(win, text="title", variable=self.mode_variable, value=1, command=self.title_display)
        self.mode_button_content = Radiobutton(win, text="content", variable=self.mode_variable, value=2, command=self.content_display)
        self.mode_button_title.place(x=200, y=50)
        self.mode_button_title.config(bg="#9fb9e3")
        self.mode_button_content.place(x=300, y=50)
        self.mode_button_content.config(bg="#9fb9e3")

        self.same_author_var = BooleanVar()
        self.same_author_var.set(0)
        self.same_author_button = Checkbutton(win, text="same author", variable=self.same_author_var)
        self.same_author_button.place(x=400, y=50)
        self.same_author_button.config(bg="#9fb9e3")

        self.same_genre_var = BooleanVar()
        self.same_genre_var.set(0)
        self.same_genre_button = Checkbutton(win, text="same genre", variable=self.same_genre_var)
        self.same_genre_button.place(x=500, y=50)
        self.same_genre_button.config(bg="#9fb9e3")

        self.num_label = Label(win, text='Number of recommendations')
        self.num_entry = Spinbox(win, from_=1, to=10, wrap=True, state="readonly")
        self.num_label.place(x=100, y=150)
        self.num_label.config(bg="#9fb9e3")
        self.num_entry.place(x=300, y=150)

        self.result_label = Label(win, text='Recommendations')
        self.result_label.place(x=100, y=250)
        self.result_label.config(bg="#9fb9e3")
        self.result_text = ScrolledText(win, height=10, width=50, wrap="word", state="disabled", padx=15, pady=10)
        self.result_text.place(x=250, y=250)

        self.summaries_label = Label(win, text='Summaries')
        self.summaries_label.place(x=100, y=450)
        self.summaries_label.config(bg="#9fb9e3")
        self.summaries_text = ScrolledText(win,  height=15, width=150, wrap="word", state="disabled", padx=15, pady=10)
        self.summaries_text.place(x=250, y=450)

    def title_display(self):
        self.search_label.config(text="Title")
        self.search_button.configure(command=self.title_search)
        self.same_author_button.config(state="normal")
        self.same_genre_button.config(state="normal")

    def content_display(self):
        self.search_label.config(text="Content")
        self.search_button.configure(command=self.content_search)
        self.same_author_button.config(state="disabled")
        self.same_genre_button.config(state="disabled")
        self.same_author_var.set(0)
        self.same_genre_var.set(0)

    def print_results(self, results):
        self.result_text.config(state="normal")
        self.summaries_text.config(state="normal")
        self.result_text.delete(1.0, END)
        self.summaries_text.delete(1.0, END)

        recommendations = [(t, a, s) for t, a, s in zip(results["title"], results["author"], results["summary"])]
        for t, a, s in recommendations:
            self.result_text.insert(END, "Title: " + str(t) + "\n")
            if str(a) == "nan":
                a = "Unknown"
            self.result_text.insert(END, "Author: " + str(a) + "\n\n")
            self.summaries_text.insert(END, str(t) + ", from " + str(a) + "\n")
            self.summaries_text.insert(END, str(s) + "\n\n")

        self.summaries_text.config(state="disabled")
        self.summaries_text.config(state="disabled")

    def title_search(self):
        print("Title search function called")
        title = self.search_entry.get()
        k = int(self.num_entry.get())
        print(self.same_genre_var.get())
        results = self.book_retriever.retrieve_top_k(k, title=title, same_genre=self.same_genre_var.get())
        self.print_results(results)

    def content_search(self):
        print("Content search function called")
        content = self.search_entry.get()
        k = int(self.num_entry.get())
        results = self.book_retriever.retrieve_top_k(k, description=content)
        self.print_results(results)


window = Tk()
mywin = MyWindow(window)
window.title('Book recommendation system')
window.geometry("1000x500+10+10")
# Set window color
window.configure(bg="#9fb9e3")
window.mainloop()
