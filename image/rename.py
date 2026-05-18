import os

folder = r"C:\Users\hutoo\Documents\git_ros_lecture\ROSLecture_2026_group7\image\labels"

for filename in os.listdir(folder):

    if "-" in filename:
        new_name = filename.split("-", 1)[1]

        old_path = os.path.join(folder, filename)
        new_path = os.path.join(folder, new_name)

        os.rename(old_path, new_path)

        print(f"{filename} -> {new_name}")

print("完了")