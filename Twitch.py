import os, subprocess, shlex, json, re

dlnum = 60

def reassemble_string(raw_string, r):
    if r:
        real_string = raw_string[2:-3]
    else:
        real_string = raw_string
    final_string = ''
    prev_char = None
    for character in real_string:
        if character == '\\':
            final_string += '/'
        elif character == '"' and prev_char == '\\':
            final_string += "'"
        else:
            final_string += character
        prev_char = character
    return final_string


def get_links(username):
    while True:
        try:
            clips = []
            clips_bytes = subprocess.run(['twitch-dl', 'clips', username.lower(), '-j', '-l', str(dlnum), '-P', 'last_day'], capture_output=True)
            clips_string = reassemble_string(str(clips_bytes.stdout), True)
            clips_string = reassemble_string(clips_string, False)
            clips_json = json.loads(clips_string)
        except:
            pass
        break
    for clip in clips_json:
        clips.append(clip['url'])
    return clips

def rectify_name(name):
    righteous_name = ''
    character_iterator = 0
    for character in name:
        if character == '\\':
            if name[character_iterator+1] != 'x'and name[character_iterator+4] != 'x':
                righteous_name += '\\\\'
            else:
                righteous_name += '\\'
        else:
            righteous_name += character
        character_iterator += 1
    emojis = re.findall(r'\\x..\\x..\\x..\\x..', righteous_name)
    for emoji in emojis:
        righteous_name.replace(emoji, emoji.encode('utf-8').decode('utf-8'), 1)
    return righteous_name

def download_individual(args, link):
    path = './data/'+args.username.lower()+'/clips/'
    command = shlex.split('youtube-dl '+link)
    twdl = subprocess.run(command, capture_output=True)
    output = str(twdl.stdout)
    name_start = re.search('\[download\] ', output)
    name_end = re.search('\.mp4', output)
    start_span = name_start.span()
    end_span = name_end.span()
    name = output[start_span[1]:end_span[1]]
    if 'Destination: ' in name:
        name = name[13:]
    name = rectify_name(name)
    return path+name

def get_dur(path):
    path_s = path.split('/')
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path_s[-1]], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    duration = 0
    try:
        duration = float(result.stdout)
    except:
        pass
    return duration