import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('rover_description')
    desc = xacro.process_file(os.path.join(share, 'urdf', 'rover.urdf.xacro')).toxml()
    rviz_config = os.path.join(share, 'rviz', 'rover.rviz')

    rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='true',
        description='Launch RViz2 alongside Gazebo'
    )

    world = os.path.join(share, 'worlds', 'gamefield.world')
    gz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r ' + world}.items()
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config] if os.path.exists(rviz_config) else [],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(LaunchConfiguration('rviz'))
    )

    return LaunchDescription([
        rviz_arg,
        SetEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH',
            os.pathsep.join([
                os.path.dirname(share),
                os.path.join(share, 'models')
            ])
        ),
        gz,
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': desc, 'use_sim_time': True}]
        ),
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-topic', 'robot_description', '-name', 'rover', '-z', '0.058']
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                '/world/gamefield/model/rover/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model',
                '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
                '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
                '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
                '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            ],
            remappings=[('/world/gamefield/model/rover/joint_state', '/joint_states')]
        ),
        rviz_node,
    ])
