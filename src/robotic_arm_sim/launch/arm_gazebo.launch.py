import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_dir = get_package_share_directory('robotic_arm_sim')
    gazebo_pkg_dir = get_package_share_directory('gazebo_ros')
    
    # Start Gazebo server
    gazebo_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_pkg_dir, 'launch', 'gazebo.launch.py')
        )
    )
    
    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        arguments=[os.path.join(pkg_dir, 'urdf', 'arm.urdf')],
        output='screen'
    )
    
    # Spawn robot
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'pick_place_arm',
            '-file', os.path.join(pkg_dir, 'urdf', 'arm.urdf')
        ],
        output='screen'
    )
    
    return LaunchDescription([
        gazebo_server,
        robot_state_publisher,
        spawn_robot
    ])