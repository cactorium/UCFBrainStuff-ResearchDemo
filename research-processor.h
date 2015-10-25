#pragma once

#ifndef RESEARCH_PROCESSOR_H
#define RESEARCH_PROCESSOR_H

#include <list>

#include "echo-buffer.h"
#include "processor.h"
#include "vector.h"
// http://iopscience.iop.org/article/10.1088/1741-2560/8/2/025015/pdf

class ResearchTrainingTemplate {
public:
    ResearchTrainingTemplate(const std::vector<float>& vf);

    float operator()(int cycle);
private:
    std::vector<float> templ;
};

struct SensorData {
    std::array<float, kSensors> data;
    bool isSyncFrame;
};

class ResearchProcessor: public EmotivProcessor {
public:
    ResearchProcessor();
    virtual ~ResearchProcessor() {;}

    void ProcessFrame(const Emotiv::Frame &f, bool isSyncFrame);
    SignalResult GetProcessingResult();

    void SetMode(DemoMode m);
    DemoMode Mode() const {return mode;}

protected:
    std::unique_ptr<ResearchTrainingTemplate> maybeTemplate;
    std::unique_ptr<SensorPosition> chosenChannel;
    EchoBuffer<SensorData> lastData;
    int framesAfterSync;
    std::list<int> syncFrames;
};

#endif
