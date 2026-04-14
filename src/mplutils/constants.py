import typing as tp
import math

MM_PER_INCH: tp.Final = 25.4
PTS_PER_INCH: tp.Final = 72.0
PTS_PER_MM: tp.Final = PTS_PER_INCH / MM_PER_INCH
GOLDENRATIO: tp.Final = (1.0 + math.sqrt(5.0)) / 2.0  # 1.618


WIDTH_NATURE_1COL: tp.Final = 3.54
WIDTH_NATURE_2COL: tp.Final = 7.09
WIDTH_PRL_1COL: tp.Final = 3.375
WIDTH_PRL_2COL: tp.Final = 6.75
WIDTH_SCIENCE_1COL: tp.Final = 2.25
WIDTH_SCIENCE_2COL: tp.Final = 4.75
WIDTH_SCIENCE_3COL: tp.Final = 7.25
WIDTH_A4: tp.Final = 210.0 / MM_PER_INCH
WIDTH_A5: tp.Final = 148.0 / MM_PER_INCH
