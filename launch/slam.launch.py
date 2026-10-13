import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('rover_description')
    slam_params = os.path.join(share, 'config', 'slam_toolbox.yaml')
    rviz_config = os.path.join(share, 'rviz', 'slam.rviz')

    sim = LaunchConfiguration('sim')
    rviz = LaunchConfiguration('rviz')
    use_sim_time = LaunchConfiguration('use_sim_time')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(share, 'launch', 'gazebo.launch.py')),
        launch_arguments={'rviz': 'false'}.items(),
        condition=IfCondition(sim),
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('slam_toolbox'), 'launch', 'online_async_launch.py')
        ),
        launch_arguments={
            'slam_params_file': slam_params,
            'use_sim_time': use_sim_time,
            'autostart': 'true',
        }.items(),
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2_slam',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(rviz),
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'sim',
            default_value='true',
            description='Launch Gazebo gamefield simulation before starting SLAM',
        ),
        DeclareLaunchArgument(
            'rviz',
            default_value='true',
            description='Launch RViz with map, scan, robot, and TF displays',
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation clock; set false when mapping with the physical RPLidar',
        ),
        gazebo,
        slam,
        rviz_node,
    ])
