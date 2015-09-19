#pragma once

#ifndef BLINKY_H
#define BLINKY_H

#include "eeg.h"

class EmotivProcessor {
public:
    EmotivProcessor(): frame_num(0) {;}
    ~EmotivProcessor() {;}

    void ProcessFrame(const Emotiv::Frame &f);
protected:
    int frame_num;
};

#endif
