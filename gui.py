from main import resize_image, padding_white, get_image_files

import os
import cv2
from PIL import Image
import numpy as np
import time
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk

# ディスプレイのDPIを考慮するための設定
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)


class App():
    def __init__(self):
        root = tk.Tk()
        root.title("image2mp4")
        root.geometry("400x400")
        root.anchor(tk.CENTER)

        self.message_frame_root = tk.Frame(root)
        self.message_frame_root.grid(column=0, row=0, sticky="ew")
        self.message_frame = MessageFrame(self.message_frame_root)

        self.progress_frame_root = tk.Frame(root)
        self.progress_frame_root.grid(column=0, row=1)

        self.control_frame_root = tk.Frame(root)
        self.control_frame_root.grid(column=0, row=2)

        self.entry_outputname = tk.Entry(self.control_frame_root)
        self.entry_outputname.insert(0, "output.mp4")
        self.entry_outputname.grid(column=0, row=0)

        self.select_folder_button = ttk.Button(self.control_frame_root, text="フォルダ選択", command=self.select_folder)
        self.select_folder_button.grid(column=0, row=1)

        self.exec_button = ttk.Button(self.control_frame_root, text="実行", command=self.exec_images_to_mp4)
        self.exec_button.grid(column=0, row=2)

        root.mainloop()

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path = folder_selected
            self.message_frame.update_message("info", f"フォルダを選択しました: {self.folder_path}")

    def exec_images_to_mp4(self):
        self.message_frame.update_message("error", "")
        
        if not hasattr(self, "folder_path"):
            self.message_frame.update_message("error", "フォルダを選択してください")
            return
        
        output_file = self.entry_outputname.get()
        if output_file == "":
            self.message_frame.update_message("error", "出力ファイル名を入力してください")
            return

        images = get_image_files(self.folder_path)
        self.progress_frame = ProgressFrame(self.progress_frame_root, len(images))

        frame_size = (1280, 720)
        fps = 30
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(os.path.join(self.folder_path, output_file), fourcc, fps, frame_size)

        display_duration_seconds = 5
        frames_per_image = int(fps * display_duration_seconds)

        for bar, image_file in enumerate(images):
            image_path = os.path.join(self.folder_path, image_file)
            self.message_frame.update_message("info", f"処理中: {image_file}")
            try:
                img = Image.open(image_path)
                frame = np.array(img)
                resized_frame = resize_image(frame, frame_size[0], frame_size[1])
                padding_white_frame = padding_white(resized_frame, frame_size[0], frame_size[1])
                bgr_frame = cv2.cvtColor(padding_white_frame, cv2.COLOR_RGB2BGR)

                for i in range(frames_per_image):
                    video.write(bgr_frame)

                img.close()
                self.progress_frame.update_progressbar(bar+1)

            except Exception as e:
                video.release()
                self.message_frame.update_message("error", f"エラーが発生しました。{e}")
                return

        video.release()
        self.message_frame.update_message("info", f"MP4ファイル '{output_file}' が作成されました。")


class MessageFrame():
    def __init__(self, master):
        self.frame = tk.Frame(master)
        self.frame.grid(column=0, row=0, sticky="ew")

        self.messages_label = tk.Label(self.frame, text="", wraplength=300, anchor=tk.CENTER)
        self.messages_label.grid(column=0, row=0)
        self.messages = {
            "info": "フォルダを選択してください",
            "error": "",
        }

        self.update_message_label()
    
    def update_message(self, message_type: str, message: str):
        self.messages[message_type] = message
        self.update_message_label()

    def update_message_label(self):
        message = ""
        for key, value in self.messages.items():
            if value:
                message += f"{key}: {value}\n"
        self.messages_label.config(text=message)

        self.frame.after(1000, self.update_message_label)


class ProgressFrame():
    def __init__(self, master, max_value: int):
        self.frame = tk.Frame(master)
        self.frame.grid(column=0, row=0)

        self.progressbar_var = tk.DoubleVar(self.frame, value=0)
        self.progressbar = ttk.Progressbar(
            self.frame, 
            orient='horizontal', 
            mode='determinate', 
            length=300, 
            variable=self.progressbar_var,
            maximum=max_value,)
        self.progressbar.grid(column=0, row=0, padx=10, pady=10)

    def update_progressbar(self, value: int):
        self.progressbar_var.set(float(value))
        self.progressbar.update()


if __name__ == "__main__":
    app = App()

