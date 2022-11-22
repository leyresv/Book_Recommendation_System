# Book_Recommendation_System

In this project, I have implemented a content-based book recommendation system.


## Installation

```bash
pip install git+https://github.com/leyresv/Book_Recommendation_System.git
pip install -r requirements.txt
```

## Usage

Before using the recommendation system, you need to download and process the [CMU Book Summaries Dataset](https://www.cs.cmu.edu/~dbamman/booksummaries.html#:~:text=This%20dataset%20contains%20plot%20summaries,Creative%20Commons%20Attribution%2DShareAlike%20License.). To do it, open a terminal prompt on the root directory and introduce the following command:
```bash
python data/utils.py
```

The data will take a few minutes to be ready. Once it's done, you can use the recommendation system by simply introducing the following command:

```bash
python main/main.py
```

If you prefer using the user interface, introduce the following command from the root directory:
```bash
python main/gui.py
```

https://user-images.githubusercontent.com/73848748/203408690-0d100775-dd24-437f-b4f5-70ec3be237f9.mp4


