
#import os
import requests
from bs4 import BeautifulSoup
import json
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
import pandas as pd
import datetime

#####CHANGE ROUND######
r_sc_url='https://supercoach.heraldsun.com.au/2024/api/afl/classic/v1/players/2?embed=notes,odds,player_stats,player_match_stats,positions,trades'
r_res = requests.get(r_sc_url)    
r_soup = BeautifulSoup(r_res.text, 'html.parser')
r_raw_stats = str(r_soup).encode('utf8')
r_json_stats = json.loads(r_raw_stats)
len(r_json_stats['player_stats'])

#####CHANGE ROUND######
para_round = len(r_json_stats['player_stats']) - 1

def get_sc_token():
    # Credentials to generate token - view via developer mode on SC site
    client_id = ''
    client_secret = ''
    get_token_url = 'https://supercoach.heraldsun.com.au/2024/api/afl/classic/v1/access_token'
                     #https://supercoach.heraldsun.com.au/2023/api/afl/classic/v1/access_token
    #There is an access token object in network developer when logging in

    # Supercoach credentials
    sc_user = ''
    sc_pass = ''

    # Create token
    #oauth = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))
    #token = oauth.fetch_token(token_url=get_token_url,
    #        username=sc_user, password=sc_pass, client_id=client_id,
    #        client_secret=client_secret)
    
    # Get from developer mode when opening SC site
    token = ''
    data = {
        'grant_type': 'social',
        'username': sc_user,
        'password': sc_pass,
        'scope': '',
        'client_id': client_id,
        'client_secret': '',
        'service': 'auth0',
        'token': token
        }

    # Create token
    response = requests.post(get_token_url, data=data)
    tokens = json.loads(response.text)
    sc_token = tokens['access_token']
    return sc_token

    # Get token value from the Access_Token key
    #sc_token = token["access_token"]
    #return sc_token

sc_token = get_sc_token()





def get_team(user):
    e = 0
    try:    
        #print('iter:'+ str(user_data_out_final.loc[user_data_out_final['user_team_id']==user,['raw_position']].values) +', user:' + str(user)  )
        team_res = requests.get(url = 'https://supercoach.heraldsun.com.au/2024/api/afl/classic/v1/userteams/'+str(user)+'/statsPlayers?round='+str(para_round)
                           , headers = {
                                   "accept": "application/json",
                                   "authorization": "Bearer " + sc_token,
                                   "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"99\", \"Microsoft Edge\";v=\"99\"",
                                   "sec-ch-ua-mobile": "?0",
                                   "sec-ch-ua-platform": "\"Windows\""
                                   }
                           ,params = {"referrer": "https://supercoach.foxsports.com.au/",
                                   "referrerPolicy": "strict-origin-when-cross-origin",
                                   "body": '',
                                   "method": "GET",
                                   "mode": "cors",
                                   "credentials": "include"}                   
                             )
        
        
        # Parse the response as HTML using the BeautifulSoup library
        team_soup = BeautifulSoup(team_res.text, 'html.parser')
                
        # Format it to JSON
        raw_team_stats = str(team_soup).encode('utf8')
                
        # Parse to JSON to make extracting key values much easier
        json_team_stats = json.loads(raw_team_stats)
        
        for p in range(0,30):
        
            team_data = {'user_team_id': json_team_stats['stats'][0]['user_team_id']   
            ,'round': [json_team_stats['stats'][0]['round']]
            ,'points': json_team_stats['stats'][0]['points']           
            ,'position': json_team_stats['stats'][0]['position']
            ,'total_points': json_team_stats['stats'][0]['total_points']
            ,'player_id': json_team_stats['players'][p]['player_id']
            ,'player_position': json_team_stats['players'][p]['position']
            ,'price': json_team_stats['players'][p]['picked'] 
            }
        
            team_data_out = pd.DataFrame(team_data)
            
            if (e == 0):  
                team_data_out_final = team_data_out
                e = e + 1
            else:
                team_data_out_final = pd.concat([team_data_out_final,team_data_out],ignore_index = True)
                                
        return team_data_out_final
        
        
    except:
            print('not a team')


# also get via developer mode 
my_team = get_team()

my_team['run_date'] = str(datetime.datetime.now())



