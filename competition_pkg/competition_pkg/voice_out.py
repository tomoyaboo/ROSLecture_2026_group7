#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import subprocess


class VoiceOutput(Node):
    def __init__(self):
        super().__init__('voice_output')

        # 他の担当者のコードから文字列を受け取るトピック
        self.subscription = self.create_subscription(
            String,
            '/voice_output',
            self.voice_callback,
            10
        )

        self.get_logger().info('VoiceOutput node started.')

    def speak(self, text):
        self.get_logger().info(f'Speaking: {text}')

        # Ubuntuの音声読み上げコマンド
        subprocess.run(['spd-say', text])

    def voice_callback(self, msg):
        command = msg.data

        if command == 'VoOut-Yes':
            self.speak('鍵があります')

        elif command == 'VoOut-No':
            self.speak('鍵がないです')

        elif command == 'VoOut-have':
            self.speak('鍵持ってるんですね')

        else:
            self.get_logger().warn(f'Unknown voice command: {command}')


def main(args=None):
    rclpy.init(args=args)

    node = VoiceOutput()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()