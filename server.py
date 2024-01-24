from slack_bolt import App
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
import ast
import os
from PIL import Image, ImageFile
import time
from config import cconfig
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
import re
import requests
from threading import Thread


### slack ###

cur_channel = 'eemune'
channel_id = cconfig[cur_channel]['channel_id']
bot_token = cconfig[cur_channel]['bot_token']
app_token = cconfig[cur_channel]['app_token']

os.environ['SLACK_APP_TOKEN'] = app_token
os.environ['SLACK_BOT_TOKEN'] = bot_token
os.environ['SLACK_CHANNEL'] = channel_id


global app_slack
app_slack = App(token=os.environ['SLACK_APP_TOKEN'])


slack_client = WebClient(token=bot_token)


ImageFile.LOAD_TRUNCATED_IMAGES = True


@app_slack.event("message")
def got_message(client, body):
    text = body.get('event').get('text')
    print(text)

    if (text == "찍어줘"):
        fourcut(client, body)
    elif (text == "찍을래"):
        fourcut_url(client, body)

### main function ###


@app_slack.message(re.compile("찍어줘"))
def fourcut(client, body):
    # is_bot = body.get("authorizations")[0].get("is_bot")
    # if(is_bot == True):
    #     print("was")
    #     return
    # say("카메라 꺼내는 중...")
    print(body.get("authorizations")[0])
    send_message_to_channel("카메라 꺼내는 중...")
    photo_card_src = make_photo_card(body)
    here = parse_channel_id(body)
    print(here)
    send_message_to_channel("사진 찍는 중...")
    send_img_to_channel(photo_card_src, here, client)


@app_slack.message(re.compile("찍을래"))
def fourcut_url(client, body):
    send_message_to_channel("아래 링크에 접속하세요👇👇")
    # say("아래 링크에 접속하세요👇👇")
    send_message_to_channel("https://www.hackafourcut.com")

### parse channel id from body, and then return it ###


def parse_channel_id(body):
    return body['event']['channel']


### whole sequence of making photo card, and tnen return src of that photo card ###
def make_photo_card(body):
    try:
        file_objs = parse_file_object(body)
        # print(file_objs)
        img_srces = save_imgs_from(file_objs)

        photo_card_src = paste_imgs_to_frame(img_srces)
        print(photo_card_src)
        return photo_card_src
    except:
        return None


### parse file object from body ###
def parse_file_object(body):
    return body["event"]["files"]


### request img from salck server and write file in local, and thel return src of that ###
def save_imgs_from(file_objs):
    file_srces = []

    for obj in file_objs:
        url = obj["url_private_download"]
        img_name = obj["name"]
        file_src = f'./static/img/base_imgs/base_{img_name}'
        file_srces.append(file_src)
        image_response = requests.get(
            url, headers={"Authorization": f"Bearer {bot_token}"}, stream=True)
        with open(file_src, 'wb') as f:
            for chunk in image_response.iter_content(1024):
                f.write(chunk)
    return file_srces


## return pil object at src which recieved ###
def get_pil_imgs_at(img_srces):
    imgs = []
    for img_src in img_srces:
        now_img = Image.open(img_src)
        imgs.append(now_img)
    return imgs


# def paste_imgs_to_frame(img_srces, frame_src='./static/img/frames/frame_blue.png', card_id="slack"):
#     print("GOGOGO")
#     frame_src = frame_src
#     fore_src = './static/img/frames/frame_foreground.png'
#     frame_size = {'width': 1193, 'height': 3602}
#     frame = Image.open(frame_src).resize(
#         (frame_size['width'], frame_size['height']))
#     frame_fore = Image.open(fore_src).convert("RGBA").resize(
#         (frame_size['width'], frame_size['height']))
#     imgs = get_pil_imgs_at(img_srces)
#     resized_imgs = get_resized_imgs(imgs)
#     new_img = Image.new(
#         "RGB", (frame_size['width'], frame_size['height']), "#ffffff")

#     for i in range(4):
#         start_point_y = 375
#         start_point_x_left = 58
#         # start_point_x_right = 1250
#         h_factor = 773
#         new_img.paste(
#             resized_imgs[i], (start_point_x_left, start_point_y+i*h_factor))
#         # new_img.paste(resized_imgs[i], (start_point_x_right, start_point_y+i*h_factor))

