cmake_minimum_required(VERSION 3.9)
project(vamos-experiments)

set(CMAKE_VERBOSE_MAKEFILE 1)
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

find_package(shamon REQUIRED)

include_directories(${shamon_INCLUDE_DIRS})

get_target_property(shamon_shamon-lib shamon-lib LOCATION)
get_target_property(shamon_shamon-ringbuf shamon-ringbuf LOCATION)
get_target_property(shamon_shamon-shmbuf shamon-shmbuf LOCATION)
get_target_property(shamon_shamon-streams shamon-streams LOCATION)
get_filename_component(shamon_LIBRARIES_DIRS_lib ${shamon_shamon-lib} DIRECTORY)
get_filename_component(shamon_LIBRARIES_DIRS_core ${shamon_shamon-ringbuf} DIRECTORY)
get_filename_component(shamon_LIBRARIES_DIRS_shmbuf ${shamon_shamon-shmbuf} DIRECTORY)
get_filename_component(shamon_LIBRARIES_DIRS_streams ${shamon_shamon-streams} DIRECTORY)

if (vamos_compiler_DIR)
	message(STATUS "vamos_compiler_DIR=${vamos_compiler_DIR}")
else()
	message(FATAL_ERROR "Need to set vamos_compiler_DIR variable")
endif()

configure_file(${CMAKE_CURRENT_SOURCE_DIR}/Makefile.config.in
	       ${CMAKE_CURRENT_SOURCE_DIR}/Makefile.config)

configure_file(${CMAKE_CURRENT_SOURCE_DIR}/setup-vars.sh.in
	       ${CMAKE_CURRENT_SOURCE_DIR}/setup-vars.sh)

configure_file(${CMAKE_CURRENT_SOURCE_DIR}/config.py.in
	       ${CMAKE_CURRENT_SOURCE_DIR}/config.py)

add_executable(gennums gennums.c)
target_compile_options(gennums PRIVATE -O3)
