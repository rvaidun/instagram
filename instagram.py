import requests
import json
import numpy as np
import time
from dotenv import load_dotenv, dotenv_values
import os
from datetime import date
import sys
load_dotenv()
config = dotenv_values(".env")

if (config.keys() < {"FOLLOWINGHASH","FOLLOWERHASH","REQUEST_ID", "SESSION_ID"}):
    print("Please populate the .env file")
    sys.exit()
    
session_id = os.environ['SESSION_ID']
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
    'cookie': f'sessionid={session_id};',
}

followinghash = os.environ['FOLLOWINGHASH']
followerhash = os.environ['FOLLOWERHASH']
req_id = os.environ['REQUEST_ID']

def nextFew(nextpageKey, hash, h):
    params = (
        ('query_hash', hash),
        ('variables',
         f'{{"id":{req_id},"include_reel":true,"fetch_mutual":false,"first":24,"after":"{nextpageKey}"}}'),
    )
    response = requests.get('https://www.instagram.com/graphql/query/',
                     headers=h, params=params)
    return json.loads(response.text)

def getFollowersandFollowing(hash, e):

    params = (
        ('query_hash', hash),
        ('variables',
         f'{{"id":{req_id},"include_reel":true,"fetch_mutual":true,"first":24}}'),
    )

    followerUsers = []
    response = requests.get('https://www.instagram.com/graphql/query/',
                     headers=headers, params=params)
    j = json.loads(response.text)
    while j['data']['user'][e]['page_info']['has_next_page'] == True:
        followerUsers.append(
            [u['node']['username'] for u in j['data']['user'][e]['edges']])
        users = [u['node']['username']
                 for u in j['data']['user'][e]['edges']]
        print(users)
        j = nextFew(j['data']['user'][e]['page_info']
                    ['end_cursor'], hash, headers)
        time.sleep(1)
    followerUsers.append(
        [u['node']['username'] for u in j['data']['user'][e]['edges']])
    users = [u['node']['username']
             for u in j['data']['user'][e]['edges']]
    print(users)
    f = []
    for ul in followerUsers:
        for u in ul:
            f.append(u)
    print(len(f))
    return f


if __name__ == "__main__":
    followers = getFollowersandFollowing(followerhash, "edge_followed_by")
    following = getFollowersandFollowing(followinghash, 'edge_follow')
    print(f"You have {len(followers)+1} followers")
    print(f"You have {len(following)+1} people following you")
    main_list = np.setdiff1d(following, followers)
    younotfollowing = np.setdiff1d(followers, following)
    print(f"These users are not following you")
    print(main_list)

    today = date.today()
    if not os.path.exists('saves'):
        os.makedirs('saves')
    with open(f"saves/{today}notfollowingyou.txt", "w") as f:
        for u in main_list:
            f.write("Bye https://www.instagram.com/" + u + "/\n")
    with open(f"saves/{today}younotfollowing.txt", "w") as f:
        for u in younotfollowing:
            f.write("https://www.instagram.com/" + u + "/\n")
