cmake_minimum_required(VERSION 3.3)

if(COMMAND cmake_policy)
  cmake_policy(SET CMP0003 NEW)
endif(COMMAND cmake_policy)
#------------------------------------------------------------------------------
# Required CPM Setup - no need to modify - See: https://github.com/iauns/cpm
#------------------------------------------------------------------------------
set(CPM_DIR "${CMAKE_CURRENT_BINARY_DIR}/cpm-packages" CACHE TYPE STRING)
find_package(Git)
if(NOT GIT_FOUND)
message(FATAL_ERROR "CPM requires Git.")
endif()
if (NOT EXISTS ${CPM_DIR}/CPM.cmake)
message(STATUS "Cloning repo (https://github.com/iauns/cpm)")
execute_process(
  COMMAND "${GIT_EXECUTABLE}" clone https://github.com/iauns/cpm ${CPM_DIR}
  RESULT_VARIABLE error_code
  OUTPUT_QUIET ERROR_QUIET)
if(error_code)
  message(FATAL_ERROR "CPM failed to get the hash for HEAD")
endif()
endif()
include(${CPM_DIR}/CPM.cmake)

#------------------------------------------------------------------------------
# CPM Modules
#------------------------------------------------------------------------------

# TODO: Include any modules here...
CPM_AddModule("cpm-glfw"
    GIT_REPOSITORY "https://github.com/iauns/cpm-glfw")
CPM_AddModule("cpm-glew"
    GIT_REPOSITORY "https://github.com/iauns/cpm-glew")
CPM_Finish()

add_executable(blinky blinky.cc)
target_link_libraries(blinky ${CPM_LIBRARIES}) 
