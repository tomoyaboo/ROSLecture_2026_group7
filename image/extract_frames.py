import cv2
import os

# ===== 設定 =====

# 動画ファイル名
video = "floor2.mp4"
video_path = os.path.join(r"C:\Users\hutoo\Documents\git_ros_lecture\ROSLecture_2026_group7\image", video)

# 保存先フォルダ
output_dir = r"C:\Users\hutoo\Documents\git_ros_lecture\ROSLecture_2026_group7\image\frames"

# 何フレームごとに保存するか
frame_interval = 15

# =================

# 保存フォルダ作成
os.makedirs(output_dir, exist_ok=True)

# 動画読み込み
cap = cv2.VideoCapture(video_path)

# 読み込み確認
if not cap.isOpened():
    print("動画を開けませんでした")
    exit()

frame_count = 0
save_count = 0

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # 指定間隔ごとに保存
    if frame_count % frame_interval == 0:

        filename = os.path.join(
            output_dir,
            f"1.5{video}_frame_{save_count:02d}.jpg"
        )

        cv2.imwrite(filename, frame)

        print(f"保存: {filename}")

        save_count += 1

    frame_count += 1

cap.release()

print("フレーム抽出完了")
print(f"保存枚数: {save_count}")