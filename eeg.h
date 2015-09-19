#pragma once

#ifndef EEG_H
#define EEG_H

#include <emokit/emokit.h>

class Emotiv {
private:
    struct emokit_device* dev;
public:
    Emotiv();
    Emotiv(int device_vid, int device_pid);
    ~Emotiv();

};

#endif
