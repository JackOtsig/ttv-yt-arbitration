import datetime, time, asyncio, json, os, argparse
from mainv2 import Plan

os.chdir(os.path.dirname(os.path.abspath(__file__)))
#XQC, LVNDMARK, TrainwrecksTV, Summit1G
exclude = ['Summit1G', 'LVNDMARK', 'TrainwrecksTV']

parser = argparse.ArgumentParser()
parser.add_argument('-v', action='store_true')
parser.add_argument('-t', action='store_true')
parser.add_argument('-f', action='store_true')
parser.add_argument('-a', action='store_true')

async def acquire_clips(args, username):
    plan = Plan(args, username)
    plan.get_clips()
    return plan

async def circulate_film(video):
    video.upload()

async def start():
    args = parser.parse_args()
    with open('./masterfile.json') as f:
        masterfile = json.load(f)
    if not args.username:
        plans = []
        for username in list(masterfile['streamers'].keys()):
            if username not in exclude:
                plans.append(asyncio.create_task(acquire_clips(args, username)))
                print('starting %s' % username)
                plans_group = asyncio.gather(*plans)
                print(1)
                await plans_group
                print(2)
                print(plans_group)
                for plan in plans_group:
                    print(3)
                    plan.plan_videos()
                    print('planned for %s' % plan.username)
                    for video in plan.videos:
                        print('rendering for %s' % username)
                        video.render_video()
                for plan in plans_group:
                    uploads = []
                    for video in plan.videos:
                        print('uploading for %s' % username)
                        uploads.append(asyncio.create_task(circulate_film(video)))
                        masterfile['streamers'][plan.username]['quota'] -= 1600
                        masterfile['streamers'][plan.username]['total_uploads'] += 1
                    masterfile['streamers'][plan.username]['last_upload'] = str(datetime.date.today())
                    uploads_group = asyncio.gather(*uploads)
                    await uploads_group

def startv2(args):
    
    with open('./masterfile.json') as f:
        masterfile = json.load(f)
        plans = []
        for username in list(masterfile['streamers'].keys()):
            if username not in exclude:
                print('starting %s' % username)
                parser = argparse.ArgumentParser()
                parser.add_argument('-v', action='store_true')
                parser.add_argument('-t', action='store_true')
                parser.add_argument('-f', action='store_true')
                parser.add_argument('-a', action='store_true')
                parser.add_argument('--username', type=str, default=username)
                args = parser.parse_args()
                args.v = True
                args.t = True
                plans.append(Plan(args, username))
    for plan in plans:
        print('getting clips for %s' % plan.args.username)
        plan.get_clips()
        if len(plan.clips) <= 40:
            continue
        print(os.listdir('./data/'+plan.args.username+'/clips/'))
        print('planning for %s' % plan.args.username)
        plan.plan_videos()
        for video in plan.videos:
            print('rendering for %s' % plan.args.username)
            print(os.listdir('./data/'+plan.args.username+'/clips/'))
            print('intro %s \noutro %s' % (str(video.clips[0].duration), str(video.clips[-1].duration)))
            video.render_video()
            print('uploading for %s' % plan.args.username)
            print(os.listdir('./data/'+plan.args.username+'/clips/'))
            video.upload_video()
            masterfile['streamers'][plan.args.username]['quota'] -= 1600
            masterfile['streamers'][plan.args.username]['total_uploads'] += 1
        masterfile['streamers'][plan.args.username]['last_upload'] = str(datetime.date.today())
        with open('./masterfile.json', 'w') as f:
            obj = json.dumps(masterfile)
            f.write(obj)
        print('%s complete with %s videos rendered and uploaded' % (plan.args.username, len(plan.videos)))
            


def main():
    args = parser.parse_args()
    if args.a:
        asyncio.run(start())
    else:
        startv2(args)
if __name__ == "__main__":
    main()