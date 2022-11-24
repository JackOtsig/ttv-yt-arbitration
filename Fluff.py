import random, datetime, json, urllib, requests
#from bs4 import BeautifulSoup

def create_title(username):
    types = 1
    exclude_basic = False
    if types > 1:
        type = random.randint(0,types)
    else:
        type = 0
    if type == 0 and not exclude_basic:
        title = username.upper()+' STREAM HIGHLIGHTS '+datetime.datetime.now().strftime('%m-%d')
    return title

def create_description(username, link):
    twitch_link = 'https://www.twitch.tv/'+username.lower()
    description = 'THANKS FOR WATCHING\n'+username+"'s channel: "+twitch_link+'\n\nSUBSCRIBE: '+link+'/?sub_confirmation=1'
    return description

def create_tags(username):
    # with urllib.request.urlopen('https://rapidtags.io/api/generator?query='+username+'&type=YouTube') as request:
    #     data = json.loads(request.read().decode())
    #     tags = data['tags']
    tags = [
        username,
        'stream',
        'highlights',
        'funny moments',
        'clips',
        'twitch',
        'live',
        'react'
        ]
    return tags

def create_thumbnail(username, iterator):
    path = './data/'+username.lower()+'/thumbnail/screenshot'+str(iterator)+'.png'
    return path



temp_expletive_list = [
    'omg'


]

temp_question_list = [
    'wtf',
    'what is that',
    'he ate what',
    'what is that smell'
]

temp_action_list = [
    ' gets crazy'
]

def test_title(username, identifier):
    pass
