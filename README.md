# ステートマシン・音声認識ノードまわりの共有事項

## 1．今回追加している内容

自分のブランチでは，主に以下の内容を追加しています．

- ステートマシンの仮動作確認用メイン
  - `competition_pkg/competition_pkg/state_main_test.py`
- 本番用ステートマシンのたたき台
  - `competition_pkg/competition_pkg/sm_main.py`
- 音声認識ステート
  - `competition_pkg/competition_pkg/states/voice_recognirion.py`
- 質問ステート
  - `competition_pkg/competition_pkg/states/question.py`
- 開始待ちステート
  - `competition_pkg/competition_pkg/states/wait4start.py`
- 音声認識ノード
  - `competition_pkg/competition_pkg/node/voice_recognition_node.py`

---

## 2．本番用 `sm_main.py` について

`sm_main.py` は，本番用のステートマシン全体を書くためのファイルとして用意しています．

現状では，まだ以下のように `???` が残っている部分があります．

```python
from .states import ???
```

```python
state=???
```

```python
transitions={
    ??? : "次のステート",
}
```

そのため，現時点では `sm_main.py` はまだそのままでは実行できません．

今後は，各担当者が作成したステートを `sm_main.py` にimportし，`sm.add_state()` の中に書き込むことで，本番用のステートマシンを完成させる想定です．

例えば，誰かが `move_to_position.py` というステートを作った場合は，`sm_main.py` に以下のように追加します．

```python
from .states import move_to_position
```

そして，ステートマシン本体には以下のように書きます．

```python
sm.add_state(
    name="te-ichi",
    state=move_to_position.MoveToPositionState(node=self),
    transitions={
        "success": "of-recog",
        "failure": "EXIT",
    },
)
```

つまり，本番用では，

```text
ステートのPythonファイルを作る
↓
sm_main.pyでimportする
↓
sm.add_state()で登録する
↓
transitionsで次に進むステート名を書く
```

という流れになります．

---

## 3．現在のテスト用メイン `state_main_test.py` の動作

現在，仮動作確認用として `state_main_test.py` を用意しています．

このファイルでは，以下のような簡単なステートマシンを動かしています．

```text
Wait4start
↓
Question
↓
VoiceRecognition
↓
EXIT
```

それぞれの役割は以下です．

### Wait4start

```text
開始待ちステート
```

ターミナル入力などで開始を待ち，開始条件を満たすと `success` を返します．

```python
transitions={
    "success": "Question",
}
```

### Question

```text
「鍵持ってますか？」と聞くステート
```

現在は，質問文をログに出して，すぐに `success` を返す簡単な実装です．

```python
transitions={
    "success": "VoiceRecognition",
}
```

### VoiceRecognition

```text
/speech_text を購読して，HAVE / LOST を待つステート
```

音声認識ノードから `/speech_text` に送られてきた文字列を見て，以下のように遷移します．

```text
HAVE を受信 → success
LOST を受信 → failure
5秒以内に認識できない → retry
```

現在のテストメインでは，以下のように書いています．

```python
sm.add_state(
    name="VoiceRecognition",
    state=voice_recognirion.VoRecofg(node=self),
    transitions={
        "success": "EXIT",
        "failure": "EXIT",
        "retry": "Question",
    },
)
```

つまり，

```text
HAVEなら終了
LOSTなら終了
認識できなければQuestionに戻って再質問
```

という仮動作確認になっています．

---

## 4．自分のステートを動かすには

自分のステートを仮に動かしたい場合は，`state_main_test.py` に一時的に追加すると確認しやすいです．

例えば，`states/my_state.py` に `MyState` というステートを作った場合，まず `state_main_test.py` の上の方にimportを追加します．

```python
from .states import my_state
```

そして，`sm.add_state()` を追加します．

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

既存の流れに組み込む場合は，前のステートの遷移先を自分のステート名に変更します．

例えば，`Question` の次に自分のステートを動かしたい場合は，

```python
sm.add_state(
    name="Question",
    state=question.QuestionState(node=self),
    transitions={
        "success": "MyState",
    },
)
```

のようにします．

その後，自分のステートから次に進む先を `transitions` に書きます．

```python
sm.add_state(
    name="MyState",
    state=my_state.MyState(node=self),
    transitions={
        "success": "VoiceRecognition",
        "failure": "EXIT",
    },
)
```

このようにすると，

```text
Wait4start
↓
Question
↓
MyState
↓
VoiceRecognition
↓
EXIT
```

のように動作確認できます．

---

## 5．`setup.py` の書き換えについて

ROS2で `ros2 run` からPythonノードを起動するには，`setup.py` の `entry_points` に登録する必要があります．

現在の `setup.py` では，以下のようになっている場合があります．

