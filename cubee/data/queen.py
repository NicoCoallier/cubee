
from datetime import date 

class Queen:
    def __init__(self, name, born_date, death_date=None):
        self.name = name
        self.born_date = born_date
        self.death_date = death_date
        self.cubee = 0

    def set_death_date(self, v):
        self.death_date = v

    def check_alive_date(self,current):
        if self.death_date is None:
            return current >= self.born_date.date()
        else:
            return (current >= self.born_date.date()) & (current <= self.death_date.date())

    def get_age_at(self,current):
        return abs((current-self.born_date.date()).days)

    def _get_state(self):
        if self.death_date is not None:
            return (self.death_date - self.born_date).days, True 
        else:
            return (date(2025,10,20) - self.born_date.date()).days, False
            


        
            
                
        