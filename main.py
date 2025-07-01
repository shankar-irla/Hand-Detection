import sys
import cv2
import numpy as np
import mediapipe as mp
import webbrowser
import time
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont, QPalette, QBrush, QPixmap
from PyQt5.QtCore import Qt
from ffpyplayer.player import MediaPlayer

class HandScannerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 Futuristic Hand Scanner Launcher")
        self.setGeometry(550, 250, 420, 240)
        self.setFixedSize(420, 240)

        # Set background image
        background_path = 'assets/images/bg.png'
        self.setAutoFillBackground(True)
        palette = self.palette()
        pixmap = QPixmap(background_path)
        palette.setBrush(QPalette.Window, QBrush(pixmap.scaled(self.size())))
        self.setPalette(palette)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(10)

        title = QLabel("🖐️ HAND DETECTION SCANNER")
        title.setStyleSheet("""
            color: cyan;
            font-size: 18px;
            font-weight: bold;
            background-color: rgba(0, 0, 0, 100);
            padding: 10px;
            border-radius: 10px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        dev_label = QLabel("🔧 Built by Shankar | _ASRAccelet team")
        dev_label.setStyleSheet("""
            color: white;
            font-size: 13px;
            background-color: rgba(0, 0, 0, 80);
            padding: 5px;
            border-radius: 8px;
        """)
        dev_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(dev_label)

        self.start_btn = QPushButton("🚀 Launch Scanner")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #1E90FF, stop:1 #00FA9A);
                color: black;
                font-size: 14px;
                font-weight: bold;
                border-radius: 12px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #00BFFF, stop:1 #00FFB2);
            }
        """)
        self.start_btn.clicked.connect(self.start_scanner)
        layout.addWidget(self.start_btn)

        layout.addStretch()
        self.setLayout(layout)

    def start_scanner(self):
        video_played = False
        video_cooldown = False

        # Load hand frame template
        template = cv2.imread('assets/images/hand_frame.png', cv2.IMREAD_UNCHANGED)
        if template is None:
            print("Error: hand_frame.png not found!")
            return

        template_h, template_w = template.shape[:2]
        cap = cv2.VideoCapture(0)

        mp_hands = mp.solutions.hands
        mp_drawing = mp.solutions.drawing_utils
        hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)

        def overlay_image_alpha(img, img_overlay, pos):
            x, y = pos
            h, w = img_overlay.shape[:2]
            if y + h > img.shape[0] or x + w > img.shape[1] or x < 0 or y < 0:
                return
            alpha_overlay = img_overlay[:, :, 3] / 255.0
            alpha_bg = 1.0 - alpha_overlay
            for c in range(3):
                img[y:y+h, x:x+w, c] = (
                    alpha_overlay * img_overlay[:, :, c] +
                    alpha_bg * img[y:y+h, x:x+w, c]
                )

        def play_video_with_sound(video_path):
            video = cv2.VideoCapture(video_path)
            player = MediaPlayer(video_path)

            cv2.namedWindow("Output", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("Output", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

            while True:
                ret, frame = video.read()
                audio_frame, val = player.get_frame()
                if not ret:
                    break
                if val != 'eof' and audio_frame is not None:
                    img, t = audio_frame
                cv2.imshow("Output", frame)
                if cv2.waitKey(20) & 0xFF == 27:
                    break

            player.close()
            video.release()
            cv2.destroyWindow("Output")
            webbrowser.open('https://www.linkedin.com/in/shankar-irla')
            time.sleep(2)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape

            center_x, center_y = w // 2 - template_w // 2, h // 2 - template_h // 2
            overlay_image_alpha(frame, template, (center_x, center_y))

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            hand_inside_template = False

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    x_coords = [lm.x * w for lm in hand_landmarks.landmark]
                    y_coords = [lm.y * h for lm in hand_landmarks.landmark]
                    x_min, x_max = int(min(x_coords)), int(max(x_coords))
                    y_min, y_max = int(min(y_coords)), int(max(y_coords))
                    if (center_x < x_min < center_x + template_w and
                        center_y < y_min < center_y + template_h and
                        center_x < x_max < center_x + template_w and
                        center_y < y_max < center_y + template_h):
                        hand_inside_template = True

            if hand_inside_template and not video_played and not video_cooldown:
                video_played = True
                video_cooldown = True
                play_video_with_sound('vid.mp4')

            if not hand_inside_template:
                video_played = False
                video_cooldown = False

            cv2.imshow("Hand Scanner Launcher", frame)
            if cv2.waitKey(5) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

        if not video_played:
            webbrowser.open('https://www.linkedin.com/in/shankar-irla')
            time.sleep(2)

        sys.exit(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HandScannerApp()
    window.show()
    sys.exit(app.exec_())
