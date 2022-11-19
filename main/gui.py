from tkinter import *
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
        self.mode = ""

        self.search_label = Label(win, text='Title')
        self.search_label.place(x=100, y=100)
        self.search_entry = Entry(width=150)
        self.search_entry.place(x=300, y=100)

        self.search_button = Button(win, text='Search', command=self.title_search)
        self.search_button.place(x=100, y=200)

        self.mode_button_title = Radiobutton(window, text="title", variable=self.mode_variable, value=1, command=self.title_display)
        self.mode_button_content = Radiobutton(window, text="content", variable=self.mode_variable, value=2, command=self.content_display)
        self.mode_button_title.place(x=200, y=50)
        self.mode_button_content.place(x=300, y=50)

        self.num_label = Label(win, text='Number of recommendations')
        self.num_entry = Entry()
        self.num_label.place(x=100, y=150)
        self.num_entry.place(x=300, y=150)

        self.result_label = Label(win, text='Result')
        self.result_label.place(x=100, y=250)
        self.result_text = Text(win, height=10, width=100)
        self.sbar = Scrollbar(win, command=self.result_text.yview)
        self.sbar.pack(side=RIGHT, fill=Y)
        self.result_text.pack(side=LEFT, fill=Y)
        self.result_text.config(yscrollcommand=self.sbar.set)
        self.result_text.place(x=200, y=250)

    def title_display(self):
        self.search_label.config(text="Title")
        self.search_button.configure(command=self.title_search)

    def content_display(self):
        self.search_label.config(text="Content")
        self.search_button.configure(command=self.content_search)

    def title_search(self):
        print("Title search function called")
        self.result_text.delete(1.0, END)
        title = self.search_entry.get()
        k = int(self.num_entry.get())
        results = self.book_retriever.retrieve_top_k(k, title=title)

        recommendations = [(t, a, s) for t, a, s in zip(results["title"], results["author"], results["summary"])]
        for t, a, s in recommendations:
            self.result_text.insert(END, "Title: " + str(t) + "\n")
            if str(a) == "nan":
                a = "Unknown"
            self.result_text.insert(END, "Author: " + str(a) + "\n\n")
           # self.result.insert(END, "Summary: " + s + "\n\n")

    def content_search(self):
        self.result_text.delete(1.0, END)
        content = self.search_entry.get()
        k = int(self.num_entry.get())
        print("Content search function called")
        results = self.book_retriever.retrieve_top_k(k, description=content)

        recommendations = [(t, a, s) for t, a, s in zip(results["title"], results["author"], results["summary"])]
        for t, a, s in recommendations:
            self.result_text.insert(END, "Title: " + str(t) + "\n")
            if str(a) == "nan":
                a = "Unknown"
            self.result_text.insert(END, "Author: " + str(a) + "\n\n")
           # self.result.insert(END, "Summary: " + s + "\n\n")



window=Tk()
mywin=MyWindow(window)
window.title('Hello Python')
window.geometry("1000x500+10+10")
window.mainloop()
