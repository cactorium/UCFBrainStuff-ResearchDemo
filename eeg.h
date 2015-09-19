#pragma once

#ifndef EEG_H
#define EEG_H

#include <cassert>

#include <emokit/emokit.h>

template <class T> class Result {
private:
    bool success;
    T t;
public:
    Result(): success(false) {;}
    Result(T t): success(true), t(t) {;}

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
    bool inited;
public:
    Emotiv();
    Emotiv(uint32_t device_vid, uint32_t device_pid);
    ~Emotiv();

    using Frame = struct emokit_frame;

    Result<bool> Open();
    Result<Frame> Next();
};

#endif
