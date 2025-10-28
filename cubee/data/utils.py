
from datetime import date 

MONTH_OF_START = 3
DAY_OF_START = 15
RANGE_SEASON_START = 90

class SeasonCheck:
    @staticmethod
    def _check_spring(ts):
        return ts.month in [4,5,6]

    @staticmethod
    def _check_summer(ts):
        return ts.month in [6,7,8]

    @staticmethod
    def _check_fall(ts):
        return ts.month in [9, 10,11]

    @staticmethod
    def _check_winter(ts):
        return ts.month in [12,1,2,3]
    

def simple_season(x):
    start = date(x["report_submitted_at"].year, MONTH_OF_START, DAY_OF_START)
    end = date(x["report_submitted_at"].year+ 1, MONTH_OF_START, DAY_OF_START)
    if (x["report_submitted_at"].date() >= start) & (
        x["report_submitted_at"].date() <= end
    ):
        return x["report_submitted_at"].year
    elif x["report_submitted_at"].date() < start: 
        if x['hive_age'] > RANGE_SEASON_START:
            return x["report_submitted_at"].year - 1
        else:
            return x["report_submitted_at"].year
    elif x["report_submitted_at"].date() > end:
        if x['hive_age'] < RANGE_SEASON_START:
            if x["report_submitted_at"].year == start.year:
                return x["report_submitted_at"].year
            else:
                return x["report_submitted_at"].year-1
        else:
            if x["report_submitted_at"].year == start.year:
                return x["report_submitted_at"].year
            else:
                return x["report_submitted_at"].year - 1
    else:
        return None