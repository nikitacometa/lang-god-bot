from enum import Enum


class QuizState(Enum):
    SELECTING_ANSWER = 1
    BETWEEN_QUESTIONS = 2
    NEXT_QUESTION = 3
    END = 4
    EMPTY = 5