```python
entry_points={
    'console_scripts': [
        "node1 = competition_pkg.node1:main",
        "node2 = competition_pkg.node2:main",
    ],
},
```

このままだと，今回追加した以下のノードを `ros2 run` で起動できません．

- `state_main_test.py`
- `sm_main.py`
- `voice_recognition_node.py`

そのため，以下のように変更します．

```python
entry_points={
    'console_scripts': [
        "node1 = competition_pkg.node1:main",
        "node2 = competition_pkg.node2:main",

        "state_main_test = competition_pkg.state_main_test:main",
        "sm_main = competition_pkg.sm_main:main",
        "voice_recognition_node = competition_pkg.node.voice_recognition_node:main",
    ],
},
```

これで，以下のように実行できるようになります．

```bash
ros2 run competition_pkg state_main_test
```

```bash
ros2 run competition_pkg sm_main
```

```bash
ros2 run competition_pkg voice_recognition_node
```

---

## 6．`setup.py` で修正が必要な点

現状の `setup.py` に以下のような typo がある場合があります．

```python
os.pashjoin
```

これは間違いで，正しくは以下です．

```python
os.path.join
```

そのため，以下の部分は，

```python
(os.pashjoin("share", package_name, "launch"), glob("./launch/*.launch.py")),
```

次のように修正します．

```python
(os.path.join("share", package_name, "launch"), glob("./launch/*.launch.py")),
```

また，現在の `setup.py` に以下のような記述がある場合があります．

```python
submodules = [f"{package_name}/states"]

packages=find_packages(exclude=['test', *submodules]),
```

この書き方だと，`states` 配下のファイルがインストール対象から外れる可能性があります．

`from .states import ...` を使うためには，`states` パッケージもインストールされる必要があります．

そのため，基本的には以下のようにした方が安全です．

```python
packages=find_packages(exclude=['test']),
```

---

## 7．修正後の `setup.py` の例

以下のようにしておくと，今回追加したステートマシンと音声認識ノードを `ros2 run` で起動できます．

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
            "voice_recognition_node = competition_pkg.node.voice_recognition_node:main",
        ],
    },
)
```

---

## 8．仮動作確認の方法

### ステートマシンの仮動作確認

まず，ステートマシン側を起動します．

```bash
cd ~/ros2_lecture_ws/
. 0_env.sh
. /entrypoint.sh
ros2 run competition_pkg state_main_test
```

これは，現在の仮動作確認用メインです．

本番用の `sm_main.py` はまだ `???` が残っているため，完成するまではこちらを使って確認します．

---

### 音声認識ノードの動作確認

別端末で，音声認識ノードを起動します．

```bash
cd ~/ros2_lecture_ws/
. 0_env.sh
. /entrypoint.sh
ros2_lecture_sandbox venv:/opt/pyvenv
ros2 run competition_pkg voice_recognition_node
```

音声認識ノードは `/speech_text` に認識結果を送信します．

ステートマシン側の `VoiceRecognition` ステートは，この `/speech_text` を購読して，`HAVE` または `LOST` を受け取ります．

---

## 9．トピックだけ確認したい場合

音声認識ノードが本当に `/speech_text` に送れているか確認したい場合は，別端末で以下を実行します．

```bash
cd ~/ros2_lecture_ws/
. 0_env.sh
. /entrypoint.sh
ros2 topic echo /speech_text
```

例えば，音声認識ノードが `HAVE` を送信していれば，以下のように表示されます．

```bash
data: HAVE
---
```

---

## 10．本番用 `sm_main.py` に統合するときの注意

現在の音声認識ステート `VoRecofg` は，返す結果が以下です．

```text
HAVEを受信した場合 → success
LOSTを受信した場合 → failure
認識失敗・時間切れ → retry
```

つまり，`transitions` は以下のように書く必要があります．

```python
sm.add_state(
    name="VoiceRecognition",
    state=voice_recognirion.VoRecofg(node=self),
    transitions={
        "success": "VoOut-Have",
        "failure": "search",
        "retry": "Question",
    },
)
```

一方で，`sm_main.py` のたたき台では，以下のように書かれている場合があります．

```python
transitions={
    "HAVE": "VoOut-have",
    "LOST": "search",
    "retry": "Question",
}
```

この書き方にしたい場合は，`VoRecofg` 側の `outcomes` と `return` を以下のように変更する必要があります．

```python
super().__init__(outcomes=["HAVE", "LOST", "retry"])
```

```python
if text == self.expected_text_Y:
    return "HAVE"

elif text == self.expected_text_N:
    return "LOST"
```

どちらでも実装できますが，現状の `VoRecofg` に合わせるなら，`sm_main.py` 側を以下のようにする方が簡単です．

```python
transitions={
    "success": "VoOut-Have",
    "failure": "search",
    "retry": "Question",
}
```

---
