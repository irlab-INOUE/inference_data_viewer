cmake_minimum_required(VERSION 3.18 FATAL_ERROR)
set (CMAKE_CXX_FLAGS "-O3 -g3 -std=c++17")
project(getdistance)

include_directories(/usr/include ${PROJECT_SOURCE_DIR})
if(APPLE)
  include_directories(/usr/local/include /opt/homebrew/include)
endif(APPLE)

link_directories(${PROJECT_SOURCE_DIR})
if(APPLE)
  link_directories(/usr/local/lib /opt/homebrew/lib)
endif(APPLE)

find_package (OpenCV REQUIRED)

add_executable (send_urg src/send_urg.cpp)	# src/GetUrg3d.cpp src/matrix.cpp
target_link_libraries(send_urg zmq)			# urg3d ${OpenCV_LIBRARIES}
