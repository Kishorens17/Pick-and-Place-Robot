#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math
import time

class GripperController(Node):
    def __init__(self):
        super().__init__('gripper_controller')
        
        self.publisher = self.create_publisher(
            JointState, '/joint_states', 10
        )
        
        self.timer = self.create_timer(0.1, self.timer_callback)
        
        # All joint names including gripper
        self.joint_names = [
            'joint_1', 'joint_2', 'joint_3', 'joint_4',
            'left_finger_joint', 'right_finger_joint'
        ]
        
        self.start_time = time.time()
        
        self.get_logger().info('Gripper Controller Started')
        self.get_logger().info('Arm moves in sinusoidal pattern')
        self.get_logger().info('Gripper opens/closes periodically')
        
    def timer_callback(self):
        elapsed = time.time() - self.start_time
        
        # Arm motion
        arm_positions = [
            math.sin(elapsed) * 0.5,           # joint_1
            math.cos(elapsed) * 0.3,           # joint_2
            math.sin(elapsed * 0.7) * 0.4,     # joint_3
            math.cos(elapsed * 0.5) * 0.3      # joint_4
        ]
        
        # Gripper motion - opens and closes every 3 seconds
        gripper_state = math.sin(elapsed / 1.5)  # Smooth oscillation
        left_finger = gripper_state * 0.4
        right_finger = -gripper_state * 0.4
        
        gripper_positions = [left_finger, right_finger]
        
        # Combine all positions
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = arm_positions + gripper_positions
        msg.velocity = [0.1] * 6
        msg.effort = [10.0, 10.0, 10.0, 10.0, 5.0, 5.0]
        
        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    controller = GripperController()
    rclpy.spin(controller)
    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()