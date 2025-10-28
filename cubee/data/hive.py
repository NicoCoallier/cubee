from datetime import date 

from cubee.data.utils import SeasonCheck
from cubee.data.queen import Queen

class Hive:
    def __init__(self, hid,hive_age, state,creation_date):
        self.hid = hid
        self.state = state 
        self.hive_age = hive_age
        self.creation_date = creation_date
        self.growth = []
        self.fob = []
        self.varroa = []
        self.agg = []
        self.queen = []
        self.cubee = 0
        self.foh = []
        self.season_cubee = dict()
        self.cubee_spring = 0
        self.cubee_summer = 0
        self.cubee_fall = 0
        self.low_age_cubee = 0
        self.medium_age_cubee = 0
        self.high_age_cubee = 0

    def _append_fob(self,v,vb, ts,season):
        if v > 0:
            if len(self.queen) > 0:
                queen_age, _ = self.queen[-1]._get_state()
            else:
                queen_age = None

            try:
                cs = self.season_cubee[season]
            except:
                cs = 0 
            
            self.fob.append({"ts":ts,"fob":v,"fobr":vb,"cubee":cs,"lifetime_cubee":self.cubee, "queen_age":queen_age,"season":season})

    def _append_varroa(self,v,ts,season, hive_age, state, fob):
        if v >= 0:
            if len(self.queen) > 0:
                queen_age, _ = self.queen[-1]._get_state()
            else:
                queen_age = None
            try:
                cs = self.season_cubee[season]
            except:
                cs = 0 
            self.varroa.append({"ts":ts,"varroa":v,"cubee":cs,"lifetime_cubee":self.cubee, "queen_age":queen_age,"season":season,"hive_age":hive_age,"state":state,"fob":fob})

    def _append_agg(self,v,ts):
        self.agg.append({"agg_score":v,"date":ts,"cubee":self.cubee})

    def _add_cubee_queen(self):
        self.queen[-1].cubee +=1

    def _append_queen(self, qn, ts):
        exclude = ['queen cell present', 'queenless', 'capped queen cell',
           'introduced','double queen (for a later split)','queennotright']
        if qn not in exclude:
            if len(self.queen) == 0:
                self.queen.append(Queen(born_date=ts, name=qn))
            else:
                previous_queen = self.queen[-1]
                self.queen[-1].set_death_date(ts)
                self.queen.append(Queen(born_date=ts, name=qn))

    def _add_cubee_age_based(self,v, age, season):
        if age < 180:
            self.low_age_cubee += 1
        elif (age >= 180) & (age < 365):
            self.medium_age_cubee +=1
        else:
            self.high_age_cubee +=1
    def _append_fh(self, v, ts,season):
        if len(self.queen) > 0:
            queen_age, _ = self.queen[-1]._get_state()
        else:
            queen_age = None
        try:
            cs = self.season_cubee[season]
        except:
            cs = 0 
        self.foh.append({"ts":ts,"foh":v,"season":season,"cubee":cs,"lifetime_cubee":self.cubee, "queen_age":queen_age})
        

    def _add_season_cubee(self,v, season):
        if season in self.season_cubee.keys():
            self.season_cubee[season] += v
        else:
            self.season_cubee[season] = 1 

    def _add_cubee(self,v, ts, season):
        if SeasonCheck._check_spring(ts):
            self.cubee_spring += v
        elif SeasonCheck._check_summer(ts):
            self.cubee_summer += v
        elif SeasonCheck._check_fall:
            self.cubee_fall += v
        self.cubee += v


    def ingest_history(self, d):
        for i,row in d.iterrows():
            if (row['action_detail'] == 'mushroom') | (row['category'] == 'cubee ml'):
                self._add_cubee(1, row['report_submitted_at'], row['season'])
                self._add_cubee_age_based(1, row['hive_age'], row['season'])
                self._add_season_cubee(1, row['season'])
                if len(self.queen) > 0:
                    self._add_cubee_queen()
            if row['category'] == 'queen management':
                self._append_queen(row['action_detail'],row['report_submitted_at'])
       
            self._append_fh(row['foh'],row['report_submitted_at'], row['season']) 
            self._append_fob(row['fob'],row['fobr'],row['report_submitted_at'], row['season'])
            self._append_agg(row['agressivity'], row['report_submitted_at'])
            self._append_varroa(row['varroa'],row['report_submitted_at'],row['season'], row['hive_age'],row['is_alive'],row['fob'])
        return self

    

    def create_monthly_growth_dataset(self,one_hive_data):
        colnames = ["fob","fobr","varroa","queen_age","is_alive","hive_age","cubee",'season']
        min_date = one_hive_data['report_submitted_at'].min()
        max_date = one_hive_data['report_submitted_at'].max()
        number_of_months = int(abs((max_date-min_date).days)/30.5) +6
        current_date = date(min_date.year,min_date.month,1)
        def add_month(d, n):
            if d.month+n <= 12:
                return d.year, d.month + n
            elif (d.month+n > 12) & (d.month+n <=24):
                return d.year+1, d.month+n - 12
            elif (d.month+n > 24) & (d.month+n <=36):
                return d.year+2, d.month+n - 24
            elif (d.month+n > 36) & (d.month+n <=48):
                return d.year+3, d.month+n - 36
            elif (d.month+n > 48) & (d.month+n <=60):
                return d.year+4, d.month+n - 48
            else:
                return d.year, d.month + n
        default = {"fob":None,"fobr":None,"varroa":None,"queen_age":None, "is_alive":1,"hive_age":None, "cubee":0, "season":None}
        results = {date(add_month(current_date,n)[0],add_month(current_date,n)[1], 1):{f:default[f] for f in colnames} for n in range(number_of_months)}
        for n in range(number_of_months):
            current_date = date(add_month(current_date,n)[0],add_month(current_date,n)[1], 1)
            for colname in colnames:
                smallest_delta = 60
                for i,row in one_hive_data.iterrows():
                    current_delta = abs((current_date-row['report_submitted_at'].date()).days)
                    if  current_delta < smallest_delta:
                        smallest_delta = current_delta        
                        if colname == 'cubee':
                            if (row['action_detail'] == 'mushroom') | (row['category'] == 'cubee ml'):
                                results[current_date]['cubee'] = 1
                        elif colname == 'queen_age':
                            queen_age = None
                            if len(self.queen) > 0:
                                for q in self.queen:
                                    if q.check_alive_date(current_date):
                                        queen_age = q.get_age_at(current_date)        
                            results[current_date]['queen_age'] = queen_age
                                
                        else:
                            if row[colname] is not None:
                                try:
                                    results[current_date][colname] = row[colname]
                                except:
                                    print(results, current_date)
            
        return results
                
        