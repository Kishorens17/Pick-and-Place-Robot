#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from gazebo_msgs.srv import SetEntityState
from geometry_msgs.msg import Pose, Twist, Quaternion, Point
import time

class GripperDirectControl(Node):
    def __init__(self):
        super().__init__('gripper_direct_control')
        
        self.client = self.create_client(SetEntityState, '/gazebo/set_entity_state')
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /gazebo/set_entity_state service...')
        
        self.get_logger().info('Connected to Gazebo! Testing gripper...')
        time.sleep(1)
        self.test_gripper()
    
    def move_finger(self, finger_name, angle):
        """Move a finger by setting its pose"""
        request = SetEntityState.Request()
        request.state.name = finger_name
        request.state.pose = Pose(
            position=Point(x=0.0, y=0.0, z=0.0),
            orientation=Quaternion(x=0.0, y=0.0, z=angle, w=1.0)
        )
        request.state.twist = Twist()
        request.state.reference_frame = 'world'
        
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
    
    def test_gripper(self):
        for i in range(3):
            self.get_logger().info(f'Cycle {i+1}: Closing gripper...')
            self.move_finger('left_finger', -0.4)
            self.move_finger('right_finger', 0.4)
            time.sleep(2)
            
            self.get_logger().info(f'Cycle {i+1}: Opening gripper...')
            self.move_finger('left_finger', 0.4)
            self.move_finger('right_finger', -0.4)
            time.sleep(2)
        
        self.get_logger().info('Test complete!')

def main(args=None):
    rclpy.init(args=args)
    test = GripperDirectControl()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
