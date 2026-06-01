import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import time

class TestGripperSimple(Node):
    def __init__(self):
        super().__init__('test_gripper_simple')
        
        self.publisher = self.create_publisher(JointState, '/joint_states', 10)
        
        self.get_logger().info('Publishing joint states with gripper motion...')
        
        for i in range(5):
            # Gripper closed
            self.publish_gripper(-0.4, 0.4)
            time.sleep(2)
            
            # Gripper open
            self.publish_gripper(0.4, -0.4)
            time.sleep(2)
        
        self.get_logger().info('Test complete!')
    
    def publish_gripper(self, left, right):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'left_finger_joint', 'right_finger_joint']
        msg.position = [0.0, 0.0, 0.0, 0.0, left, right]
        msg.velocity = [0.0] * 6
        msg.effort = [0.0] * 6
        
        self.publisher.publish(msg)
        self.get_logger().info(f'Gripper: left={left:.1f}, right={right:.1f}')

def main(args=None):
    rclpy.init(args=args)
    test = TestGripperSimple()
    rclpy.shutdown()

if __name__ == '__main__':
    main()