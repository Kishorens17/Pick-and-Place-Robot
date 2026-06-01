#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import time

class SimpleGripperTest(Node):
    def __init__(self):
        super().__init__('simple_gripper_test')
        
        self.publisher = self.create_publisher(
            JointTrajectory, 
            '/joint_trajectory_controller/joint_trajectory',
            10
        )
        
        self.get_logger().info('Simple Gripper Test Started')
        self.get_logger().info('Sending gripper open/close commands...')
        
        # Give Gazebo time to start
        time.sleep(2)
        
        # Send commands
        self.test_gripper()
    
    def send_trajectory(self, positions, duration=1.0):
        """Send joint trajectory command"""
        msg = JointTrajectory()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.joint_names = [
            'joint_1', 'joint_2', 'joint_3', 'joint_4',
            'left_finger_joint', 'right_finger_joint'
        ]
        
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(sec=int(duration), nanosec=int((duration % 1) * 1e9))
        
        msg.points = [point]
        self.publisher.publish(msg)
        self.get_logger().info(f'Sent: {positions}')
        time.sleep(duration + 0.5)
    
    def test_gripper(self):
        """Test gripper opening and closing"""
        
        for i in range(3):
            # Gripper CLOSED
            self.get_logger().info('Closing gripper...')
            self.send_trajectory([0.0, 0.0, 0.0, 0.0, -0.4, 0.4], duration=2.0)
            
            # Gripper OPEN
            self.get_logger().info('Opening gripper...')
            self.send_trajectory([0.0, 0.0, 0.0, 0.0, 0.4, -0.4], duration=2.0)
        
        self.get_logger().info('Test complete!')
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    test = SimpleGripperTest()
    rclpy.spin(test)

if __name__ == '__main__':
    main()