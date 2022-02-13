# https://stackoverflow.com/questions/tagged/c%23?tab=Active#?sort=RecentActivity&edited=true
# https://stackoverflow.com/search?q=%5Bpython%5Danswers%3A1
import dataclasses


# Note: To see top answer add this to question url: "?answertab=votes#tab-top"
@dataclasses.dataclass
class AnsweredQuestion:
    question_title: str
    question_body_html: str
    answer_html: str


def parse_questions(amount=1):
    pass
