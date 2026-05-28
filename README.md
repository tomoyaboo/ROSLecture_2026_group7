# ステートマシン開発・動作確認方法

## 1．目的

共同開発では，基本的に各自が担当するステートを作成し，最終的に本番用ステートマシンに統合する形で開発します．

そのため，このブランチでは以下の2つを用意しています．

- 本番用ステートマシンのたたき台
  - `competition_pkg/competition_pkg/sm_main.py`
- 各ステートの仮動作確認用メイン
  - `competition_pkg/competition_pkg/state_main_test.py`

各自が作成したステートは，まず `state_main_test.py` を使って単体または簡単な流れで確認し，問題なければ `sm_main.py` に統合する想定です．

---

## 2．本番用 `sm_main.py` について

`sm_main.py` は，本番用のステートマシン全体を書くためのファイルです．

各自が作成したステートを，このファイルに `import` し，`sm.add_state()` で登録していくことで，全体のステートマシンを構成します．

例えば，`states/my_state.py` に `MyState` というステートを作成した場合，`sm_main.py` に以下のように追加します．

```python
from .states import my_state
```

そして，ステートマシン本体に以下のように登録します．

```python
sm.add_state(
    name="MyState",
    state=my_state.MyState(node=self),
    transitions={
        "success": "NextState",
        "failure": "EXIT",
    },
)
```

基本的な流れは以下です．

```text
ステートのPythonファイルを作成
↓
sm_main.pyでimport
↓
sm.add_state()で登録
↓
transitionsに次のステート名を書く
```

---

## 3．仮動作確認用 `state_main_test.py` について

`state_main_test.py` は，各自が作成したステートを一時的に動作確認するためのファイルです．

本番用の `sm_main.py` を直接編集しながら確認すると，他の人の作業と衝突しやすいため，まずは `state_main_test.py` に自分のステートを追加して確認するのがよいです．

例えば，`states/my_state.py` に `MyState` を作った場合，`state_main_test.py` に以下を追加します．

```python
from .states import my_state
```

次に，ステートマシン内に以下のように追加します．

```python
sm.add_state(
    name="MyState",
    state=my_state.MyState(node=self),
    transitions={
        "success": "EXIT",
        "failure": "EXIT",
    },
)
```

これで，自分のステートだけを実行して，正常に動くか確認できます．

---

## 4．複数ステートをつなげて確認する方法

複数のステートをつなげて確認したい場合は，`transitions` の遷移先を書き換えます．

例えば，以下のような流れで確認したい場合を考えます．

```text
Wait4start
↓
MyState
↓
EXIT
```

その場合，`Wait4start` の遷移先を `MyState` にします．

```python
sm.add_state(
    name="Wait4start",
    state=wait4start.Wait4StartState(node=self),
    transitions={
        "success": "MyState",
    },
)
```

そして，`MyState` から `EXIT` に進むようにします．

```python
sm.add_state(
    name="MyState",
    state=my_state.MyState(node=self),
    transitions={
        "success": "EXIT",
        "failure": "EXIT",
    },
)
```

このように，`transitions` の値を変更することで，各自のステートを好きな順番で仮確認できます．

---

## 5．`setup.py` の書き換えについて

ROS2でPythonファイルを `ros2 run` から実行するには，`setup.py` の `entry_points` に登録する必要があります．

例えば，`state_main_test.py` と `sm_main.py` を実行できるようにするには，以下のように書きます．

```python
entry_points={
    'console_scripts': [
        "state_main_test = competition_pkg.state_main_test:main",
        "sm_main = competition_pkg.sm_main:main",
    ],
},
```

これで，以下のコマンドで実行できます．

```bash
ros2 run competition_pkg state_main_test
```

```bash
ros2 run competition_pkg sm_main
```

既存の `node1` や `node2` を残す場合は，以下のように追加してください．

```python
entry_points={
    'console_scripts': [
        "node1 = competition_pkg.node1:main",
        "node2 = competition_pkg.node2:main",

        "state_main_test = competition_pkg.state_main_test:main",
        "sm_main = competition_pkg.sm_main:main",
    ],
},
```

---

## 6．`setup.py` の注意点

### `states` を除外しない

`setup.py` に以下のような記述がある場合，`states` 配下がインストール対象から外れる可能性があります．

```python
submodules = [f"{package_name}/states"]

packages=find_packages(exclude=['test', *submodules]),
```

各自が作成したステートを `from .states import ...` で使うためには，`states` もパッケージとして含める必要があります．

そのため，基本的には以下のようにするのが安全です．

```python
packages=find_packages(exclude=['test']),
```

### `__init__.py` を置く

`states` 配下をPythonパッケージとして扱うため，以下のファイルが必要です．

```text
competition_pkg/competition_pkg/states/__init__.py
```

また，ノード用のディレクトリを使う場合は，以下も必要です．

```text
competition_pkg/competition_pkg/node/__init__.py
```

---

## 7．修正後の `setup.py` の例

ステートマシンの仮動作確認と本番用メインを実行できるようにする場合，`setup.py` は以下のようになります．

```python
from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'competition_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join("share", package_name, "launch"), glob("./launch/*.launch.py")),
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
            "node1 = competition_pkg.node1:main",
            "node2 = competition_pkg.node2:main",

            "state_main_test = competition_pkg.state_main_test:main",
            "sm_main = competition_pkg.sm_main:main",
        ],
    },
)
```

---

## 8．ビルド方法

`setup.py` を変更した場合や，新しいステートを追加した場合は，ビルドし直してください．

```bash
cd ~/ros2_lecture_ws/
. 0_env.sh
. /entrypoint.sh
colcon build --packages-select competition_pkg
```

ビルド後，環境を読み込み直します．

```bash
. install/setup.bash
```

---

## 9．仮動作確認の方法

各自のステートを確認する場合は，`state_main_test.py` を使います．

```bash
cd ~/ros2_lecture_ws/
. 0_env.sh
. /entrypoint.sh
ros2 run competition_pkg state_main_test
```

本番用の `sm_main.py` を確認する場合は，以下を実行します．

```bash
cd ~/ros2_lecture_ws/
. 0_env.sh
. /entrypoint.sh
ros2 run competition_pkg sm_main
```

ただし，`sm_main.py` に未完成のステートや `???` が残っている場合は実行できません．  
その場合は，まず `state_main_test.py` で個別に確認してください．

---

## 10．自分のステートを動かすときの手順

各自が作成したステートを確認する流れは以下です．

```text
1．states配下に自分のステートファイルを作成する
2．state_main_test.pyでimportする
3．state_main_test.pyのsm.add_state()に追加する
4．transitionsで遷移先を書く
5．setup.pyにstate_main_testが登録されていることを確認する
6．colcon buildする
7．ros2 run competition_pkg state_main_testで実行する
```

---
