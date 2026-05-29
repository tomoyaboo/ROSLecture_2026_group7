#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration

from geometry_msgs.msg import Twist

from yasmin import StateMachine
from yasmin_viewer import YasminViewerPub

# 各ステートをimport
from .states import wait4start
from .states import question
from .states import voice_recognirion
from .states import of_recog


class StateMachineTestNode(Node):
    def __init__(self):
        super().__init__("state_main_test")

        self.get_logger().info("State main test start")

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

        # ----------------------------------------------
        # 定位置に移動する
        sm.add_state(
            name="te-ichi",
            state=question.QuestionState(node=self),
            transitions={
                "success": "of-recog",
            },
        )

        # ----------------------------------------------
        # 物体認識
        sm.add_state(
            name="of-recog",
            state=of_recog.ObRecogState(node=self),
            transitions={
                "success": "EXIT",
                "failure": "EXIT",
                "retry": "te-ichi",
            },
        )

        # ----------------------------------------------
        # Yasmin Viewer用
        YasminViewerPub(fsm_name="STATE_MAIN_TEST", fsm=sm)

        # StateMachine実行
        outcome = sm()
        self.get_logger().info("State Machine finished with outcome: " + outcome)


def shutdown(node: Node):
    node.get_logger().info("Shutdown!!")

    pub = node.create_publisher(
        msg_type=Twist,
        topic="cmd_vel",
        qos_profile=10
    )
    pub.publish(Twist())

    node.get_clock().sleep_for(Duration(nanoseconds=100))
    node.destroy_publisher(pub)


def main(args=None):
    rclpy.init(args=args)

    node = None

    try:
        node = StateMachineTestNode()

    except KeyboardInterrupt:
        pass

    finally:
        if node is not None:
            shutdown(node)
            node.destroy_node()

        rclpy.shutdown()


if __name__ == "__main__":
    main()
