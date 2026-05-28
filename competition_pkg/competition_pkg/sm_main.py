#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration

from geometry_msgs.msg import Twist
from std_msgs.msg import String

from yasmin import StateMachine
from yasmin_viewer import YasminViewerPub

# 各ステートをimport
from .states import wait4start
from .states import ???
from .states import ???
from .states import ???
from .states import ???
from .states import question
from .states import voice_recognirion


class StateMachineNode(Node):
    def __init__(self):
        super().__init__("success")

        self.get_logger().info("<< PLEASE ENTER TO START >>")
        self.get_logger().info("Task Start!!")

        # StateMachineを作成
        sm = StateMachine(outcomes=["EXIT"])

        # ----------------------------------------------
        # スタート待ち
        sm.add_state(
            name="Wait4start",
            state=wait4start.Wait4startState(node=self),
            transitions={
                "success": "te-ichi",
            },
        )

        # 定位置移動
        sm.add_state(
            name="te-ichi",
            state=???,
            transitions={
                ??? : "of-recog",
            },
        )

        # ----------------------------------------------
        # 物体認識
        sm.add_state(
            name="of-recog",
            state=???,
            transitions={
                ??? : "VoOut-Yes",
                ??? : "Question",
            }
        )

        # ----------------------------------------------
        # 「カギあります」音声１
        sm.add_state(
            name="VoOut-Yes",
            state=???,
            transitions={
                ??? : "EXIT",
            },
        )

        #「持っているか聞く」

        sm.add_state(
            name="Question",
            state=question.QuestionState(node=self),
            transitions={
                "success": "VoiceRecognition",
            },
        )

        # ----------------------------------------------

        # 音声認識
        sm.add_state(
            name="VoiceRecognition",
            state=voice_recognirion.VoRecofg(node=self),
            transitions={
                "HAVE": "VoOut-have",
                "LOST": "search",
                "retry": "Question",
            },
        )

        # ----------------------------------------------


        # ----------------------------------------------
        # 探し回る
        sm.add_state(
            name="search",
            state=???,
            transitions={
                ???: "VoOut-Yes",
                ???: "VoOut-No",
            },
        )
        # ----------------------------------------------


        # 「カギないです」音声２
        sm.add_state(
            name="VoOut-No",
            state=???,
            transitions={
                ???: "Exit",
            },
        )

        # ----------------------------------------------
        # 「鍵持っている」音声３
        sm.add_state(
            name="VoOut-Have",
            state=???,
            transitions={
                ??? : "EXIT",
            },
        )

        # ----------------------------------------------
        # Yasmin Viewer用
        YasminViewerPub(fsm_name="SM_MAIN", fsm=sm)

        # StateMachine実行
        outcome = sm()
        self.get_logger().info("State Machine finished with outcome: " + outcome)

    def speech_callback(self, msg: String):
        self.latest_speech_text = msg.data
        self.get_logger().info(f"音声認識結果を受信: {msg.data}")


def shutdown(node: Node):
    node.get_logger().info("Shutdown!!")

    pub = node.create_publisher(msg_msg = Twist, topic="cmd_vel", qos_profile=10)
    pub.publish(Twist())

    node.get_clock().sleep_for(Duration(nanoseconds=100))
    node.destroy_publisher(pub)


def main(args=None):
    rclpy.init(args=args)

    node = None

    try:
        node = StateMachineNode()

    except KeyboardInterrupt:
        pass

    finally:
        if node is not None:
            shutdown(node)
            node.destroy_node()

        rclpy.shutdown()


if __name__ == "__main__":
    main()