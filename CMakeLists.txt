cmake_minimum_required(VERSION 3.8)
project(rover_description)
find_package(ament_cmake REQUIRED)
install(DIRECTORY urdf meshes launch worlds rviz models config
  DESTINATION share/${PROJECT_NAME})
ament_package()
