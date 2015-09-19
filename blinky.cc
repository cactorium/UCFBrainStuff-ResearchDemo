// Lots of stuff copied from lots of OpenGL tutorials!
#include <GL/glew.h>
#include <GLFW/glfw3.h>

#include <algorithm>
#include <atomic>
#include <iostream>
#include <thread>
#include <vector>

#include "eeg.h"
#include "processor.h"
#include "window.h"

extern std::atomic<DemoMode> newMode;

void error_callback(int error, const char* description);

void error_callback(int error, const char* description) {
    fputs(description, stderr);
}

uint32_t next_msequence63(uint32_t i) {
    const auto lsb = i & 0x00000001;
    const auto lsb2 = (i & (0x00000001 << 5)) >> 5;
    return (i >> 1) | ((lsb ^ lsb2) << 5);
};

int main(void) {
    GLFWwindow* window;
    glfwSetErrorCallback(error_callback);
    if (!glfwInit()) exit(EXIT_FAILURE);
    window = glfwCreateWindow(640, 480, "Simple example", NULL, NULL);
    // window = glfwCreateWindow(640, 480, "My Title", glfwGetPrimaryMonitor(), NULL);
    if (!window) {
        glfwTerminate();
        exit(EXIT_FAILURE);
    }
    glfwMakeContextCurrent(window);
    GLenum err = glewInit();
    if (err != GLEW_OK) {
        std::cerr << "glew failed to initialize " <<
                glewGetErrorString(err) << std::endl;
        glfwTerminate();
        exit(EXIT_FAILURE);
    }
    std::atomic<bool> running(true), failed(false), isSyncFrame(false);
    std::thread emokitThread([&]() {
        std::cerr << "emokit thread start" << std::endl;
        Emotiv e(0x1234, 0xed02);
        if (e.Open().Empty()) {
            failed.store(true);
            std::cerr << "unable to connect to headset" << std::endl;
            return;
        }
        std::cerr << "emokit thread inited" << std::endl;
        auto stillRunning = running.load();
        std::cerr << "emokit thread inited2" << std::endl;
        EmotivProcessor p;
        auto newFrame = e.Next();
        while(stillRunning && !newFrame.Empty()) {
            if (p.Mode() != newMode.load()) {
                p.SetMode(newMode);
            }
            auto isSync = isSyncFrame.load();
            if (isSync) {
                auto tmp = isSync;
                isSyncFrame.compare_exchange_strong(tmp, false);
            }
            p.ProcessFrame(newFrame.Unwrap(), isSync);

            newFrame = e.Next();
            stillRunning = running.load();
        }
        failed.store(true);
        std::cerr << "emokit thread ended" << std::endl;
    });

    SetupWindow(window);

    auto seqs = std::vector<uint32_t>(16);
    uint32_t tmp = 1;
    for (auto i = 0u; i < seqs.size(); i++) {
        seqs[i] = tmp;
        for (auto j = 0u; j < 64/seqs.size(); j++) {
            tmp = next_msequence63(tmp);
        }
    }

    auto emokitFailed = failed.load();
    while (!glfwWindowShouldClose(window) && !emokitFailed) {
        if (seqs[0] == 1) {
            isSyncFrame.store(true);
        } else {
            isSyncFrame.store(false);
        }
        uint32_t vals = 0;
        for (auto i = 0u; i < seqs.size(); i++) {
            vals |= (seqs[i] & 1) << i;
        }
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        DrawFrame(vals);
        std::for_each(seqs.begin(), seqs.end(), [](uint32_t &val) {
            val = next_msequence63(val);
        });
        emokitFailed = failed.load();
        glfwPollEvents();
        glfwSwapBuffers(window);
    }

    glfwDestroyWindow(window);
    glfwTerminate();

    running.store(false);
    emokitThread.join();

    exit(EXIT_SUCCESS);
}
