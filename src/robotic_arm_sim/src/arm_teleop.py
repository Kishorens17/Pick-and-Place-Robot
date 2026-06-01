#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from pynput import keyboard
import math

class ArmTeleop(Node):
    def __init__(self):
        super().__init__('arm_teleop')
        
        self.publisher = self.create_publisher(
            JointState, '/joint_states', 10
        )
        
        self.joint_names = ['joint_1', 'joint_2', 'joint_3', 'joint_4']
        self.joint_values = [0.0, 0.0, 0.0, 0.0]
        self.step = 0.05  # Increment per key press
        
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()
        
        self.get_logger().info('Arm Teleop Started')
        self.get_logger().info('Controls:')
        self.get_logger().info('  1/2: Joint 1 (CCW/CW)')
        self.get_logger().info('  3/4: Joint 2 (Down/Up)')
        self.get_logger().info('  5/6: Joint 3 (Down/Up)')
        self.get_logger().info('  7/8: Joint 4 (Down/Up)')
        self.get_logger().info('  9/0: Gripper (Close/Open)')
        self.get_logger().info('  r: Reset')
    
    def on_key_press(self, key):
        try:
            char = key.char
            
            if char == '1':
                self.joint_values[0] -= self.step
            elif char == '2':
                self.joint_values[0] += self.step
            elif char == '3':
                self.joint_values[1] -= self.step
            elif char == '4':
                self.joint_values[1] += self.step
            elif char == '5':
                self.joint_values[2] -= self.step
            elif char == '6':
                self.joint_values[2] += self.step
            elif char == '7':
                self.joint_values[3] -= self.step
            elif char == '8':
                self.joint_values[3] += self.step
            elif char == 'r':
                self.joint_values = [0.0, 0.0, 0.0, 0.0]
            
            # Publish joint states
            msg = JointState()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.name = self.joint_names
            msg.position = self.joint_values
            msg.velocity = [0.0] * 4
            msg.effort = [0.0] * 4
            
            self.publisher.publish(msg)
            self.get_logger().info(f'Joint values: {[f"{v:.2f}" for v in self.joint_values]}')
            
        except AttributeError:
            pass

def main(args=None):
    rclpy.init(args=args)
    teleop = ArmTeleop()
    rclpy.spin(teleop)

if __name__ == '__main__':
    main()