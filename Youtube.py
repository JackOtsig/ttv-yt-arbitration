import datetime, os, json
from Google import Create_Service
from googleapiclient.http import MediaFileUpload
from Fluff import create_title, create_description, create_tags, create_thumbnail



def create_fluff(username, iterator, link):
    category = 23
    title = create_title(username)
    description = create_description(username, link)
    tags = create_tags(username)
    thumbnail = create_thumbnail(username, iterator)
    return category, title, description, tags, thumbnail


def upload(args, video_location, publish_time, iterator, secret_data, link):
    os.chdir('./data/'+args.username.lower())
    API_NAME = 'youtube'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    secret = Secret(secret_data)
    if args.v:
        print('temp json secret made')
    service = Create_Service(secret.path[2:], API_NAME, API_VERSION, SCOPES)
    category, title, description, tags, thumbnail = create_fluff(args.username, iterator, link)
    thumbnail = shorten_name(thumbnail)
    print('thumbnail', thumbnail)
    title += ' '+str(iterator)
    request_body = {
    'snippet': {
        'categoryI': category,
        'title': title,
        'description': description,
        'tags': tags
    },
    'status': {
        'privacyStatus': 'private',
        'publishAt': publish_time,
        'selfDeclaredMadeForKids': False
    },
    'notifySubscribers': False
    }
    video_location = shorten_name(video_location)
    print('video location', video_location)
    video = MediaFileUpload(video_location)
    response_upload = service.videos().insert(
    part = 'snippet,status',
    body = request_body,
    media_body = video
    ).execute()
    service.thumbnails().set(
    videoId = response_upload.get('id'),
    media_body = MediaFileUpload(thumbnail)
    ).execute()
    secret.delete()
    if args.v:
        print('uploaded', iterator)
    return title

def upload_times(videos):
    times = []
    now = datetime.datetime.now()
    until_midnight = (24 - int(datetime.datetime.now().hour))
    offset = 0
    timing = until_midnight/videos
    if videos > 1:
        while videos > 0:
            time = now + datetime.timedelta(hours=offset)
            times.append(time.isoformat())
            offset += timing
            videos -= 1
    else:
        times.append(now.isoformat())
    return times

def upload_time(identifier):
    now = datetime.datetime.now()
    if identifier == 0:
        return now.isoformat()
    else:
        offset = 0
        until_midnight = (24 - int(datetime.datetime.now().hour))
        offset += until_midnight / identifier
        time = now + datetime.timedelta(hours=offset)
        return time.isoformat()




class Secret:
    def __init__(self, data):
        dictionary = {'installed': data}
        self.path = './client_secret.json'
        with open(self.path, 'w') as f:
            obj = json.dumps(dictionary)
            f.write(obj)
    
    def delete(self):
        os.remove(self.path)

def shorten_name(name):
    name_split = name.split('/')
    for i in range(2): name_split.pop(1)
    last = name_split[-1]
    fname= ''
    for directory in name_split:
        fname+= directory
        if directory != last:
            fname+= '/'
    return fname