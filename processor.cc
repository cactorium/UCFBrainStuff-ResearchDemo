#include <iostream>

#include "processor.h"

void EmotivProcessor::SetMode(DemoMode m) {
    if (m == TRAINING) {
        std::cerr << "training mode set to training" << std::endl;
    } else {
        std::cerr << "training mode set to processing" << std::endl;
    }
    mode = m;
}
void EmotivProcessor::ProcessFrame(const Emotiv::Frame &f, bool isSyncFrame) {
    std::cerr << "Got frame data for frame " << frame_num << std::endl;

    frame_num++;
}

