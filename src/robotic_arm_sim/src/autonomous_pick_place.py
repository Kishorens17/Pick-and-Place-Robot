#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from visualization_msgs.msg import Marker
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
import time
import math

class RealisticPickPlace(Node):
    def __init__(self):
        super().__init__('realistic_pick_place')
        
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        self.marker_pub = self.create_publisher(Marker, '/visualization_marker', 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        
        self.joint_names = [
            'joint_1', 'joint_2', 'joint_3', 'joint_4',
            'left_finger_joint', 'right_finger_joint'
        ]
        
        self.current_pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.carrying_box = False
        self.carried_box_data = None
        
        # Box locations - positioned where gripper can reach
        self.pick_boxes = [
            {'x': 0.45, 'y': 0.25, 'angle': 0.5, 'name': 'Red Box 1', 'picked': False},
            {'x': 0.45, 'y': 0.0, 'angle': 0.0, 'name': 'Red Box 2', 'picked': False},
            {'x': 0.45, 'y': -0.25, 'angle': -0.5, 'name': 'Red Box 3', 'picked': False},
        ]
        
        self.place_stack = []
        self.place_location = {'x': 0.45, 'y': -0.45}
        
        # Create timer to continuously publish carried box
        self.box_update_timer = self.create_timer(0.05, self.update_carried_box)
        
        self.get_logger().info('=== Realistic Pick-and-Place with Synchronized Boxes ===')
        
        time.sleep(2)
        self.run_pick_place()
    
    def publish_joint_state(self, positions):
        """Publish joint state"""
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = positions
        msg.velocity = [0.0] * 6
        msg.effort = [0.0] * 6
        self.joint_pub.publish(msg)
        self.current_pos = positions
    
    def get_gripper_position(self):
        """Calculate gripper position based on current joint angles"""
        j1, j2, j3, j4, _, _ = self.current_pos
        
        # Forward kinematics (simplified)
        # Link lengths
        l1 = 0.3  # Link 1 height
        l2 = 0.3  # Link 2 length
        l3 = 0.25  # Link 3 length
        l4 = 0.18  # Link 4 + gripper
        
        # Calculate end effector position
        x = math.cos(j1) * (l2 * math.cos(j2) + l3 * math.cos(j2 + j3) + l4 * math.cos(j2 + j3 + j4))
        y = math.sin(j1) * (l2 * math.cos(j2) + l3 * math.cos(j2 + j3) + l4 * math.cos(j2 + j3 + j4))
        z = l1 + l2 * math.sin(j2) + l3 * math.sin(j2 + j3) + l4 * math.sin(j2 + j3 + j4)
        
        return x, y, z
    
    def update_carried_box(self):
        """Update position of carried box to follow gripper"""
        if self.carrying_box and self.carried_box_data:
            x, y, z = self.get_gripper_position()
            # Offset box slightly below gripper
            self.publish_box(900, x, y, z - 0.05, 1.0, 0.5, 0.0)  # Orange while carried
    
    def publish_box(self, marker_id, x, y, z, r, g, b, a=1.0):
        """Publish a single box marker"""
        marker = Marker()
        marker.header.frame_id = "base_link"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.id = marker_id
        marker.type = Marker.CUBE
        marker.action = Marker.ADD
        
        marker.pose.position.x = x
        marker.pose.position.y = y
        marker.pose.position.z = z
        marker.pose.orientation.w = 1.0
        
        marker.scale.x = 0.08
        marker.scale.y = 0.08
        marker.scale.z = 0.08
        
        marker.color.r = r
        marker.color.g = g
        marker.color.b = b
        marker.color.a = a
        
        marker.lifetime.sec = 0
        
        self.marker_pub.publish(marker)
    
    def delete_box(self, marker_id):
        """Delete a marker"""
        marker = Marker()
        marker.header.frame_id = "base_link"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.id = marker_id
        marker.action = Marker.DELETE
        self.marker_pub.publish(marker)
    
    def update_boxes(self):
        """Update all box visualizations"""
        marker_id = 0
        
        # Show pick boxes (red)
        for idx, box in enumerate(self.pick_boxes):
            if not box['picked']:
                self.publish_box(marker_id, box['x'], box['y'], 0.04, 1.0, 0.0, 0.0)
            else:
                self.delete_box(marker_id)
            marker_id += 1
        
        # Show placed boxes (green, stacked)
        for idx in range(len(self.place_stack)):
            z_height = 0.04 + (idx * 0.09)
            self.publish_box(100 + idx, self.place_location['x'], 
                           self.place_location['y'], z_height, 0.0, 1.0, 0.0)
    
    def smooth_move(self, target, steps=30):
        """Smooth interpolation"""
        start = self.current_pos.copy()
        
        for i in range(steps + 1):
            t = i / steps
            t = t * t * (3 - 2 * t)
            
            pos = [start[j] + (target[j] - start[j]) * t for j in range(6)]
            self.publish_joint_state(pos)
            time.sleep(0.03)
    
    def run_pick_place(self):
        """Main pick-place loop"""
        cycle = 0
        
        while True:
            for box_idx, box in enumerate(self.pick_boxes):
                if box['picked']:
                    continue
                
                cycle += 1
                self.get_logger().info(f"\n{'='*60}")
                self.get_logger().info(f"CYCLE {cycle}: {box['name']}")
                self.get_logger().info(f"{'='*60}")
                
                self.update_boxes()
                
                # 1. Home
                self.get_logger().info("[1/9] Home position")
                self.smooth_move([0.0, 0.0, 0.0, 0.0, 0.0, 0.0], steps=20)
                time.sleep(0.5)
                
                # 2. Rotate toward box
                self.get_logger().info(f"[2/9] Rotating to {box['name']}")
                self.smooth_move([box['angle'], 0.0, 0.0, 0.0, 0.03, -0.03], steps=20)
                time.sleep(0.5)
                
                # 3. Extend and approach
                self.get_logger().info("[3/9] Approaching box")
                self.smooth_move([box['angle'], -1.0, 0.8, 0.0, 0.03, -0.03], steps=30)
                time.sleep(0.5)
                
                # 4. Lower to box
                self.get_logger().info("[4/9] Lowering to box")
                self.smooth_move([box['angle'], -1.1, 1.4, -0.3, 0.03, -0.03], steps=35)
                time.sleep(0.8)
                
                # 5. Close gripper and pick box
                self.get_logger().info("[5/9] Grasping...")
                for i in range(15):
                    t = i / 15
                    grip = 0.03 - (t * 0.03)
                    self.publish_joint_state([box['angle'], -1.1, 1.4, -0.3, grip, -grip])
                    time.sleep(0.03)
                
                # Box is now grasped - start carrying it
                time.sleep(0.2)
                self.get_logger().info("    ✓ BOX GRASPED - now carrying!")
                box['picked'] = True
                self.carrying_box = True
                self.carried_box_data = box
                self.delete_box(box_idx)  # Remove from floor
                time.sleep(0.5)
                
                # 6. Lift
                self.get_logger().info("[6/9] Lifting box")
                self.smooth_move([box['angle'], -0.6, 0.5, 0.0, 0.0, 0.0], steps=30)
                time.sleep(0.5)
                
                # 7. Move to place
                place_angle = -0.8
                self.get_logger().info("[7/9] Moving to place location")
                self.smooth_move([place_angle, -0.6, 0.5, 0.0, 0.0, 0.0], steps=30)
                time.sleep(0.5)
                
                # 8. Lower to place
                self.get_logger().info("[8/9] Lowering to place")
                self.smooth_move([place_angle, -1.0, 1.3, -0.3, 0.0, 0.0], steps=30)
                time.sleep(0.5)
                
                # 9. Open gripper and place box
                self.get_logger().info("[9/9] Releasing...")
                for i in range(15):
                    t = i / 15
                    grip = 0.0 + (t * 0.03)
                    self.publish_joint_state([place_angle, -1.0, 1.3, -0.3, grip, -grip])
                    time.sleep(0.03)
                
                # Box is now placed
                time.sleep(0.2)
                self.get_logger().info("    ✓ BOX PLACED!")
                self.carrying_box = False
                self.delete_box(900)  # Remove carried box
                self.place_stack.append(box)
                self.update_boxes()
                time.sleep(0.5)
                
                # Return home
                self.get_logger().info("Returning home")
                self.smooth_move([0.0, -0.3, 0.2, 0.0, 0.0, 0.0], steps=25)
                self.smooth_move([0.0, 0.0, 0.0, 0.0, 0.0, 0.0], steps=20)
                time.sleep(1)
                
                self.get_logger().info(f"\n✓ Cycle {cycle} COMPLETE!")
                self.get_logger().info(f"Remaining: {sum(1 for b in self.pick_boxes if not b['picked'])}")
                self.get_logger().info(f"Placed: {len(self.place_stack)}")
                time.sleep(2)
            
            # All done
            self.get_logger().info("\n" + "="*60)
            self.get_logger().info("🎉 ALL BOXES TRANSFERRED! 🎉")
            self.get_logger().info("="*60)
            time.sleep(5)
            
            # Reset
            for box in self.pick_boxes:
                box['picked'] = False
            self.place_stack = []
            self.carrying_box = False
            self.update_boxes()

def main(args=None):
    rclpy.init(args=args)
    controller = RealisticPickPlace()
    rclpy.spin(controller)
    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()