#     new_img.paste(frame, (0, 0), frame)
#     new_img.paste(frame_fore, (0, 0), frame_fore)

#     frame_final = Image.new(
#         "RGB", (frame_size['width']*2, frame_size['height']), "#ffffff")
#     frame_final.paste(new_img, (0, 0))
#     frame_final.paste(new_img, (frame_size['width'], 0))

#     final_src = f"./static/img/final_imgs/final_img_{card_id}.png"
#     frame_final.save(final_src)
#     return final_src

def paste_imgs_to_frame(img_srces, frame_src='./static/img/frames/frame_blue.png', card_id="slack"):
    fore_src = './static/img/frames/blue.png'
    frame_size = {'width': 1193, 'height': 3602}
    print("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")

    frame_fore = Image.open(fore_src).convert("RGBA").resize(
        (frame_size['width'], frame_size['height']))
    print(frame_size['width']*2)
    imgs = get_pil_imgs_at(img_srces)
    resized_imgs = get_resized_imgs(imgs)
    new_img = Image.new(
        "RGB", (frame_size['width'], frame_size['height']), "#ffffff")
    frame = Image.new(
        "RGB", (frame_size['width']*2, frame_size['height']), "#ffffff")

    for i in range(4):
        start_point_y = 375
        start_point_x_left = 58
        h_factor = 773
        new_img.paste(
            resized_imgs[i], (start_point_x_left, start_point_y+i*h_factor))

    new_img.paste(frame_fore, (0, 0), frame_fore)
    print(new_img)
    frame.paste(new_img, (0, 0))
    print(frame)
    frame.paste(new_img, (frame_size['width'], 0))
    print(frame)

    final_src = f"./static/img/final_imgs/final_img_{card_id}.png"
    frame.save(final_src)
    return final_src

### recieve bulk of imgs and return them ###


def get_resized_imgs(imgs):
    resized_imgs = []
    for img in imgs:
        resized_img = resize_img(1080, 725, img)
        resized_imgs.append(resized_img)
    return resized_imgs


### resize target_img ###
def resize_img(width, height, target_img):
    now_img = target_img
    if (now_img.width < now_img.height*1080/725):
        now_img = now_img.crop((0, now_img.height*1/2-725/1080*now_img.width *
                               1/2, now_img.width, now_img.height*1/2+725/1080*now_img.width*1/2))
        now_img = now_img.resize((1080, 725))
    else:
        now_img = now_img.crop((now_img.width*1/2-1080/725*now_img.height*1/2,
                               0, now_img.width*1/2+1080/725*now_img.height*1/2, now_img.height))
        now_img = now_img.resize((1080, 725))
    return now_img


def save_img_from_dataurl(path_to_save, dataurl):
    print(dataurl[:100])
    print(len(dataurl) % 4)
    import urllib.request
    urllib.request.urlretrieve(dataurl+"==", path_to_save)

### send img at src to channel which has same id as received channel_id ###


def send_img_to_channel(img_src, cannel_id, client):
    print(img_src)
    if (img_src != None):
        slack_client = WebClient(token=bot_token)
        response = slack_client.files_upload_v2(
            channel=channel_id, file=img_src)
        if (response['ok'] == True):
            send_message_to_channel("찰칵찰칵📸📷")
        else:
            send_message_to_channel("다시 시도하세요.")
    else:
        send_message_to_channel("촬영 실패! 사진 네 장과 함께 '찍어줘'라고 말해 보세요")


def send_message_to_channel(message):
    slack_client = WebClient(token=bot_token)
    slack_client.chat_postMessage(
        channel=channel_id,
        text=message
    )


def change_cur_channel(channel):
    global cur_channel
    cur_channel = channel
    global channel_id
    channel_id = cconfig[cur_channel]['channel_id']
    global bot_token
    bot_token = cconfig[cur_channel]['bot_token']
    global app_token
    app_token = cconfig[cur_channel]['app_token']

    os.environ['SLACK_APP_TOKEN'] = app_token
    os.environ['SLACK_BOT_TOKEN'] = bot_token
    os.environ['SLACK_CHANNEL'] = channel_id

    # app_slack = App(token=os.environ['SLACK_APP_TOKEN'])
    # app_slack.start()


