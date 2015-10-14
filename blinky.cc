// Lots of stuff copied from lots of OpenGL tutorials!
#include <GL/glew.h>
#include <GLFW/glfw3.h>

#include <algorithm>
#include <atomic>
#include <array>
#include <iostream>
#include <thread>
#include <vector>

#include "custom-processor.h"
#include "eeg.h"
#include "processor.h"
#include "window.h"

extern std::atomic<DemoMode> newMode;

void error_callback(int error, const char* description);

void error_callback(int error, const char* description) {
    fputs(description, stderr);
}

void dumpQualityLevels(const Emotiv::Frame& f);

uint32_t next_msequence63(uint32_t i) {
    const auto lsb = i & 0x00000001;
    const auto lsb2 = (i & (0x00000001 << 5)) >> 5;
    return (i >> 1) | ((lsb ^ lsb2) << 5);
};

void dumpQualityLevels(const Emotiv::Frame& f) {
    std::vector<short> levels({f.cq.F3, f.cq.FC6, f.cq.P7,
            f.cq.T8, f.cq.F7, f.cq.F8, f.cq.T7, f.cq.P8,
            f.cq.AF4, f.cq.F4, f.cq.AF3, f.cq.O2, f.cq.O1,
            f.cq.FC5});
    std::cerr << "Quality levels: ";
    for (auto q : levels) {
        std::cerr << q << " ";
    }
    std::cerr << std::endl;
}

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
    std::atomic<uint32_t> chosen(0x0000);
    std::thread emokitThread([&]() {
        std::cerr << "emokit thread start" << std::endl;
        auto oe = Emotiv::Create(0x1234, 0xed02);
        if (oe.Empty()) {
            failed.store(true);
            std::cerr << "unable to connect to headset" << std::endl;
            return;
        }
        auto e = oe.Unwrap();
        std::cerr << "emokit thread inited" << std::endl;
        auto stillRunning = running.load();
        std::cerr << "emokit thread inited2" << std::endl;
        CustomProcessor p;
        auto newFrame = e.Next();
        int counter = 0;
        while (stillRunning /* && !newFrame.Empty() */) {
            if (p.Mode() != newMode.load()) {
                p.SetMode(newMode);
            }
            auto isSync = isSyncFrame.load();
            if (isSync) {
                auto tmp = isSync;
                isSyncFrame.compare_exchange_strong(tmp, false);
            }
            p.ProcessFrame(newFrame.Unwrap(), isSync);
            if (!(counter % 64)) {
                dumpQualityLevels(newFrame.Unwrap());
                auto result = p.GetProcessingResult();
                std::cerr << "Current best is " << result.offset/4 << 
                    " with confidence " << result.confidence << std::endl;
                if (result.confidence > 0) {
                    chosen.store(result.offset/4);
                }
            }

            newFrame = e.Next();
            stillRunning = running.load();
            counter++;
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
        uint32_t chosn = chosen.load();
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        DrawFrame(vals, chosn);
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
