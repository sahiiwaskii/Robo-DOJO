import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('rover_description')
    desc = xacro.process_file(os.path.join(share, 'urdf', 'rover.urdf.xacro')).toxml()
    rviz_config = os.path.join(share, 'rviz', 'rover.rviz')
    return LaunchDescription([
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             parameters=[{'robot_description': desc}]),
        Node(package='joint_state_publisher_gui', executable='joint_state_publisher_gui'),
        Node(package='rviz2', executable='rviz2',
             arguments=['-d', rviz_config] if os.path.exists(rviz_config) else []),
    ])
