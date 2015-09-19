#pragma once

#ifndef EEG_H
#define EEG_H

#include <cassert>

#include <emokit/emokit.h>

template <class T> class Option {
private:
    bool success;
    T t;
public:
    Option(): success(false) {;}
    Option(T t): success(true), t(t) {;}

    bool Empty() { return !success; }
    T Unwrap() {
        assert(success);
        return t;
    }
};

class Emotiv {
private:
    struct emokit_device* dev;
    uint32_t vid, pid;
    bool inited, opened;
public:
    Emotiv();
    Emotiv(uint32_t device_vid, uint32_t device_pid);
    ~Emotiv();

    using Frame = struct emokit_frame;

    Option<bool> Open();
    Option<Frame> Next();
};

#endif
