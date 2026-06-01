import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_dir = get_package_share_directory('robotic_arm_sim')
    
    # MoveIt
    moveit_config_package = 'robotic_arm_sim'
    moveit_config_dir = os.path.join(pkg_dir, 'config', 'moveit_config')
    
    # Load SRDF
    srdf_file = os.path.join(moveit_config_dir, 'arm.srdf')
    urdf_file = os.path.join(pkg_dir, 'urdf', 'arm.urdf')
    
    # MoveIt nodes
    move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[
            {'robot_description': open(urdf_file).read()},
            {'robot_description_semantic': open(srdf_file).read()},
        ]
    )
    
    # RViz with MoveIt plugin
    rviz_config = os.path.join(pkg_dir, 'config', 'moveit_config', 'moveit.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        output='log',
        arguments=['-d', rviz_config]
    )
    
    return LaunchDescription([
        move_group_node,
        rviz
    ])