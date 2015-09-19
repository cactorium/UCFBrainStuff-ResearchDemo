#include "eeg.h"

#include <iostream>

Emotiv::Emotiv(): Emotiv(EMOKIT_VID, EMOKIT_PID) {
}

Emotiv::Emotiv(uint32_t device_vid, uint32_t device_pid):
        dev(nullptr), vid(device_vid), pid(device_pid), inited(false) {
    dev = emokit_create();
}

Emotiv::~Emotiv() {
    if (dev == nullptr || !inited) {
        return;
    }
    emokit_close(dev);
    emokit_delete(dev);
}

Result<bool> Emotiv::Open() {
    if (inited) {
        return Result<bool>(true);
    }
    if (emokit_get_count(dev, vid, pid) < 1) {
        return Result<bool>();
    }
    if (emokit_open(dev, vid, pid, 1) < 0) {
        return Result<bool>();
    }
    inited = true;
    return Result<bool>(true);
}

Result<Emotiv::Frame> Emotiv::Next() {
    auto r = emokit_read_data_timeout(dev, 1000);
    if (r <= 0) {
        if (r < 0) {
            std::cerr << "Error reading from headset\n" << std::endl;
        } else {
            std::cerr << "Headset timeout\n" << std::endl;
        }
        return Result<Frame>();
    }
    return Result<Frame>(emokit_get_next_frame(dev));
}
