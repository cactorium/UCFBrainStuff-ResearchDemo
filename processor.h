#pragma once

#ifndef PROCESSOR_H
#define PROCESSOR_H

#include "eeg.h"

enum DemoMode {
    TRAINING,
    PROCESSING
};

class EmotivProcessor {
public:
    EmotivProcessor(): mode(TRAINING), frame_num(0) {;}
    ~EmotivProcessor() {;}

    void ProcessFrame(const Emotiv::Frame &f, bool isSyncFrame);

    void SetMode(DemoMode m);
    DemoMode Mode() {return mode;}
protected:
    DemoMode mode;
    int frame_num;
};

#endif
