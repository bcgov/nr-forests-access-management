from enum import Enum


class UserType(str, Enum):
    IDIR = "I"
    BCEID = "B"


COGNITO_USERNAME_KEY = "username"