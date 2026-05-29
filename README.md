# ステートマシン開発・動作確認方法

## 1．目的

共同開発では，各自が担当するステートを作成し，最終的に本番用ステートマシンへ統合する形で開発します．

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

## 5．各自のステートを動かすときの手順

各自が作成したステートを確認する流れは以下です．

```text
1．states配下に自分のステートファイルを作成する
2．state_main_test.pyでimportする
3．state_main_test.pyのsm.add_state()に追加する
4．transitionsで遷移先を書く
5．colcon buildする
6．ros2 run competition_pkg state_main_testで実行する
```

実行例は以下です．

```bash
cd ~/ros2_lecture_ws/
. 0_env.sh
. /entrypoint.sh
colcon build --packages-select competition_pkg
ros2 run competition_pkg state_main_test
```

本番用の `sm_main.py` を確認する場合は，以下を実行します．

```bash
cd ~/ros2_lecture_ws/
. 0_env.sh
. /entrypoint.sh
colcon build --packages-select competition_pkg
source install/setup.bash
ros2 run competition_pkg sm_main
```

ただし，`sm_main.py` に未完成のステートや `???` が残っている場合は実行できません．  
その場合は，まず `state_main_test.py` で個別に確認してください．

---

## 6．本番用 `sm_main.py` に統合するときの考え方

`state_main_test.py` で自分のステートの動作確認ができたら，本番用の `sm_main.py` に統合します．

統合時には，以下の3点を追加・変更します．

```text
1．sm_main.pyで自分のステートをimportする
2．sm.add_state()で自分のステートを登録する
3．前後のステートのtransitionsを書き換える
```

例えば，`MyState` を `StartState` の次に入れたい場合は，以下のようにします．

```python
sm.add_state(
    name="StartState",
    state=start_state.StartState(node=self),
    transitions={
        "success": "MyState",
    },
)

sm.add_state(
    name="MyState",
    state=my_state.MyState(node=self),
    transitions={
        "success": "NextState",
        "failure": "EXIT",
    },
)
```

このように，前のステートの遷移先を自分のステート名にし，自分のステートの遷移先を次のステート名にします．

---

## 7．参考：ノードを作って試したい場合

ステートだけでなく，ROS2ノードを作って試したい場合は，`competition_pkg/competition_pkg/node/` 配下にノード用のPythonファイルを作成します．

例えば，`my_node.py` というノードを作る場合は，以下のような構成にします．

```text
competition_pkg/
└── competition_pkg/
    └── node/
        ├── __init__.py
        └── my_node.py
```

`my_node.py` の中には，通常のROS2ノードと同じように `main()` を用意します．

```python
import rclpy
from rclpy.node import Node


class MyNode(Node):
    def __init__(self):
        super().__init__("my_node")
        self.get_logger().info("my_nodeを起動しました")


def main(args=None):
    rclpy.init(args=args)

    node = MyNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

このノードを `ros2 run` で起動したい場合は，`setup.py` の `entry_points` に以下を追加します．

```python
"my_node = competition_pkg.node.my_node:main",
```

追加後は，ビルドして実行します．

```bash
cd ~/ros2_lecture_ws/
. 0_env.sh
. /entrypoint.sh
colcon build --packages-select competition_pkg
ros2 run competition_pkg my_node
```

音声認識ノードなど，追加のライブラリが必要なノードを作る場合は，そのノードを使う人だけ必要なライブラリをインストールしてください．

ros2@ros2-athome01 ~/ros2_lecture_ws $ ros2_lecture_sandbox venv:/opt/pyvenv 
 > colcon build --packages-select competition_pkg
[0.645s] ERROR:colcon:colcon build: Duplicate package names not supported:
- competition_pkg:
  - group7/ROSLecture_2026_group7/competition_pkg
  - src/7_lectures/competition_pkg
  - src/7_lectures/last/competition_pkg

