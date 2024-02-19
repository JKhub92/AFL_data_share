
import pandas as pd
#import os

import requests
from bs4 import BeautifulSoup
import json
import datetime
#from oauthlib.oauth2 import LegacyApplicationClient
#from requests_oauthlib import OAuth2Session 

e = 0
try:
    del(data_out_final)
except:
    print('n')

for p in range(1,850):
    
    print(p)
    
    try:
        sc_url='https://supercoach.heraldsun.com.au/2024/api/afl/classic/v1/players/'+str(p)+'?embed=notes,odds,player_stats,player_match_stats,positions,trades'
        
        # HTTP request to Stats Centre URL
        res = requests.get(sc_url)    
        
        # Parse the response as HTML using the BeautifulSoup library
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Format it to JSON
        raw_stats = str(soup).encode('utf8')
        
        # Parse to JSON to make extracting key values much easier
        json_stats = json.loads(raw_stats)
        
        p2 = None
        for r in range(1, len(json_stats['player_stats']) ):
            
            #p = 447
            #r = 8
            
            try:
                scores_temp = pd.DataFrame({'points': [x['points'] for x in json_stats['player_match_stats'][:]] , 
                               'round': [x['round'] for x in json_stats['player_match_stats'][:]] })
                scores_temp = scores_temp[scores_temp['round'] < r]
                score_p1 = list(scores_temp['points'])[-1]
            except:
                score_p1 = 0
                
            try:
                scores_temp = pd.DataFrame({'points': [x['points'] for x in json_stats['player_match_stats'][:]] , 
                               'round': [x['round'] for x in json_stats['player_match_stats'][:]] })
                scores_temp = scores_temp[scores_temp['round'] < r]
                score_p2 = list(scores_temp['points'])[-2]
            except:
                score_p2 = 0
            
            p2 = None
            try:
                p2 = json_stats['positions'][1]['position']
            except:
                p2 = None
                
            try:         
                data = {'first_name': [json_stats['first_name']] 
                ,'last_name': [json_stats['last_name']]            
                ,'round':json_stats['player_stats'][r]['round']
                ,'owned':json_stats['player_stats'][r]['owned']
                ,'player_id':json_stats['player_stats'][r]['player_id']
                ,'points':json_stats['player_stats'][r]['points']
                ,'price':json_stats['player_stats'][r]['price']
                ,'price_change':json_stats['player_stats'][r]['price_change']
                ,'total_price_change':json_stats['player_stats'][r]['total_price_change']
                ,'total_points':json_stats['player_stats'][r]['total_points']
                ,'position1':json_stats['positions'][0]['position']
                ,'position2':p2
                ,'avg3':json_stats['player_stats'][r]['avg3']
                ,'score_p1':score_p1
                ,'score_p2':score_p2
                ,'team':json_stats['team']['name']
                ,'team_abbr':json_stats['team']['abbrev']
                ,'minutes_played':json_stats['player_stats'][r]['minutes_played']
                         }
            except:
                data = {'first_name': [json_stats['first_name']] 
                ,'last_name': [json_stats['last_name']]            
                ,'round':json_stats['player_stats'][r]['round']
                ,'owned':0
                ,'player_id':json_stats['player_stats'][r]['player_id']
                ,'points':0
                ,'price':0
                ,'price_change':0
                ,'total_price_change':0
                ,'total_points':0
                ,'position1':json_stats['positions'][0]['position']
                ,'position2':p2
                ,'avg3':0
                ,'score_p1':score_p1
                ,'score_p2':score_p2
                ,'team':json_stats['team']['name']
                ,'team_abbr':json_stats['team']['abbrev']
                ,'minutes_played':0
                         }
            
            data_out = pd.DataFrame(data)
            
            if (e ==0):  
                data_out_final = data_out
                e = e + 1
            else:
                #data_out_final = data_out_final.append(data_out)
                data_out_final = pd.concat([data_out_final,data_out],ignore_index = True)
                
        
    except:
        print('no player maybe')
        
