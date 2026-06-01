cmake_minimum_required(VERSION 3.8)
project(robotic_arm_sim)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(gazebo_ros_pkgs REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# Copy URDF files
install(DIRECTORY urdf DESTINATION share/${PROJECT_NAME})

# Copy launch files
install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})

# Install Python nodes
install(PROGRAMS
  src/pick_place_controller.py
  src/gripper_controller.py
  src/simple_gripper_test.py
  src/autonomous_pick_place.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
