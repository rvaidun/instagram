import requests
from dotenv import load_dotenv, dotenv_values
import os
from datetime import date
import sys
import progressbar
import numpy as np
import sys

load_dotenv()
config = dotenv_values(".env")
opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
if "-c" in opts:
    session_id = input("Enter session ID: ")
    req_id = input("Enter request ID: ")
    username = input("Enter username: ")
    app_id = input("Enter app ID: ")
else:
    session_id = os.environ['SESSION_ID']
    req_id = os.environ['REQUEST_ID']
    username = os.environ['USERNAME']
    app_id = os.environ['APP_ID']
headers = {
    'authority': 'i.instagram.com',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    'x-ig-app-id': app_id,
    'sec-gpc': '1',
    'origin': 'https://www.instagram.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.instagram.com/',
    'accept-language': 'en-US,en;q=0.9',
    'cookie': f'sessionid={session_id}',
}


acc_info = requests.get(f'https://www.instagram.com/{username}/?__a=1', headers=headers)
acc_info = acc_info.json()
followers_count = acc_info['graphql']['user']['edge_followed_by']['count']
following_count = acc_info['graphql']['user']['edge_follow']['count']

following = requests.get(f'https://i.instagram.com/api/v1/friendships/{req_id}/following/?count=10000', headers=headers)
test = following.json()
followers = requests.get(f'https://i.instagram.com/api/v1/friendships/{req_id}/followers/?count=10000', headers=headers)

followingjson = following.json()
followersjson = followers.json()

followingusername = [x['username'] for x in followingjson['users']]
followersusername = [x['username'] for x in followersjson['users']]

not_following_you = np.setdiff1d(followingusername, followersusername)
if (len(not_following_you) > 0):
    print("These are the users not following you")
    print(not_following_you)
else:
    print("No one is not following you back!")
younotfollowing = np.setdiff1d(followersusername, followingusername)

today = date.today()
if not os.path.exists('saves'):
    os.makedirs('saves')

dddd = f'saves/{username}'
if not os.path.exists(dddd):
    os.makedirs(dddd)

with open(f"saves/{acc_info['graphql']['user']['username']}/{today}notfollowingyou.txt", "a+") as f:
    for u in not_following_you:
        f.write("https://www.instagram.com/" + u + "/\n")
with open(f"saves/{acc_info['graphql']['user']['username']}/{today}younotfollowing.txt", "a+") as f:
    for u in younotfollowing:
        f.write("https://www.instagram.com/" + u + "/\n")

discord_webhook = config['WEBHOOK']
# post users not following me and users I don't follow back to discord
if (len(not_following_you) > 0):
    s = ""
    for u in not_following_you:
        s += f"[{u}](https://www.instagram.com/{u}/)\n"
    payload = {
        "username": "Instagram Bot",
        "embeds": [
            {
                "title": f"Users not following you on {today.strftime('%m/%d/%Y')}",
                "description": s,
                "color": 0xdd2a7b
            }
        ]
    }
    requests.post(discord_webhook, json=payload)
else:
    payload = {
        "username": "Instagram Bot",
        "avatar_url": "https://123accs.com/wp-content/uploads/2021/03/instagram-automation-tools.png",
        "content": f"No one is not following you back on {today.strftime('%m/%d/%Y')}",
    }
    requests.post(discord_webhook, json=payload)