######################### CALCS

print('b/e calc')
magic_no = 5588.8

data_out_final['run_date'] = str(datetime.datetime.now())
        
data_out_final['position2'] = data_out_final['position2'].fillna('') 
        
data_out_final['val_set'] = 0
data_out_final.loc[data_out_final['price_change']==0,'val_set'] = data_out_final.loc[data_out_final['price_change']==0]['price']  

data_out_final['val_set2'] = 0
data_out_final.loc[data_out_final['points']==0,'val_set2'] = data_out_final.loc[data_out_final['points']==0]['price']  

data_out_final['val_flex'] = 0
data_out_final.loc[data_out_final['price_change']!=0,'val_flex'] = 0.75*(data_out_final.loc[data_out_final['price_change']!=0]['price']  - data_out_final.loc[data_out_final['price_change']!=0]['price_change'])+0.25*magic_no* data_out_final.loc[data_out_final['price_change']!=0]['avg3']

data_out_final['val_flex2'] = 0
data_out_final.loc[data_out_final['points']!=0,'val_flex2'] = 0.75*(data_out_final.loc[data_out_final['points']!=0]['price']  - data_out_final.loc[data_out_final['points']!=0]['price_change'])+0.25*magic_no* data_out_final.loc[data_out_final['points']!=0]['avg3']


data_out_final['deflate_factor'] = 0

all_rounds = data_out_final['round'].unique()
new_comp = 237931300 #data_out_final['price'].sum()

#test
#data_out_final.loc[data_out_final['round']==rr-1,'price'].sum()

for rr in all_rounds:
    print(rr)
    new_comp = data_out_final.loc[data_out_final['round']==rr-1,'price'].sum()
    
    if rr == 1 or rr ==2:
        data_out_final.loc[data_out_final['round']==rr , 'deflate_factor'] = 1
        
    elif rr != max(all_rounds):
        temp_factor = (new_comp - sum(data_out_final.loc[data_out_final['round']==rr , 'val_set']) ) / sum(data_out_final.loc[data_out_final['round']==rr , 'val_flex'])
        data_out_final.loc[data_out_final['round']==rr , 'deflate_factor'] = temp_factor
        
    elif rr == max(all_rounds):
        temp_factor = (new_comp - sum(data_out_final.loc[data_out_final['round']==rr-1 , 'val_set']) ) / sum(data_out_final.loc[data_out_final['round']==rr-1 , 'val_flex'])
        
        if temp_factor == temp_factor:        
            data_out_final.loc[data_out_final['round']==rr , 'deflate_factor'] = temp_factor
        else:
            temp_factor2 = (new_comp - sum(data_out_final.loc[data_out_final['round']==rr-1 , 'val_set2']) ) / sum(data_out_final.loc[data_out_final['round']==rr-1 , 'val_flex2'])
            data_out_final.loc[data_out_final['round']==rr , 'deflate_factor'] = temp_factor2

data_out_final['score_p1_imply'] = data_out_final['score_p1']
data_out_final.loc[data_out_final['score_p1']==0,'score_p1_imply'] = data_out_final.loc[data_out_final['score_p1']==0,'price'] / magic_no

data_out_final['score_p2_imply'] = data_out_final['score_p2']
data_out_final.loc[data_out_final['score_p2']==0,'score_p2_imply'] = data_out_final.loc[data_out_final['score_p2']==0,'price'] / magic_no

data_out_final['price_p1'] = data_out_final['price']-data_out_final['price_change']

data_out_final['breakeven'] =  ((data_out_final['price_p1']-0.75*data_out_final['price_p1']*data_out_final['deflate_factor'])/(magic_no*0.25*data_out_final['deflate_factor'])*3)-data_out_final['score_p1_imply']-data_out_final['score_p2_imply']