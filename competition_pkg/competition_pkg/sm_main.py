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
from .states import te_ichistate
from .states import of_recog
from .states import of_recog2
from .states import search_state
from .states import voout_have
from .states import voout_no
from .states import voout_question
from .states import voout_yes
from .states import voice_recognirion


class StateMachineNode(Node):
    def __init__(self):
        super().__init__("success")

        self.get_logger().info("<< PLEASE ENTER TO START >>")
        self.get_logger().info("Task Start!!")
        map_yaml = "/HOME/ros2_lecture_ws/map.yaml"

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
            state=te_ichistate.TeiichiState(node=self),
            transitions={
                "success" : "of-recog",
                "failure" : "te-ichi",
            },
        )

        # ----------------------------------------------
        # 物体認識
        sm.add_state(
            name="of-recog",
            state=of_recog.ObRecogState(node=self),
            transitions={
                "success" : "VoOut-Yes",
                "failure": "Question",
            }
        )

        # ----------------------------------------------
        # 「カギあります」音声１
        sm.add_state(
            name="VoOut-Yes",
            state=voout_yes.VoOutYesState,
            transitions={
                "success" : "EXIT",
                "failure" : "EXIT"
            },
        )

        #「持っているか聞く」

        sm.add_state(
            name="Question",
            state=voout_question.QuestionState(node=self),
            transitions={
                "success": "VoiceRecognition",
            },
        )

        # ----------------------------------------------

        # 音声認識
        sm.add_state(
            name="VoiceRecognition",
            state=voice_recognirion.VoRecofg,
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
            state=search_state.SearchState(self, map_yaml),
            transitions={
                "moved": "of-recog2",
                "loop": "search",
                "finished": "VoOut-No"

            },
        )
        # ----------------------------------------------

        # ----------------------------------------------
        # 物体認識2
        sm.add_state(
            name="of-recog2",
            state=of_recog2.OfRecogState2(node=self),
            transitions={
                "success" : "VoOut-Yes",
                "failure" : "search",
            }
        )


        # 「カギないです」音声２
        sm.add_state(
            name="VoOut-No",
            state=voout_no.VoOutNoState,
            transitions={
                "success" : "Exit",
                "failure" : "Exit"
            },
        )

        # ----------------------------------------------
        # 「鍵持っている」音声３
        sm.add_state(
            name="VoOut-Have",
            state=voout_have.VoOutHaveState,
            transitions={
                "success" : "EXIT",
                "failure" : "EXIT"
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
