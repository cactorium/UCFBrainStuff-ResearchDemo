#include <algorithm>
#include <cmath>
#include <iostream>

#include "processor.h"

static int getValueBySensorId(const SensorPosition &p, const Emotiv::Frame &f) {
    switch (p) {
        case F3: return f.F3;
        case FC6: return f.FC6;
        case P7: return f.P7;
        case T8: return f.T8;
        case F7: return f.F7;
        case F8: return f.F8;
        case T7: return f.T7;
        case P8: return f.P8;
        case AF4: return f.AF4;
        case F4: return f.F4;
        case AF3: return f.AF3;
        case O2: return f.O2;
        case O1: return f.O1;
        case FC5: return f.FC5;
        default:
            return 0;
    }
}

static short getQualityBySensorId(const SensorPosition &p, const Emotiv::Frame &f) {
    switch (p) {
        case F3: return f.cq.F3;
        case FC6: return f.cq.FC6;
        case P7: return f.cq.P7;
        case T8: return f.cq.T8;
        case F7: return f.cq.F7;
        case F8: return f.cq.F8;
        case T7: return f.cq.T7;
        case P8: return f.cq.P8;
        case AF4: return f.cq.AF4;
        case F4: return f.cq.F4;
        case AF3: return f.cq.AF3;
        case O2: return f.cq.O2;
        case O1: return f.cq.O1;
        case FC5: return f.cq.FC5;
        default:
            return 0;
    }
}

void normalize(Vectorf &v) {
    auto mag2 = 0.0f;
    std::for_each(v.begin(), v.end(), [&](float f) {
        mag2 += f*f;
    });
    auto mag = sqrtf(mag2);
    std::for_each(v.begin(), v.end(), [=](float& f) {
        f /= mag;
    });
}

void fill(Vectorf &v, float val) {
    std::for_each(v.begin(), v.end(), [=](float& f) {
        f = val;
    });
}

EmotivProcessor::EmotivProcessor(): mode(TRAINING), frame_num(0), training_num(0) {
    for (auto s : kSensorOrder) {
        auto idx = static_cast<int>(s);
        processors[idx] = SignalProcessor(s);
    }
}

void EmotivProcessor::ProcessFrame(const Emotiv::Frame &f, bool isSyncFrame) {
    std::cerr << "Got frame data for frame " << frame_num << std::endl;

    if (isSyncFrame) {
        frame_num = 0;
    }
    for (auto &p : processors) {
        p.ProcessFrame(frame_num, f, isSyncFrame);
    }
    frame_num++;

    if (std::count_if(processors.begin(), processors.end(),
                [](const SignalProcessor &p) -> bool {
                    return p.TrainingFinished();
                }) >= kSensors/3) {
        this -> SetMode(PROCESSING);
    }
}

SignalResult EmotivProcessor::GetProcessingResult() const {
    SignalResult best;
    best.confidence = 0.0f;

    for (auto &p: processors) {
        auto result = p.GetProcessingResult();
        if (result.confidence > best.confidence) {
            best = result;
        }
    }
    return best;
}

void EmotivProcessor::SetMode(DemoMode m) {
    if (m == TRAINING) {
        std::cerr << "training mode set to training" << std::endl;
    } else {
        std::cerr << "training mode set to processing" << std::endl;
    }

    for (auto s : kSensorOrder) {
        processors[static_cast<int>(s)].SetMode(m);
    }
}

SignalProcessor::SignalProcessor(SensorPosition pos): mode(TRAINING),
    pos(pos), first_sync(true), avg_quality(0.0f),
    last_corr(-1), confidence(0.0f) {;}

void SignalProcessor::ProcessFrame(int frame_num, const Emotiv::Frame &f,
        bool isSyncFrame) {
    if (mode == TRAINING) {
        if (isSyncFrame) {
            if (first_sync) {
                first_sync = false;
            } else {
                if (avg_quality > kQualityThreshold && tmp.size() > 0) {
                    auto new_data = Vectorf(tmp.size());
                    for (auto i = 0u; i < tmp.size(); i++) {
                        new_data[i] = tmp[i];
                    }
                    training_data.push_back(new_data);
                    data_quality.push_back(avg_quality);
                }
                tmp.clear();
                avg_quality = 0.0f;
            }
        }
        tmp.push_back(getValueBySensorId(pos, f));
        avg_quality = avg_quality*frame_num/(1+frame_num) +
            getQualityBySensorId(pos, f)/(1+frame_num);
    } else {
        for (auto i = 0u; i < last.size() - 1; i++) {
            last[i] = last[i + 1];
        }
        last[last.size()-1] = getValueBySensorId(pos, f);
        for (auto i = 0u; i < last_quality.size() - 1; i++) {
            last_quality[i] = last_quality[i + 1];
        }
        last_quality[last_quality.size()-1] = getQualityBySensorId(pos, f);

        auto shifted_templ = templ;
        auto best = -1e-30f;
        auto offset = -1;
        for (auto i = 0u; i < shifted_templ.size(); i++) {
            auto tmp = shifted_templ[0];
            for (auto j = 0u; j < shifted_templ.size() - 1; j++) {
                shifted_templ[j] = shifted_templ[j + 1];
            }
            // TODO
        }
    }
}

SignalResult SignalProcessor::GetProcessingResult() const {
    return SignalResult {
        last_corr, confidence
    };
}

bool SignalProcessor::TrainingFinished() const {
    return training_data.size() >= kTrainingSets;
}

void SignalProcessor::SetMode(DemoMode m) {
    mode = m;
    if (m == TRAINING) {
        first_sync = true;
        avg_quality = 0.0f;
        training_data.clear();
        data_quality.clear();
        tmp.clear();
    } else {
        if (training_data.size() <= 0) {
            std::cerr << "WARNING: no new training data, keeping old values" << std::endl;
            return;
        }

        unsigned int trunc_size = 100000000u;
        for (auto &s: training_data) {
            if (s.size() < trunc_size) {
                trunc_size = s.size();
            }
        }

        // average and generate template
        templ = Vectorf(trunc_size);
        for (auto i = 0u; i < templ.size(); i++) {
            auto sum = 0.0f;
            for (auto s: training_data) {
                sum += static_cast<float>(s[i]);
            }
            templ[i] = sum/training_data.size();
        }

        auto qual_sum = std::accumulate(data_quality.begin(), data_quality.end(), 0.0f);

        normalize(templ);
        last = Vectorf(trunc_size);
        last_quality = Vectorf(trunc_size);

        fill(last, 0.0f);
        fill(last_quality, 0.0f);
        last_corr = -1;
        confidence = qual_sum/data_quality.size();
    }
}

