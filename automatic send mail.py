import requests
import time

class Cricbuzz():
    def __init__(self):
        pass

    def crawl_url(self,url):
        try:
            r = requests.get(url).json()
            return r
        except Exception:
            raise

    def players_mapping(self,mid):
        url = "http://mapps.cricbuzz.com/cbzios/match/" + mid
        match = self.crawl_url(url)
        players = match.get('players')
        d = {}
        for p in players:
            d[int(p['id'])] = p['name']
        t = {}
        t[int(match.get('team1').get('id'))] = match.get('team1').get('name')
        t[int(match.get('team2').get('id'))] = match.get('team2').get('name')
        return d,t

    def matchinfo(self,mid):
        d = {}
        d['id'] = mid
        url = "http://mapps.cricbuzz.com/cbzios/match/" + mid
        match = self.crawl_url(url)

        d['srs'] = match.get('series_name')
        d['mnum'] = match.get('header',).get('match_desc')
        d['type'] = match.get('header').get('type')
        d['mchstate'] = match.get('header').get('state')
        d['status'] = match.get('header').get('status')
        d['venue_name'] = match.get('venue').get('name')
        d['venue_location'] = match.get('venue').get('location')
        d['toss'] = match.get('header').get('toss')
        d['official'] = match.get('official')
        d['start_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(match.get('header').get('start_time'))))


        #squads
        p_map,_ = self.players_mapping(mid)
        team1 = {}
        team1['name'] = match.get('team1').get('name')
        t1_s = match.get('team1').get('squad')
        if t1_s is None:
            t1_s = []
        team1['squad'] = [ p_map[id] for id in t1_s]
        t1_s_b = match.get('team1').get('squad_bench')
        if t1_s_b is None:
            t1_s_b = []
        team1['squad_bench'] =  [ p_map[id] for id in t1_s_b]
        team2 = {}
        team2['name'] = match.get('team2').get('name')
        t2_s = match.get('team2').get('squad')
        if t2_s is None:
            t2_s = []
        team2['squad'] = [ p_map[id] for id in t2_s]
        t2_s_b = match.get('team2').get('squad_bench')
        if t2_s_b is None:
            t2_s_b = []
        team2['squad_bench'] =  [ p_map[id] for id in t2_s_b]
        d['team1'] = team1
        d['team2'] = team2
        return d

    def matches(self):
        url = "http://mapps.cricbuzz.com/cbzios/match/livematches"
        crawled_content = self.crawl_url(url)
        matches = crawled_content['matches']
        #info = []
        return matches
        #for match in matches:
        #    info.append(self.matchinfo(match['match_id']))
        #return info

    def find_match(self,id):
        url = "http://mapps.cricbuzz.com/cbzios/match/livematches"
        crawled_content = self.crawl_url(url)
        matches = crawled_content['matches']

        for match in matches:
            if match['match_id'] == id:
                return match
        return None

    def livescore(self,mid):
        data = {}
        try:
            comm = self.find_match(mid)
            if comm is None:
                return data
            batting = comm.get('bat_team')
            if batting is None:
                return data
            bowling = comm.get('bow_team')
            batsman = comm.get('batsman')
            bowler = comm.get('bowler')

            team_map = {}
            team_map[comm["team1"]["id"]] = comm["team1"]["name"]
            team_map[comm["team2"]["id"]] = comm["team2"]["name"]

            if batsman is None:
                batsman = []
            if bowler is None:
                bowler = []
            d = {}
            d['team'] = team_map[batting.get('id')]
            d['score'] = []
            d['batsman'] = []
            for player in batsman:
                d['batsman'].append({'name':player['name'],'runs': player['r'],'balls':player['b'],'fours':player['4s'],'six':player['6s']})
            binngs = batting.get('innings')
            if binngs is None:
                binngs = []
            for inng in binngs:
                d['score'].append({'inning_num':inng['id'], 'runs': inng['score'],'wickets':inng['wkts'],'overs':inng['overs'],'declare':inng.get('decl')})
            data['batting'] = d
            d = {}
            d['team'] = team_map[bowling.get('id')]
            d['score'] = []
            d['bowler'] = []
            for player in bowler:
                d['bowler'].append({'name':player['name'],'overs':player['o'],'maidens':player['m'],'runs':player['r'],'wickets':player['w']})
            bwinngs = bowling.get('innings')
            if bwinngs is None:
                bwinngs = []
            for inng in bwinngs:
                d['score'].append({'inning_num':inng['id'], 'runs': inng['score'],'wickets':inng['wkts'],'overs':inng['overs'],'declare':inng.get('decl')})
            data['bowling'] = d
            return data
        except Exception:
            raise

    def commentary(self,mid):
        data = {}
        try:
            url =  "http://mapps.cricbuzz.com/cbzios/match/" + mid + "/commentary"
            comm = self.crawl_url(url).get('comm_lines')
            d = []
            for c in comm:
                if "comm" in c:
                    d.append({"comm":c.get("comm"),"over":c.get("o_no")})
            data['commentary'] = d
            return data
        except Exception:
            raise

    def scorecard(self,mid):
        try:
            url = "http://mapps.cricbuzz.com/cbzios/match/" +  mid + "/scorecard.json"
            scard = self.crawl_url(url)
            p_map,t_map = self.players_mapping(mid)

            innings = scard.get('Innings')
            data = {}
            d = []
            card = {}
            for inng in innings:
                card['batteam'] = inng.get('bat_team_name')
                card['runs'] = inng.get('score')
                card['wickets'] = inng.get('wkts')
                card['overs'] = inng.get('ovr')
                card['inng_num'] = inng.get('innings_id')
                extras = inng.get("extras")
                card["extras"] = {"total":extras.get("t"),"byes":extras.get("b"),"lbyes":extras.get("lb"),"wides":extras.get("wd"),"nballs":extras.get("nb"),"penalty":extras.get("p")}
                batplayers = inng.get('batsmen')
                if batplayers is None:
                    batplayers = []
                batsman = []
                bowlers = []
                fow = []
                for player in batplayers:
                    status = player.get('out_desc')
                    p_name = p_map[int(player.get('id'))]
                    batsman.append({'name':p_name,'runs': player['r'],'balls':player['b'],'fours':player['4s'],'six':player['6s'],'dismissal':status})
                card['batcard'] = batsman
                card['bowlteam'] = t_map[int(inng.get("bowl_team_id"))]
                bowlplayers = inng.get('bowlers')
                if bowlplayers is None:
                    bowlplayers = []
                for player in bowlplayers:
                    p_name = p_map[int(player.get('id'))]
                    bowlers.append({'name':p_name,'overs':player['o'],'maidens':player['m'],'runs':player['r'],'wickets':player['w'],'wides':player['wd'],'nballs':player['n']})
                card['bowlcard'] = bowlers
                fall_wickets = inng.get("fow")
                if fall_wickets is None:
                    fall_wickets = []
                for p in fall_wickets:
                    p_name = p_map[int(p.get('id'))]
                    fow.append({"name":p_name,"wkt_num":p.get("wkt_nbr"),"score":p.get("score"),"overs":p.get("over")})
                card["fall_wickets"] = fow
                d.append(card.copy())
            data['scorecard'] = d
            return data
        except Exception:
            raise

    def fullcommentary(self,mid):
        data = {}
        try:
            url =  "https://www.cricbuzz.com/match-api/"+mid+"/commentary-full.json"
            comm = self.crawl_url(url).get('comm_lines')
            d = []
            for c in comm:
                if "comm" in c:
                    d.append({"comm":c.get("comm"),"over":c.get("o_no")})
            data['fullcommentary'] = d
            return data
        except Exception:
            raise
    def players(self,mid):
        data = {}
        try:
            url =  "https://www.cricbuzz.com/match-api/"+mid+"/commentary.json"
            players = self.crawl_url(url).get('players')
            d = []
            for c in players:
                if "player" in c:
                    d.append({"id":c.get("id"),"f_name":c.get("f_name"),"name":c.get("name"),"bat_style":c.get("bat_style"),"bowl_style":c.get("bowl_style")})
            data['players'] = d
            return data
        except Exception:
            raise
c=Cricbuzz()


#print(new)
#for i in new:
#    print(new['match_id'])
#print(new[0]['id'])
matches=c.matches()
#print(matches)
info = []
#'series_name': 'Indian Premier League 2020'
#a=c.players_mapping('30474')
#for match in matches:
#    if (match['series_name']=='Indian Premier League 2020') and (srs_category['state']=='preview'):
#        info.append(match['match_id'])
for match in matches:
    if match['series_name']=='Indian Premier League 2020':
        #info.append(match['match_id'])
        info.append(c.matchinfo(match['match_id']))
#for match in matches:
#    print(match['series_name'])
#for match in matches:
#    print(match['state'])
print(info)

print("#########################################################")

for i in info:
    if(i['mchstate']=='toss'):
        print(i['team1']['name'])
        print(i['team2']['name'])
        print(i['venue_name'])
        print(i['toss'])
        print(i['status'])
        a=i['status']

team1=''
team2=''
venue_name=''
toss_winner=''
for i in info:
    if(i['mchstate']=='toss'):
        team1 = i['team1']['name']
        team2 = i['team2']['name']
        venue_name = i['venue_name']
        toss=i['toss']



#for i in info:
#    if(i['mchstate']=='inprogress'):
#        team1 = i['team1']['name']
#        team2 = i['team2']['name']
#        venue_name = i['venue_name']
#        toss=i['toss']
#        print(i['toss'])







t2 = toss.split()

if "Chennai" in t2:
    toss_winner="CSK" 
if "Kings" in t2:
    toss_winner="KXIP"
if "Sunrisers" in t2:
    toss_winner="SRH"
if "Kolkata" in t2:
    toss_winner="KKR"        
if "Royal" in t2:
    toss_winner="RCB"
if "Rajasthan" in t2:
    toss_winner="RR"
if "Mumbai" in t2:
    toss_winner="MI"
if "Delhi" in t2:
    toss_winner="DC"

home_team=team1
away_team=team2
venue=venue_name
toss_winner=toss_winner
toss_decision=t2.pop()


print("*******************************predection function **************************************************")
print("home_team"   ,home_team)
print(away_team)
print(venue)
print(toss_winner)
print(toss_decision)










import pickle as pk
import numpy as np
import pandas as pd

def pred(home_team, away_team, venue, toss_winner, toss_decision):
    results = convert_to_numerical_field(home_team, away_team, venue, toss_winner, toss_decision)
    print(results)
    dbfile = open(r'C:\Users\paras\Desktop\Mail_with_ipl\model.pkl', 'rb')    
    db = pk.load(dbfile)
    #y_pred=model.predict([results])
    y_pred=db.predict([results])



    db.predict([results])
    print(y_pred[0])

    global act_win_team
    
    if y_pred[0]==home_team and y_pred[0]==away_team:
    
        if y_pred[0]==1:
            act_win_team='MI'
        if y_pred[0]==2:
            act_win_team='KKR'    
        if y_pred[0]==3:
            act_win_team='RCB'     
        if y_pred[0]==4:
            act_win_team='DC'    
        if y_pred[0]==5:
            act_win_team='CSK'                
        if y_pred[0]==6:
            act_win_team='RR'     
        if y_pred[0]==7:
            act_win_team='DD'    
        if y_pred[0]==8:
            act_win_team='GL'             
        if y_pred[0]==9:
            act_win_team='KXIP'     
        if y_pred[0]==10:
            act_win_team='SRH'    
        if y_pred[0]==11:
            act_win_team='RPS' 
        if y_pred[0]==12:
            act_win_team='KTK'    
        if y_pred[0]==13:
            act_win_team='PW'       

    else:
        act_win_team=cal_ef_score(home_team,away_team)
        
    return act_win_team    

def convert_to_numerical_field(home_team, away_team, venue, toss_winner, toss_decision):
    list = []

    if home_team == 'Mumbai Indians':
        list.append(1)
    if home_team == "Kolkata Knight Riders":
        list.append(2)
    if home_team == "Royal Challengers Bangalore":
        list.append(3)
    if home_team == "Delhi Capitals":
        list.append(4)
    if home_team == "Chennai Super Kings":
        list.append(5)
    if home_team == "Rajasthan Royals":
        list.append(6)
    if home_team == "DD":
        list.append(7)
    if home_team == "GL":
        list.append(8)
    if home_team == "Kings XI Punjab":
        list.append(9)
    if home_team == "Sunrisers Hyderabad":
        list.append(10)
    if home_team == "RPS":
        list.append(11)
    if home_team == "KTK":
        list.append(12)   
    if home_team == "PW":
        list.append(13)        
        
    if away_team== 'Mumbai Indians':
        list.append(1)
    if away_team== "Kolkata Knight Riders":
        list.append(2)
    if away_team== "Royal Challengers Bangalore":
        list.append(3)
    if away_team== "Delhi Capitals":
        list.append(4)
    if away_team== "Chennai Super Kings":
        list.append(5)
    if away_team== "Rajasthan Royals":
        list.append(6)
    if away_team== "DD":
        list.append(7)
    if away_team== "GL":
        list.append(8)
    if away_team== "Kings XI Punjab":
        list.append(9)
    if away_team== "Sunrisers Hyderabad":
        list.append(10)
    if away_team== "RPS":
        list.append(11)
    if away_team== "KTK":
        list.append(12)   
    if away_team== "PW":
        list.append(13)

    if home_team == 'MI':
        list.append(1)
    if home_team == "KKR":
        list.append(2)
    if home_team == "RCB":
        list.append(3)
    if home_team == "DC":
        list.append(4)
    if home_team == "CSK":
        list.append(5)
    if home_team == "RR":
        list.append(6)
    if home_team == "DD":
        list.append(7)
    if home_team == "GL":
        list.append(8)
    if home_team == "KXIP":
        list.append(9)
    if home_team == "SRH":
        list.append(10)
    if home_team == "RPS":
        list.append(11)
    if home_team == "KTK":
        list.append(12)   
    if home_team == "PW":
        list.append(13)        
        
    if away_team== 'MI':
        list.append(1)
    if away_team== "KKR":
        list.append(2)
    if away_team== "RCB":
        list.append(3)
    if away_team== "DC":
        list.append(4)
    if away_team== "CSK":
        list.append(5)
    if away_team== "RR":
        list.append(6)
    if away_team== "DD":
        list.append(7)
    if away_team== "GL":
        list.append(8)
    if away_team== "KXIP":
        list.append(9)
    if away_team== "SRH":
        list.append(10)
    if away_team== "RPS":
        list.append(11)
    if away_team== "KTK":
        list.append(12)   
    if away_team== "PW":
        list.append(13)   
        
    if venue=="Dr DY Patil Sports Academy":
        list.append(1)
    if venue=="Feroz Shah Kotla":
        list.append(2)
    if venue=="Wankhede Stadium":
        list.append(3)        
    if venue=="Maharashtra Cricket Association Stadium":
        list.append(4)        
    if venue=="Punjab Cricket Association Stadium, Mohali":
        list.append(5)
    if venue=="M Chinnaswamy Stadium":
        list.append(6)
    if venue=="Eden Gardens":
        list.append(7)        
    if venue=="MA Chidambaram Stadium, Chepauk":
        list.append(8)        
    if venue=="Rajiv Gandhi International Stadium, Uppal":
        list.append(9)
    if venue=="Sawai Mansingh Stadium":
        list.append(10)
    if venue=="Himachal Pradesh Cricket Association Stadium":
        list.append(11)        
    if venue=="Saurashtra Cricket Association Stadium":
        list.append(12)        
    if venue=="Green Park":
        list.append(13)
    if venue=="New Wanderers Stadium":
        list.append(14)
    if venue=="Punjab Cricket Association IS Bindra Stadium, Mohali":
        list.append(15)        
    if venue=="Holkar Cricket Stadium":
        list.append(16)        
    if venue=="Subrata Roy Sahara Stadium":                             
        list.append(17)
    if venue=="Vidarbha Cricket Association Stadium, Jamtha":
        list.append(18)
    if venue=="Dubai International Cricket Stadium":
        list.append(19)        
    if venue=="Kingsmead":
        list.append(20)        
    if venue=="Nehru Stadium":
        list.append(21)
    if venue=="JSCA International Stadium Complex":
        list.append(22)
    if venue=="Sardar Patel Stadium, Motera":
        list.append(23)        
    if venue=="Sharjah Cricket Stadium":
        list.append(24)  
    if venue=="Brabourne Stadium":
        list.append(25)
    if venue=="Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium":
        list.append(26)        
    if venue=="Shaheed Veer Narayan Singh International Stadium":
        list.append(27)          
    if venue=="Sheikh Zayed Stadium":
        list.append(28)
    if venue=="M.Chinnaswamy Stadium":
        list.append(29)        
    if venue=="St George's Park":
        list.append(30)          
    if venue=="Newlands":
        list.append(31)
    if venue=="SuperSport Park":
        list.append(32)       
    if venue=="Buffalo Park":
        list.append(33)               
    if venue=="Barabati Stadium":
        list.append(34)       
    if venue=="OUTsurance Oval":
        list.append(35)              
    if venue=="De Beers Diamond Oval":
        list.append(36)             

    if toss_winner== 'MI':
        list.append(1)
    if toss_winner== "KKR":
        list.append(2)
    if toss_winner== "RCB":
        list.append(3)
    if toss_winner== "DC":
        list.append(4)
    if toss_winner== "CSK":
        list.append(5)
    if toss_winner== "RR":
        list.append(6)
    if toss_winner== "DD":
        list.append(7)
    if toss_winner== "GL":
        list.append(8)
    if toss_winner== "KXIP":
        list.append(9)
    if toss_winner== "SRH":
        list.append(10)
    if toss_winner== "RPS":
        list.append(11)
    if toss_winner== "KTK":
        list.append(12)   
    if toss_winner== "PW":
        list.append(13) 
        
    if toss_decision=="bat":
        list.append(0)
    if toss_decision=="field":    
        list.append(1)
    if toss_decision=="bowl":    
        list.append(1)                
        
    return list    

ef_data = pd.read_csv(r'C:\Users\paras\Desktop\Mail_with_ipl\_team_rank.csv')

ef_data.replace(['Mumbai Indians','Kolkata Knight Riders','Royal Challengers Bangalore','Deccan Chargers','Chennai Super Kings',
                 'Rajasthan Royals','Delhi Daredevils','Delhi Capitals','Gujarat Lions','Kings XI Punjab',
                 'Sunrisers Hyderabad','Rising Pune Supergiants','Rising Pune Supergiant','Kochi Tuskers Kerala','Pune Warriors']
                ,['MI','KKR','RCB','DC','CSK','RR','DD','DD','GL','KXIP','SRH','RPS','RPS','KTK','PW'],inplace=True)

def cal_ef_score(home_team,away_team):
    
    home_score = list(ef_data.loc[ef_data['Team'] == home_team]['sum'])
    away_score = list(ef_data.loc[ef_data['Team'] == away_team]['sum'])
    if home_score > away_score :
        return home_team
    else:
        return away_team



#print(pred('MI','CSK','Sheikh Zayed Stadium','CSK','bat'))       
result=pred(home_team,away_team,venue,toss_winner,toss_decision)

print(result)


print("***********************sending mail***************************")

import smtplib 
 
  
# list of email_id to send the mail 
li = ["parasbhalala77@gmail.com","bhutprit786@gmail.com","harshilbg7@gmail.com","adipatelrock1997@gmail.com"] 
#li = ["parasbhalala77@gmail.com"] 

for dest in li: 
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    s.starttls() 
    s.login("gmail@gmail.com", "password")# email_id and password 
    SUBJECT = "Today IPL Match Predection"   
    TEXT = f"Dear Friends, \r\n   Today ipl match between {home_team} and {away_team}.{toss_winner} won the toss and choses to {toss_decision}.and today match is being played in {venue}. \r\n According to our Predections {result} will win the match today."
    message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
    #message = "Message_you_need_to_send"
    s.sendmail("sender_email_id", dest, message) 
    print(team1)
    s.quit() 

print("*********************************log file***************************")

import datetime 	

file = open("log.txt","a+")  

current_time = str(datetime.datetime.now())

a=[]

a.append(current_time)
a.append(home_team)
a.append(away_team)
a.append(venue)
a.append(toss_winner)
a.append(toss_decision)
a.append(result)
a.append("****************")


for i in (a):
	print(i)
	file.write("%s\r\n" %i)
#file1.write(a)
a=[]


file.close()






# list of email_id to send the mail 
'''li = ["parasbhalala77@gmail.com","bhutprit786@gmail.com","harshilbg7@gmail.com","adipatelrock1997@gmail.com"] 
#li=["parasbhalala77@gmail.com"]
  
for dest in li: 
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    s.starttls() 
    s.login("gmail@gmail.com", "password") 
    SUBJECT = "Today IPL Match Predection"   
    TEXT = f"Dear Friends, \r\n        Today ipl match between {home_team} and {away_team}.  {toss_winner} won the toss and choses to {toss_decision}. and today match is being played in {venue}.  \r\n   According to our Predections {result} will win the match today."
    message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
    #message = "Message_you_need_to_send"
    s.sendmail("sender_email_id", dest, message) 
    
    s.quit()''' 





'''[{'id': '30475', 'srs': 'Indian Premier League 2020', 'mnum': '40th Match', 'type': 'T20', 'mchstate': 'toss', 'status': 'Sunrisers HYD opt to bowl', 'venue_name': 'Dubai
onal Cricket Stadium', 'venue_location': 'Dubai, United Arab Emirates', 'toss': 'Sunrisers Hyderabad elect to bowl', 'official': {'umpire1': {'id': '4730', 'name': 'Paul
'country': 'AUS'}, 'umpire2': {'id': '8862', 'name': 'Nitin Menon', 'country': 'IND'}, 'umpire3': {'id': '8294', 'name': 'Anil Chaudhary', 'country': 'IND'}, 'referee': {
4', 'name': 'Javagal Srinath', 'country': 'IND'}}, 'start_time': '2020-10-22 19:30:00', 'team1': {'name': 'Rajasthan Royals', 'squad': ['Samson', 'Smith'], 'squad_bench':
, 'Uthappa', 'Buttler', 'Riyan Parag', 'Rahul Tewatia', 'Jofra Archer', 'Shreyas Gopal', 'Rajpoot', 'Kartik Tyagi', 'Aaron', 'Unadkat', 'Miller', 'Aniruddha Joshi', 'Vohr
urran', 'Tye', 'Shashank Singh', 'Lomror', 'Thomas', 'Markande', 'Anuj Rawat', 'Jaiswal', 'Akash Singh']}, 'team2': {'name': 'Sunrisers Hyderabad', 'squad': ['Bairstow',
 'squad_bench': ['Williamson', 'Priyam Garg', 'Manish Pandey', 'Shankar', 'Abdul Samad', 'Rashid Khan', 'Sandeep Sharma', 'T Natarajan', 'Basil Thampi', 'W Saha', 'Goswam
l', 'Nabi', 'Nadeem', 'Holder', 'Sandeep', 'Stanlake', 'Fabian Allen', 'Virat Singh', 'Khaleel Ahmed', 'Sanjay Yadav', 'Abhishek Sharma', 'Prithvi Raj']}}]'''    