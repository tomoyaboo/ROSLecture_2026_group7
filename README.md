## Whisper音声認識ノードの実行方法

本パッケージでは，`faster-whisper` を用いてマイク入力を音声認識し，認識結果を `/speech_text` トピックに送信します．

ステートマシン側では，この `/speech_text` を購読して，音声認識結果に応じた状態遷移を行います．

---

## 1．Whisper関連ライブラリのインストール

以下のコマンドを実行し，Whisper音声認識に必要なライブラリをインストールします．

```bash
cd ~/ros2_lecture_ws/
. 1_env_write.sh
. /entrypoint.sh
ros2_lecture_sandbox venv:/opt/pyvenv
pip install faster-whisper sounddevice scipy
```

インストールする主なライブラリは以下です．

- `faster-whisper`：Whisperによる音声認識
- `sounddevice`：マイク入力の録音
- `scipy`：録音した音声のwav保存

---

## 2．ステートマシンノードの起動

別の端末を開き，以下のコマンドを実行します．

```bash
cd ~/ros2_lecture_ws/
. 0_env.sh
. /entrypoint.sh
ros2 run competition_pkg state_main_test
```

このノードは，音声認識ノードから送信される `/speech_text` トピックを受け取り，ステートマシンを動作させます．

---

## 3．音声認識ノードの起動

さらに別の端末を開き，以下のコマンドを実行します．

```bash
cd ~/ros2_lecture_ws/
. 0_env.sh
. /entrypoint.sh
ros2_lecture_sandbox venv:/opt/pyvenv
ros2 run competition_pkg voice_recognition_node
```

音声認識ノードが起動すると，マイク入力を一定時間録音し，Whisperで文字起こしを行います．

認識結果は `/speech_text` トピックに送信されます．

---

## 注意点

Whisper関連ライブラリを使用するため，音声認識ノードを起動する端末では，以下を実行して仮想環境に入ってください．

```bash
ros2_lecture_sandbox venv:/opt/pyvenv
```

ステートマシンノード側ではWhisperを直接使用しないため，通常は仮想環境に入らなくても実行できます．

ただし，`0_env.sh` や `/entrypoint.sh` を実行し忘れると，ROS2パッケージやトピックが正しく認識されない場合があります．


os2@ros2-athome01 ~/ros2_lecture_ws $ ros2_lecture_sandbox venv:/opt/pyvenv 
 > python3 -c "from huggingface_hub import snapshot_download; print('start'); snapshot_download(repo_id='Systran/faster-whisper-tiny', local_dir='/home/ros2/whisper_models/faster-whisper-tiny'); print('done')"
start
Downloading (incomplete total...): 0.00B [00:00, ?B/s]                         Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Downloading (incomplete total...):   3%|   | 2.67M/78.2M [00:19<00:13, 5.56MB/s]
Fetching 6 files:  17%|████▌                      | 1/6 [00:00<00:02,  2.32it/s]