### web ###
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/studio')
def studio():
    return render_template('studio.html', snap_cnt=0, card_id=time.time())


@app.route('/connect_gogo_snap', methods=['GET'])
def connect_gogo_snap():
    snap_cnt = request.args.get("snap_cnt")
    return "<script>location.href='/gogo_snap'</script>"


@app.route('/final')
def final():
    return render_template('final.html')


@app.post('/final_step1')
def final_step1():
    return render_template('final_step1.html')


@app.post('/final_step2')
def final_step2():
    card_id = request.form.get("card_id")
    selected_img_idxes = request.form.get("selected_img_idxes").split(",")
    selected_img_idxes = list(map(int, selected_img_idxes))
    return render_template('final_step2.html', card_id=card_id, selected_img_idxes=selected_img_idxes)


@app.post('/final_step3')
def final_step3():
    card_id = request.form.get("card_id")
    img_idxes = ast.literal_eval(request.form.get("selected_img_idxes"))
    frame_name = request.form.get("frame_name")
    slack_client = WebClient(token=bot_token)
    frame_src = f'./static/img/frames/{frame_name}.png'
    img_srces = [f'./static/img/base_imgs/{card_id}_{img_idxes[0]}.png', f'./static/img/base_imgs/{card_id}_{
        img_idxes[1]}.png', f'./static/img/base_imgs/{card_id}_{img_idxes[2]}.png', f'./static/img/base_imgs/{card_id}_{img_idxes[3]}.png']
    photo_card_src = paste_imgs_to_frame(
        img_srces=img_srces, frame_src=frame_src, card_id=card_id)
    return render_template("final.html", card_id=card_id)


@app.get('/send_img_to_slack')
def send_img_to_slack():
    slack_client = WebClient(token=bot_token)
    card_id = request.args.get("card_id")
    response = slack_client.files_upload_v2(
        channel=channel_id, file=f'./static/img/final_imgs/final_img_{card_id}.png')
    send_message_to_channel(message="찰칵찰칵📸📷")
    return redirect(url_for('index'))


@app.get('/change_frame')
def change_frame():
    # path = "./static/"
    # file_lst = os.listdir(path)
    return render_template("change_frame.html")


@app.post('/change_frame')
def change_frame_post():
    if 'image' not in request.files:
        return '<script>alert("nono"); location.href="/change_frame"</script>'
    image = request.files['image']
    fore_path = f'./static/img/frames/frame_foreground.png'
    image.save(fore_path)
    return '<script>alert("good"); location.href="/change_frame"</script>'


@app.route('/gogo_snap', methods=['GET', 'POST'])
def data_url():
    data_url = request.form.get("gogo_url")
    snap_cnt = int(request.form.get("snap_cnt"))
    card_id = request.form.get("card_id")

    save_src = f'./static/img/base_imgs/{card_id}_{snap_cnt}.png'
    save_img_from_dataurl(save_src, data_url)

    if snap_cnt < 8:
        return render_template('studio.html', snap_cnt=snap_cnt, card_id=card_id)
    else:
        return render_template("final_step1.html", card_id=card_id)


@app.get('/change_channel')
def change_channel():
    channel_to_change = request.args.get('channel')

    try:
        if (cur_channel != ''):
            send_message_to_channel("📷 해커네컷이 비활성화되었습니다. 다음에 또 만나요! 🥺😘")
            change_cur_channel(channel_to_change)
            send_message_to_channel("📸 찰칵! 우리의 열정을 네 컷에 담아보자😘 해커네컷이 활성화되었습니다!")
            return (f'<script>alert("바뀐 채널: {cur_channel}"); location.href="/"</script>')
    except:
        return (f'<script>alert("nono"); location.href="/"</script>')


if __name__ == '__main__':
    # logging.basicConfig(filename='./log_gogo.txt', level=logging.INFO)
    # logging.basicConfig(filename='./why_nono.txt', level=logging.DEBUG)
    flask_thread = Thread(target=app.run, kwargs={
                          'host': '0.0.0.0', 'port': 5000})
    flask_thread.start()
    SocketModeHandler(app_slack, os.environ['SLACK_APP_TOKEN']).start()
    app_slack.start()
