#pragma once

#ifndef WINDOW_H
#define WINDOW_H

#include <cstdio>
#include <cstdint>

#include <fstream>
#include <iostream>
#include <memory>
#include <vector>

#include <GL/glew.h>
#include <GLFW/glfw3.h>

struct GLState;

void key_callback(GLFWwindow* window, int key, int scancode, int action, int mods);
void window_size_callback(GLFWwindow* window, int width, int height);

GLuint LoadShaders(const char* vertex_file_path, const char* fragment_file_path);

void SetupWindow(GLFWwindow *window);
void DrawFrame(uint32_t uniformVal, uint32_t chosen);

#endif
