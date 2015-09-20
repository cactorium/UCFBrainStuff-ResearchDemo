#pragma once

#ifndef EEG_H
#define EEG_H

#include <cassert>

#include "option.h"

#include <emokit/emokit.h>

class Emotiv {
private:
    struct emokit_device* dev;
    uint32_t vid, pid;
    bool opened;
    
    Emotiv();
    Emotiv(uint32_t device_vid, uint32_t device_pid);
    Option<bool> Open();
public:
    Emotiv(Emotiv &rhs) = delete;
    Emotiv(Emotiv &&rhs);
    ~Emotiv();

    using Frame = struct emokit_frame;

    static Option<Emotiv> Create();
    static Option<Emotiv> Create(uint32_t device_vid, uint32_t device_pid);

    Option<Frame> Next();
};

#endif
