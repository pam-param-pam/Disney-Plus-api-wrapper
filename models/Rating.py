from enum import Enum


class Rating(Enum):
    ADULT = "1850"
    TEEN = "1650"
    KID = "9999"

    AGE18PLUS = "1850"
    AGE16PLUS = "1650"
    AGE14PLUS = "1450"
    AGE12PLUS = "1250"
    AGE9PLUS = "950"
    AGE6PLUS = "650"
    AGE0PLUS = "10"
