#pragma once

#ifndef PROCESSOR_H
#define PROCESSOR_H

#include "eeg.h"

#include <vector>

const int kTrainingSets = 10;
const int kSensors = 14;
const float kQualityThreshold = 5.0f;
const float kCorrThreshold = 5.0f;

enum DemoMode {
    TRAINING,
    PROCESSING
};

enum SensorPosition {
	F3, FC6, P7, T8, F7, F8, T7, P8, AF4, F4, AF3, O2, O1, FC5, INVALID
};

const std::array<SensorPosition, kSensors> kSensorOrder {{
    F3, FC6, P7, T8, F7, F8, T7, P8, AF4, F4, AF3, O2, O1, FC5
}};

struct SignalResult {
    int offset;
    float confidence;
};

// typedef std::vector<float> Vectorf;

int getValueBySensorId(const SensorPosition &p, const Emotiv::Frame &f);
short getQualityBySensorId(const SensorPosition &p, const Emotiv::Frame &f);

class EmotivProcessor {
public:
    EmotivProcessor(): mode(TRAINING) {;}
    virtual void ProcessFrame(const Emotiv::Frame &f, bool isSyncFrame) = 0;
    virtual SignalResult GetProcessingResult() const = 0;

    virtual void SetMode(DemoMode m) = 0;
    virtual DemoMode Mode() const {return mode;}

protected:
    DemoMode mode;
};


#endif
