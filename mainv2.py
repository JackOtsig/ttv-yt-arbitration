import argparse, os, json, datetime
from Twitch import get_links, download_individual, get_dur
from Video import load_clip, render_video, correct_lengths, create_intro, create_outro
from Youtube import upload, upload_time
from Thumbnail import get_screenshot




os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Plan:
    def __init__(self, args, username):
        self.videos = []
        self.args = args
        self.args.username = username
        self.pname = '[ '+self.args.username+' ]  '
        if self.args.v:
            print(self.pname, 'starting...')
        self.read_masterfile()
        self.check_quota()
        if args.f:
            self.init_folders()
    
    def check_quota(self):
        if self.masterfile['streamers'][self.args.username]['quota'] != str(datetime.date.today()):
            self.masterfile['streamers'][self.args.username]['quota'] = 10000
            if self.args.v:
                print(self.pname, 'quota reset')
    
    def init_folders(self):
        ufol = './data/'+self.args.username.lower()
        os.mkdir(ufol)
        os.mkdir(ufol+'/clips')
        os.mkdir(ufol+'/thumbnail')
        os.mkdir(ufol+'/videos')
        if self.args.v:
            print(self.pname, 'folders created')
    
    def write_masterfile(self):
        with open('./masterfile.json', 'w') as f:
            obj = json.dumps(self.masterfile)
            print(self.masterfile)
            f.write(obj)
            if self.args.v:
                print(self.pname, 'masterfile written')

    def read_masterfile(self):
        with open('./masterfile.json') as f:
            masterfile = json.load(f)
            self.masterfile = masterfile
            if self.args.v:
                print(self.pname, 'read masterfile')
    
    def get_clips(self):
        self.clips = []
        links = get_links(self.args.username)
        if self.args.v:
            print(self.pname, len(links), 'links gotten')
        iterator = 1
        os.chdir('./data/'+self.args.username.lower()+'/clips/')
        for link in links:
            self.clips.append(Clip(self.args, link))
            if self.args.v:
                name = self.clips[-1].path.split('/')
                if self.args.v:
                    print(self.pname, 'downloaded', iterator, 'of', len(links),':', name[-1])
            iterator += 1
            clip_iterator = 0
        for clip in self.clips:
            if clip.incom:
                self.clips.remove(clip)
                if self.args.v:
                    clip_iterator += 1
                    print(self.pname, 'clip removed')
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    def plan_videos(self):
        duration = 0
        clips = []
        identifier = 0
        for clip in self.clips:
            if duration + clip.duration < 9.5*60:
                clips.append(clip)
                duration += clip.duration
                if self.args.v:
                    print(self.pname, round(clip.duration, 2), '-->', round(duration/60, 2))
            else:
                if self.masterfile['streamers'][self.args.username]['quota'] >= 1600:
                    if self.args.v:
                        print(self.pname, identifier, 'videos planned')
                    self.videos.append(Video(self.args, clips, identifier))
                    duration = 0
                    clips = []
                    identifier += 1
                else:
                    if self.args.v:
                        print(self.pname, 'quota too low, rendering what is here')



class Video:
    def __init__(self, args, clips, identifier):
        self.args = args
        self.clips = clips
        self.pname = '[ '+self.args.username+' ]'
        self.identifier = identifier
        self.read_masterfile()
        clip_identifier = 0
        while True:
            try:
                self.screenshot = get_screenshot(self.args, self.clips[clip_identifier].path, self.identifier)
                break
            except:
                clip_identifier += 1
        if self.args.v:
            print(self.pname, 'screenshot gotten')
        self.clips = correct_lengths(args, self.clips)
        self.secret = self.masterfile['streamers'][self.args.username]['installed']
    
    def read_masterfile(self):
        with open('./masterfile.json') as f:
            masterfile = json.load(f)
            self.masterfile = masterfile
            if self.args.v:
                print(self.pname, 'read masterfile')
    
    def as_objs(self):
        self.objs = []
        for clip in self.clips:
            clip.convert_obj()
            if clip.obj:
                self.objs.append(clip.obj)
            else:
                self.clips.remove(clip)
        if self.args.v:
            print(self.pname, len(self.objs), 'objects converted')
    
    def finish_objs(self):
        for obj in self.objs:
            obj.close()
        for clip in self.clips:
            clip.close_obj()
            clip.delete()
        if self.args.v:
            print(self.pname, len(self.clips), 'clips deleted')

    def render_video(self):
        self.as_objs()
        self.objs[0] = create_intro(self.args, self.objs[0])
        self.objs[1] = create_outro(self.args, self.objs[1])
        self.path = render_video(self.objs, self.identifier, self.args)
        self.finish_objs()
        
    def upload_video(self):
        publish_time = upload_time(self.identifier)
        video_title = upload(self.args, self.path, publish_time, self.identifier, self.secret, self.masterfile['streamers'][self.args.username]['channel'])
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Clip:
    def __init__(self, args, link):
        self.args = args
        self.pname = '[ '+self.args.username+' ]'
        self.link = link
        self.incom = False
        self.obj = None
        self.download_clip()
        self.get_duration()
    
    def download_clip(self):
        self.path = download_individual(self.args, self.link)
    
    def convert_obj(self):
        try:
            self.obj = load_clip(self.path)
        except:
            self.obj = None
    def close_obj(self):
        if self.obj:
            self.obj.close()
    
    def delete(self):
        try:
            os.remove(self.path)
            print(os.listdir('./data/'+self.args.username+'/clips/'))
        except:
            print('file not found (idk)')
    
    def get_duration(self):
        self.duration = get_dur(self.path)