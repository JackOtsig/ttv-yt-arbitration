from moviepy.editor import *
from skimage import filters
import datetime



def blur(image):
    return filters.gaussian(image.astype(float), sigma=6)

def load_clip(path):
    obj = VideoFileClip(path)
    return obj


def render_video(clips, identifier, args):
    video_path = './data/'+args.username.lower()+'/videos/'
    if args.t:
        clips = clips[0:1]+clips[-2:-1]
    video = concatenate_videoclips(clips)
    video_name = video_path+str(datetime.date.today())+'-'+str(identifier)+'.avi'
    video.write_videofile(video_name, fps=30, codec='libx264', audio_codec='aac', bitrate='650k', temp_audiofile='/tmp/tempaudio.m4a', remove_temp=True)
    return video_name


def create_intro(args, clip):
    logo_path = './data/imgs/'+args.username.lower()+'.png'
    first_clip = clip.crossfadein(5.0)
    logo_clip = ImageClip(logo_path).set_duration(5.0).resize(0.25).set_position('center').on_color(size=first_clip.size,color=(0,0,0))
    intro = CompositeVideoClip(size=first_clip.size,clips=[logo_clip, first_clip])
    intro = concatenate_videoclips([logo_clip, intro])
    logo_clip.close()
    return intro

def create_outro(args, clip):
    o_last_clip = clip.subclip(0,-10.0).crossfadein(2.0)
    last_clip = clip.subclip(-10.0, clip.duration).fl_image( blur )
    subscribe_clip = TextClip('SUBSCRIBE', method='label', color='white', font='Amiri-Bold', fontsize=150, stroke_color='black', stroke_width=3).set_duration(10.0).set_position(('center', last_clip.h/9))
    formore_clip = TextClip('for More '+args.username.upper(), method='label', color='white', font='Amiri-Bold', fontsize=100, kerning=3, stroke_color='black', stroke_width=3).set_duration(10.0).set_position(('center', last_clip.h/4.5))
    part_outro = CompositeVideoClip([last_clip, subscribe_clip, formore_clip])
    outro = concatenate_videoclips([o_last_clip, part_outro])
    subscribe_clip.close()
    formore_clip.close()
    return outro

def correct_lengths(args, clips):
    changedi = False
    changedo = False
    print(clips[0].duration)
    while clips[0].duration < 11:
        mvclip = clips.pop(0)
        clips.insert(10, mvclip)
        print('moved')
        changedi = True
    if args.v and changedi:
        print('intro clip corrected')
    while clips[-1].duration < 11:
        mvclip = clips.pop(-1)
        clips.insert(-10, mvclip)
        print('moved')
        changedo = True
    if args.v and changedo:
        print('outro clip corrected')
    if args.v:
        print('intro %s \noutro %s \n%s' % (str(clips[0].duration), str(clips[-1].duration), str(len(clips))))
    return clips