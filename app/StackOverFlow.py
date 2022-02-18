from dataclasses import dataclass


@dataclass()
class Question:
    used_language: str
    title: str
    answer_body_html: str
    url: str
    id: str  # Used to avoid selecting the same question again


# https://stackoverflow.com/search?q=%5B{lang_nam}%5Danswers%3A1
# https://stackoverflow.com/search?tab=Relevance&pagesize=50&q=%5b{lang_name}%5danswers%3a1