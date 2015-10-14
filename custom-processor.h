#pragma once

#ifndef CUSTOM_PROCESSOR_H
#define CUSTOM_PROCESSOR_H 

#include "processor.h"
#include "vector.h"

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
    std::vector<FloatVector> training_data;
    std::vector<float> data_quality;
    // std::vector<float> tmp;
    FloatVector tmp;

    // used for processing mode
    FloatVector templ;
    FloatVector last;
    FloatVector last_quality;
    int last_corr;
    float confidence;
    FloatVector foo;
};

class CustomProcessor: public EmotivProcessor {
public:
    CustomProcessor();
    virtual ~CustomProcessor() {;}

    void ProcessFrame(const Emotiv::Frame &f, bool isSyncFrame);
    SignalResult GetProcessingResult() const;

    void SetMode(DemoMode m);
    DemoMode Mode() const {return mode;}
protected:
    int frame_num, training_num;
    std::array<SignalProcessor, kSensors> processors;
    DemoMode m;
};

#endif
