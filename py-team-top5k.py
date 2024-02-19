
#import os
import requests
from bs4 import BeautifulSoup
import json
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
import pandas as pd
import datetime

r_sc_url='https://supercoach.heraldsun.com.au/2023/api/afl/classic/v1/players/2?embed=notes,odds,player_stats,player_match_stats,positions,trades'
r_res = requests.get(r_sc_url)    
r_soup = BeautifulSoup(r_res.text, 'html.parser')
r_raw_stats = str(r_soup).encode('utf8')
r_json_stats = json.loads(r_raw_stats)
len(r_json_stats['player_stats'])

#####CHANGE ROUND######
para_round = len(r_json_stats['player_stats']) - 2

def get_sc_token():
    # Credentials to generate token
    client_id = ''
    client_secret = ''
    get_token_url = 'https://supercoach.heraldsun.com.au/2023/api/afl/classic/v1/access_token'
                     #https://supercoach.heraldsun.com.au/2023/api/afl/classic/v1/access_token
    #There is an access token object in network developer when logging in

    # Supercoach credentials
    sc_user = ''
    sc_pass = ''

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

for para_page in range(1,11):

    user_list = requests.get(url = 'https://supercoach.heraldsun.com.au/2023/api/afl/classic/v1/rankings/userteams/all?period=overall&round='+str(para_round)+'&page='+str(para_page)+'&page_size=100'
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
    user_soup = BeautifulSoup(user_list.text, 'html.parser')
    user_stats = str(user_soup).encode('utf8')
    json_users = json.loads(user_stats)

    #json_users

    for para_user in range(0,100):
        user_data = {'user_team_id': [json_users[para_user]['userTeam']['stats'][0]['user_team_id']]
                ,'position': json_users[para_user]['position'] 
                ,'raw_position': json_users[para_user]['raw_position']         
                }
            
        user_data_out = pd.DataFrame(user_data)
            
        if (para_page == 1 and para_user ==0):  
            user_data_out_final = user_data_out
        else:
            user_data_out_final = user_data_out_final.append(user_data_out)

e = 0
for user in user_data_out_final['user_team_id']:

    try:    
        print('iter:'+ str(user_data_out_final.loc[user_data_out_final['user_team_id']==user,['raw_position']].values) +', user:' + str(user)  )
        team_res = requests.get(url = 'https://supercoach.heraldsun.com.au/2023/api/afl/classic/v1/userteams/'+str(user)+'/statsPlayers?round='+str(para_round)
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
        
            if (e ==0):  
                team_data_out_final = team_data_out
                e = e + 1
            else:
                team_data_out_final = pd.concat([team_data_out_final,team_data_out],ignore_index = True)                
    
    except:
            print('not a team')

team_data_out_final['run_date'] = str(datetime.datetime.now())
