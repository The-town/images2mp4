# INSERT_YOUR_CODE
import os
import cv2
from PIL import Image
import numpy as np
import random
from tqdm import tqdm
import time


def resize_image(image, w_size, h_size):
    h, w = image.shape[:2]
    aspect = w / h
    nh = h_size
    nw = w_size
    if 1 >= aspect:
        nw = round(nh * aspect)
    else:
        nh = round(nw / aspect)

    resized = cv2.resize(image, dsize=(nw, nh))

    return resized


def padding_white(image, w_size, h_size):
    h, w = image.shape[:2]
    y = (h_size - h) // 2
    x = (w_size - w) // 2

    image = Image.fromarray(image) #一旦PIL形式に変換
    canvas = Image.new(image.mode, (w_size, h_size), (255, 255, 255)) # 黒埋めなら(0,0,0)にする
    canvas.paste(image, (x, y))

    dst = np.array(canvas) #numpy(OpenCV)形式に戻す
    
    return dst


def get_image_files(folder_path):
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    return image_files


def main_cli(folder_path, output_file):
    image_files = get_image_files(folder_path)
    # random.shuffle(image_files)

    if not image_files:
        return(("指定されたフォルダに画像ファイルが見つかりませんでした。", ""))


    frame_size = (1280, 720)
    fps = 30
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(output_file, fourcc, fps, frame_size)

    display_duration_seconds = 5
    frames_per_image = int(fps * display_duration_seconds)

    for image_file in tqdm(image_files):
        image_path = os.path.join(folder_path, image_file)
        try:
            img = Image.open(image_path)
            frame = np.array(img)
            resized_frame = resize_image(frame, frame_size[0], frame_size[1])
            padding_white_frame = padding_white(resized_frame, frame_size[0], frame_size[1])
            bgr_frame = cv2.cvtColor(padding_white_frame, cv2.COLOR_RGB2BGR)

            for i in range(frames_per_image):
                video.write(bgr_frame)

            img.close()
        except Exception as e:
            video.release()
            return(("エラーが発生しました。", e))

    video.release()
    return((f"MP4ファイル '{output_file}' が作成されました。", ""))


if __name__ == "__main__":
    folder_path = "./images"
    output_file = "output.mp4"
    info, err = main_cli(folder_path, output_file)
    
    print("info: ", info)
    print("err: ", err)