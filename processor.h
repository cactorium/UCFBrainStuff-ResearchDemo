#pragma once

#ifndef PROCESSOR_H
#define PROCESSOR_H

#include "eeg.h"
#include "vector.h"

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

typedef std::vector<float> Vectorf;

/*
void normalize(Vectorf &v);
void fill(Vectorf &v, float val);
*/

struct SignalResult {
    int offset;
    float confidence;
};

class SignalProcessor {
public:
    SignalProcessor() : SignalProcessor(INVALID) {;}
    SignalProcessor(SensorPosition pos);
    ~SignalProcessor() {;}

    void ProcessFrame(int frame_num, const Emotiv::Frame &f, bool isSyncFrame);
    SignalResult GetProcessingResult() const;
    bool TrainingFinished() const;
    void SetMode(DemoMode m);
protected:
    // used for both modes
    DemoMode mode;
    SensorPosition pos;

    // used for training mode
    bool first_sync;
    float avg_quality;
    // std::vector<Vectorf> training_data;
    std::vector<FloatVector> training_data;
    std::vector<float> data_quality;
    // std::vector<float> tmp;
    FloatVector tmp;

    // used for processing mode
    // Vectorf templ;
    FloatVector templ;
    // Vectorf last;
    FloatVector last;
    // Vectorf last_quality;
    FloatVector last_quality;
    int last_corr;
    float confidence;
    FloatVector foo;
};

class EmotivProcessor {
public:
    EmotivProcessor();
    ~EmotivProcessor() {;}

    void ProcessFrame(const Emotiv::Frame &f, bool isSyncFrame);
    SignalResult GetProcessingResult() const;

    void SetMode(DemoMode m);
    DemoMode Mode() const {return mode;}
protected:
    DemoMode mode;
    int frame_num, training_num;
    std::array<SignalProcessor, kSensors> processors;
};

#endif
