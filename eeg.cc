#include <iostream>

#include "eeg.h"

Emotiv::Emotiv(): Emotiv(EMOKIT_VID, EMOKIT_PID) {
}

Emotiv::Emotiv(uint32_t device_vid, uint32_t device_pid):
        dev(nullptr), vid(device_vid), pid(device_pid), opened(false) {
    dev = emokit_create();
}

Emotiv::Emotiv(Emotiv &&rhs) {
    opened = rhs.opened;
    rhs.opened = false;

    dev = rhs.dev;
    rhs.dev = nullptr;

    vid = rhs.vid;
    pid = rhs.pid;

    rhs.vid = 0;
    rhs.pid = 0;
}

Emotiv::~Emotiv() {
    if (dev == nullptr)
        return;
    if (opened)
        emokit_close(dev);
    emokit_delete(dev);
}

Option<Emotiv> Emotiv::Create() {
    return Emotiv::Create(EMOKIT_VID, EMOKIT_PID);
}

Option<Emotiv> Emotiv::Create(uint32_t device_vid, uint32_t device_pid) {
    auto e = Emotiv(device_vid, device_pid);
    if (e.Open().Empty()) {
        return Option<Emotiv>();
    }
    return Option<Emotiv>(std::move(e));
}

Option<bool> Emotiv::Open() {
    if (opened) {
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

CopyableOption<Emotiv::Frame> Emotiv::Next() {
    if (!opened) return CopyableOption<Frame>();
    auto r = emokit_read_data_timeout(dev, 1000);
    if (r <= 0) {
        if (r < 0) {
            std::cerr << "Error reading from headset\n" << std::endl;
        } else {
            std::cerr << "Headset timeout\n" << std::endl;
        }
        return CopyableOption<Frame>();
    }
    return CopyableOption<Frame>(emokit_get_next_frame(dev));
}
