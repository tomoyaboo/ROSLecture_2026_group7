# モジュールのインポート（ROS2関連）
import rclpy
from rclpy.node import Node

from std_msgs.msg import String

# 標準ライブラリ
import subprocess
import tempfile
import os
import wave
import audioop

# Whisper用
from faster_whisper import WhisperModel


class SpeechRecognitionNode(Node):
    def __init__(self):
        super().__init__("speech_recognition_node")

        self.speech_pub = self.create_publisher(
            msg_type=String,
            topic="speech_text",
            qos_profile=10
        )

        # ===== 設定 =====
        self.record_seconds = 3
        self.sample_rate = 16000
        self.model_size = "tiny"
        self.language = "ja"

        # 無音判定のしきい値
        # 小さくすると無音判定されにくい
        # 大きくすると無音判定されやすい
        self.silence_threshold = 300

        self.get_logger().info("Whisper音声認識ノードを開始しました")
        self.get_logger().info("Whisperモデルを読み込み中...")

        self.model = WhisperModel(
            self.model_size,
            device="cpu",
            compute_type="int8"
        )

        self.get_logger().info("Whisperモデルの読み込み完了")
        self.get_logger().info("/speech_text に認識結果を送信します")

    def record_audio(self):
        """
        arecordコマンドでマイク音声を録音してwavファイルに保存する
        """
        temp_file = tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        )
        wav_path = temp_file.name
        temp_file.close()

        self.get_logger().info(f"{self.record_seconds}秒間話してください...")

        cmd = [
            "arecord",
            "-d", str(self.record_seconds),
            "-r", str(self.sample_rate),
            "-c", "1",
            "-f", "S16_LE",
            wav_path
        ]

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=self.record_seconds + 2
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("録音処理がタイムアウトしました")

        if result.returncode != 0:
            raise RuntimeError(f"録音に失敗しました: {result.stderr}")

        return wav_path

    def is_silent_audio(self, wav_path: str):
        """
        録音されたwavの音量が小さすぎるか判定する
        """
        try:
            with wave.open(wav_path, "rb") as wf:
                frames = wf.readframes(wf.getnframes())
                sample_width = wf.getsampwidth()

            rms = audioop.rms(frames, sample_width)
            self.get_logger().info(f"録音音量RMS: {rms}")

            return rms < self.silence_threshold

        except Exception as e:
            self.get_logger().warn(f"音量チェックに失敗しました: {e}")
            return False

    def recognize_audio(self, wav_path: str):
        """
        wavファイルをWhisperで文字起こしする
        """
        segments, info = self.model.transcribe(
            wav_path,
            language=self.language,
            beam_size=1,
            vad_filter=False
        )

        text = ""
        for segment in segments:
            text += segment.text

        return text.strip()

    def normalize_command(self, text: str):
        """
        認識結果をHAVE / LOSTに変換する
        """
        original_text = text
        text = text.strip()
        lower_text = text.lower()

        self.get_logger().info(f"normalize前の認識文字列: [{original_text}]")

        # HAVE系
        have_words = [
            "have",
            "ハブ",
            "はぶ",
            "持って",
            "もって",
            "持っています",
            "持ってます",
            "あります",
            "ある",
            "見つけた",
            "みつけた",
            "拾った",
            "ひろった",
        ]

        # LOST系
        lost_words = [
            "lost",
            "ロスト",
            "ろすと",
            "なく",
            "無く",
            "失く",
            "ない",
            "ありません",
            "落とした",
            "おとした",
            "失いました",
            "うしないました",
            "見失った",
            "みうしなった",
        ]

        for word in have_words:
            if word in text or word in lower_text:
                return "HAVE"

        for word in lost_words:
            if word in text or word in lower_text:
                return "LOST"

        return "UNKNOWN"

    def publish_text(self, text: str):
        """
        /speech_text にString型で送信する
        """
        msg = String()
        msg.data = text

        self.speech_pub.publish(msg)
        self.get_logger().info(f"/speech_text に送信: {text}")

    def run(self):
        while rclpy.ok():
            wav_path = None

            try:
                wav_path = self.record_audio()

                # 無音ならWhisperに渡さない
                if self.is_silent_audio(wav_path):
                    self.get_logger().warn("音声が小さすぎるため，Whisper認識をスキップします")
                    self.publish_text("UNKNOWN")
                    continue

                self.get_logger().info("Whisperで認識中...")
                recognized_text = self.recognize_audio(wav_path)

                self.get_logger().info(f"認識結果: {recognized_text}")

                if recognized_text == "":
                    self.get_logger().warn("認識結果が空でした")
                    command = "UNKNOWN"
                else:
                    command = self.normalize_command(recognized_text)

                self.get_logger().info(f"変換後コマンド: {command}")

                self.publish_text(command)

            except KeyboardInterrupt:
                break

            except Exception as e:
                self.get_logger().error(f"音声認識中にエラー: {e}")

            finally:
                if wav_path is not None and os.path.exists(wav_path):
                    os.remove(wav_path)


def main(args=None):
    rclpy.init(args=args)

    node = SpeechRecognitionNode()

    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
