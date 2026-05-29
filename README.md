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

rm -rf /home/ros2/whisper_models/faster-whisper-tiny
mkdir -p /home/ros2/whisper_models/faster-whisper-tiny

cd /home/ros2/whisper_models/faster-whisper-tiny

wget https://huggingface.co/Systran/faster-whisper-tiny/resolve/main/config.json
wget https://huggingface.co/Systran/faster-whisper-tiny/resolve/main/model.bin
wget https://huggingface.co/Systran/faster-whisper-tiny/resolve/main/tokenizer.json
wget https://huggingface.co/Systran/faster-whisper-tiny/resolve/main/vocabulary.txt

ls -lh /home/ros2/whisper_models/faster-whisper-tiny

python3 -c "from faster_whisper import WhisperModel; print('start'); model=WhisperModel('/home/ros2/whisper_models/faster-whisper-tiny', device='cpu', compute_type='int8'); print('loaded')"


ros2@ros2-athome01 ~/whisper_models/faster-whisper-tiny $ ros2_lecture_sandbox venv:/opt/pyvenv 
 > wget https://huggingface.co/Systran/faster-whisper-tiny/resolve/main/model.bin
--2026-04-14 23:30:47--  https://huggingface.co/Systran/faster-whisper-tiny/resolve/main/model.bin
Resolving huggingface.co (huggingface.co)... 143.204.80.100, 143.204.80.9, 143.204.80.60, ...
Connecting to huggingface.co (huggingface.co)|143.204.80.100|:443... connected.
HTTP request sent, awaiting response... 302 Found
Location: https://cas-bridge.xethub.hf.co/xet-bridge-us/655f211ad5c0d3db537f315b/95d706516af777831fff6b2c35837dfb450afca078db361910d44a435b24dc2c?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=cas%2F20260529%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260529T072551Z&X-Amz-Expires=3600&X-Amz-Signature=86dea6ebacd92d4650ef56836053cf9e55200caa1aab7ca796bae9f514da6afd&X-Amz-SignedHeaders=host&X-Xet-Cas-Uid=public&response-content-disposition=inline%3B+filename*%3DUTF-8%27%27model.bin%3B+filename%3D%22model.bin%22%3B&response-content-type=application%2Foctet-stream&x-amz-checksum-mode=ENABLED&x-id=GetObject&Expires=1780043151&Policy=eyJTdGF0ZW1lbnQiOlt7IkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc4MDA0MzE1MX19LCJSZXNvdXJjZSI6Imh0dHBzOi8vY2FzLWJyaWRnZS54ZXRodWIuaGYuY28veGV0LWJyaWRnZS11cy82NTVmMjExYWQ1YzBkM2RiNTM3ZjMxNWIvOTVkNzA2NTE2YWY3Nzc4MzFmZmY2YjJjMzU4MzdkZmI0NTBhZmNhMDc4ZGIzNjE5MTBkNDRhNDM1YjI0ZGMyYyoifV19&Signature=ZRKZlGaAbXmxkQlEXjXLbN0XDbjJCv87iNz4phcrJJyYoS8b6TQWYdN2SjRd03V2-UcW7MV67pkmAXqtzAYHadUsP2YUOl%7EMmIxfpoApJGoTFUlkhiBK0W7SwM4tX-9HGUQaQ0Gi3KFSG%7EZsNngcbcB0YHMvzZDiBgSgvdmagobgLJhfsoouT0GqzIs6y9-A%7E3WSXd4e9VodSbM864e%7E9hJd0WWkNxjNvotq%7EQ-DikvsPxlTzq%7EyUbbO-1UR%7E5Vf%7EEOHhsxF-cHlsWccXpnHZuB%7EMPTQaIykc04Zyp3YQdUjVyAa209uwALI7E1u0iyP5JVtMyG7P8PKwOciuOUt5w__&Key-Pair-Id=K2L8F4GPSG1IFC [following]
--2026-04-14 23:30:48--  https://cas-bridge.xethub.hf.co/xet-bridge-us/655f211ad5c0d3db537f315b/95d706516af777831fff6b2c35837dfb450afca078db361910d44a435b24dc2c?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=cas%2F20260529%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260529T072551Z&X-Amz-Expires=3600&X-Amz-Signature=86dea6ebacd92d4650ef56836053cf9e55200caa1aab7ca796bae9f514da6afd&X-Amz-SignedHeaders=host&X-Xet-Cas-Uid=public&response-content-disposition=inline%3B+filename*%3DUTF-8''model.bin%3B+filename%3D%22model.bin%22%3B&response-content-type=application%2Foctet-stream&x-amz-checksum-mode=ENABLED&x-id=GetObject&Expires=1780043151&Policy=eyJTdGF0ZW1lbnQiOlt7IkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc4MDA0MzE1MX19LCJSZXNvdXJjZSI6Imh0dHBzOi8vY2FzLWJyaWRnZS54ZXRodWIuaGYuY28veGV0LWJyaWRnZS11cy82NTVmMjExYWQ1YzBkM2RiNTM3ZjMxNWIvOTVkNzA2NTE2YWY3Nzc4MzFmZmY2YjJjMzU4MzdkZmI0NTBhZmNhMDc4ZGIzNjE5MTBkNDRhNDM1YjI0ZGMyYyoifV19&Signature=ZRKZlGaAbXmxkQlEXjXLbN0XDbjJCv87iNz4phcrJJyYoS8b6TQWYdN2SjRd03V2-UcW7MV67pkmAXqtzAYHadUsP2YUOl~MmIxfpoApJGoTFUlkhiBK0W7SwM4tX-9HGUQaQ0Gi3KFSG~ZsNngcbcB0YHMvzZDiBgSgvdmagobgLJhfsoouT0GqzIs6y9-A~3WSXd4e9VodSbM864e~9hJd0WWkNxjNvotq~Q-DikvsPxlTzq~yUbbO-1UR~5Vf~EOHhsxF-cHlsWccXpnHZuB~MPTQaIykc04Zyp3YQdUjVyAa209uwALI7E1u0iyP5JVtMyG7P8PKwOciuOUt5w__&Key-Pair-Id=K2L8F4GPSG1IFC
Resolving cas-bridge.xethub.hf.co (cas-bridge.xethub.hf.co)... 13.227.50.35, 13.227.50.117, 13.227.50.76, ...
Connecting to cas-bridge.xethub.hf.co (cas-bridge.xethub.hf.co)|13.227.50.35|:443... connected.
ERROR: cannot verify cas-bridge.xethub.hf.co's certificate, issued by 'CN=Amazon RSA 2048 M01,O=Amazon,C=US':
  Issued certificate not yet valid.
To connect to cas-bridge.xethub.hf.co insecurely, use `--no-check-certificate'.





