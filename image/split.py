import os
import random
import shutil

# 元データ
image_dir = r"C:\Users\hutoo\Documents\git_ros_lecture\ROSLecture_2026_group7\image\frames"
label_dir = r"C:\Users\hutoo\Documents\git_ros_lecture\ROSLecture_2026_group7\image\labels"

# 出力先
dataset_dir = r"C:\Users\hutoo\Documents\git_ros_lecture\ROSLecture_2026_group7\image\dataset1"

train_img = os.path.join(dataset_dir, "images", "train")
val_img = os.path.join(dataset_dir, "images", "val")
train_lbl = os.path.join(dataset_dir, "labels", "train")
val_lbl = os.path.join(dataset_dir, "labels", "val")

for folder in [train_img, val_img, train_lbl, val_lbl]:
    os.makedirs(folder, exist_ok=True)

# jpgだけ取得
images = [f for f in os.listdir(image_dir) if f.endswith(".jpg")]

random.shuffle(images)

split_idx = int(len(images) * 0.8)

train_files = images[:split_idx]
val_files = images[split_idx:]

def move_files(file_list, img_dst, lbl_dst):
    for img in file_list:
        label = img.replace(".jpg", ".txt")

        shutil.copy(
            os.path.join(image_dir, img),
            os.path.join(img_dst, img)
        )

        shutil.copy(
            os.path.join(label_dir, label),
            os.path.join(lbl_dst, label)
        )

move_files(train_files, train_img, train_lbl)
move_files(val_files, val_img, val_lbl)

print(f"Train: {len(train_files)}")
print(f"Val: {len(val_files)}")
print("done")