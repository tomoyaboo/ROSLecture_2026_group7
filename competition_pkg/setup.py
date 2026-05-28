from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'competition_pkg'
submodules = [f"{package_name}/states"]

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test',*submodules]),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.pashjoin("share", package_name, "launch"), glob("./launch/*.launch.py")),
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
            'state_main_test = competition_pkg.state_main_test:main',
            'voice_recognition_node = competition_pkg.node.voice_recognition_node:main',
        ],
    },
)
