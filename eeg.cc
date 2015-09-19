#include <iostream>

#include "eeg.h"

Emotiv::Emotiv(): Emotiv(EMOKIT_VID, EMOKIT_PID) {
}

Emotiv::Emotiv(uint32_t device_vid, uint32_t device_pid):
        dev(nullptr), vid(device_vid), pid(device_pid), inited(false), opened(false) {
    dev = emokit_create();
    inited = true;
}

Emotiv::~Emotiv() {
    if (dev == nullptr)
        return;
    if (opened)
        emokit_close(dev);
    emokit_delete(dev);
}

Option<bool> Emotiv::Open() {
    if (inited) {
        return Option<bool>(true);
    }
    if (emokit_get_count(dev, vid, pid) < 1) {
        return Option<bool>();
    }
    if (emokit_open(dev, vid, pid, 1) < 0) {
        return Option<bool>();
    }
    opened = true;
    return Option<bool>(true);
}

Option<Emotiv::Frame> Emotiv::Next() {
    auto r = emokit_read_data_timeout(dev, 1000);
    if (r <= 0) {
        if (r < 0) {
            std::cerr << "Error reading from headset\n" << std::endl;
        } else {
            std::cerr << "Headset timeout\n" << std::endl;
        }
        return Option<Frame>();
    }
    return Option<Frame>(emokit_get_next_frame(dev));
}
