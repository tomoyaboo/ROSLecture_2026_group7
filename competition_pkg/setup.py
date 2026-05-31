from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'competition_pkg'
submodules = [f"{package_name}/states"]
yolo = [f"yolo"]
yolov5 = [f"yolov5"]

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test',*submodules,*yolo, *yolov5]),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join("share", package_name, "launch"), glob("./launch/*.launch.py")),
        (os.path.join("share", package_name, "yolov5"), glob("competition_pkg/yolov5/*")),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ros2',
    maintainer_email='syuta0910a@yahoo.co.jp',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "sm_main = competition_pkg.sm_main:main",
            'voice_recognition_node = competition_pkg.node.voice_recognition_node_whisper:main',
            " sample = competition_pkg.navigation_sample1:main",

        ],
    },
)
