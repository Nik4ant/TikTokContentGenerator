from dataclasses import dataclass
from typing import List


@dataclass()
class Question:
    used_language: str
    title: str
    answer_body_html: str
    url: str
    id: str  # Used to avoid selecting the same question again


# TODO: actual code not a placeholder
def parse_questions(amount: int) -> List[Question]:
    return [Question("python",
                     "What does if __name__ == \"__main__\": do?",
                     open("app/Video/data/static/test.html").read(),
                     "https://stackoverflow.com/questions/419163/what-does-if-name-main-do",
                     "419163")]

# https://stackoverflow.com/search?q=%5B{lang_nam}%5Danswers%3A1
# https://stackoverflow.com/search?tab=Relevance&pagesize=50&q=%5b{lang_name}%5danswers%3a1
