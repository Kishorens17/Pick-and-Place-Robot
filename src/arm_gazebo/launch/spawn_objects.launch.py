from launch import LaunchDescription
from launch_ros.actions import Node
import os

def generate_launch_description():
    
    spawn_cube_1 = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'cube_1',
            '-file', 'model://cube_20k/model.sdf',
            '-x', '0.3', '-y', '-0.2', '-z', '0.1'
        ]
    )
    
    spawn_cube_2 = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'cube_2',
            '-file', 'model://cube_20k/model.sdf',
            '-x', '0.4', '-y', '0.1', '-z', '0.1'
        ]
    )
    
    return LaunchDescription([spawn_cube_1, spawn_cube_2])