#include "research-processor.h"

const int N = 20;

ResearchProcessor::ResearchProcessor() : framesAfterSync(0) {
    lastData.Resize(kTrainingSets * kApproximateTrainingSize);
    // TODO
}

void ResearchProcessor::ProcessFrame(const Emotiv::Frame &f, bool isSyncFrame) {
    auto values = std::array<float, kSensors>();
    for (size_t i = 0; i < values.size(); i++) {
        values[i] = getValueBySensorId(kSensorOrder[i], f);
    }
    lastData.Push(values);
    framesAfterSync++;
    if (isSyncFrame) {
        syncFrames.push(framesAfterSync);
        // FIXME: this grows indefinitely; resize after it gets longer than the buffer
        framesAfterSync = 0;
    }

    if (mode == PROCESSING) {
        // TODO: process data 
    }
}

SignalResult ResearchProcessor::GetProcessingResult() {
    // TODO
}

void ResearchProcessor::SetMode(DemoMode m) {
    if (m != mode) {
        if (m == TRAINING) {
            lastData.Resize(kTrainingSets * kApproximateTrainingSize);
        } else if (m == PROCESSING) {
            // TODO: process data
        }
    }
    mode = m;
    // TODO
}
