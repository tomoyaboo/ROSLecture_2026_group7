import cv2
import os

# 入力フォルダ
input_folder = "Documents/git_ros_lecture/ROSLecture_2026_group7/image/bright"

# 出力フォルダ
output_folder = "Documents/git_ros_lecture/ROSLecture_2026_group7/image/frames"
# os.makedirs(output_folder, exist_ok=True)

# 明るさ調整（1より小さいと暗くなる）
brightness_scale = 1.5

for i in range(25):
    filename = f"1.5floor2.mp4_frame_{i:02d}.jpg"
    filepath = os.path.join(input_folder, filename)

    img = cv2.imread(filepath)

    if img is None:
        print(f"読み込み失敗: {filename}")
        continue

    # 明るさを下げる
    dark_img = cv2.convertScaleAbs(img, alpha=brightness_scale, beta=0)

    # 保存
    output_filename = f"right_{filename}"
    output_path = os.path.join(output_folder, output_filename)
    cv2.imwrite(output_path, dark_img)

    print(f"保存: {output_path}")

print("完了！")