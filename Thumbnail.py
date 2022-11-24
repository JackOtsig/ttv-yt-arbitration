import random, cv2

scale = 50

def get_screenshot(args, path, identifier):
    frames = []
    current_frame = 0
    cam = cv2.VideoCapture(path)
    ret, frame = cam.read()
    while ret and current_frame < 10:
        frames.append(frame)
        ret, frame = cam.read()
        current_frame += 1
    frame_num = random.randint(0,len(frames)-1)
    width = int(frames[frame_num].shape[1] * scale / 100)
    height = int(frames[frame_num].shape[0] * scale / 100)
    screenshot = cv2.resize(frames[frame_num], (width, height))
    name = './data/'+args.username.lower()+'/thumbnail/screenshot'+str(identifier)+'.png'
    cv2.imwrite(name, screenshot)
    return name