from enum import Enum


class Rating(Enum):
    Adult = "1850"
    Teen = "1650"
    Kid = "9999"

    Age18Plus = "1850"
    Age16Plus = "1650"
    Age14Plus = "1450"
    Age12Plus = "1250"
    Age9Plus = "950"
    Age6Plus = "650"
    Age0Plus = "10"