#include <algorithm>
#include <cmath>
#include <iostream>

#include "custom-processor.h"
#include "processor.h"

/*
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
*/

CustomProcessor::CustomProcessor(): frame_num(0), training_num(0) {
    for (auto s : kSensorOrder) {
        auto idx = static_cast<int>(s);
        processors[idx] = SignalProcessor(s);
    }
}

void CustomProcessor::ProcessFrame(const Emotiv::Frame &f, bool isSyncFrame) {
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

SignalResult CustomProcessor::GetProcessingResult() const {
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

void CustomProcessor::SetMode(DemoMode m) {
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
                // if (avg_quality > kQualityThreshold && tmp.size() > 0) {
                if (avg_quality > kQualityThreshold && tmp.Size() > 0) {
                    /*
                    auto new_data = Vectorf(tmp.size());
                    for (auto i = 0u; i < tmp.size(); i++) {
                        new_data[i] = tmp[i];
                    }
                    */

                    auto new_data = tmp.Clone();
                    training_data.push_back(new_data);
                    data_quality.push_back(avg_quality);
                }
                tmp.Clear();
                avg_quality = 0.0f;
            }
        }
        // tmp.push_back(getValueBySensorId(pos, f));
        tmp.Append(getValueBySensorId(pos, f));
        avg_quality = avg_quality*frame_num/(1+frame_num) +
            getQualityBySensorId(pos, f)/(1+frame_num);
    } else {
        /*
        for (auto i = 0u; i < last.size() - 1; i++) {
            last[i] = last[i + 1];
        }
        last[last.size()-1] = getValueBySensorId(pos, f);
        */
        last.Shift(1);
        last[-1] = getValueBySensorId(pos, f);
        /*
        for (auto i = 0u; i < last_quality.size() - 1; i++) {
            last_quality[i] = last_quality[i + 1];
        }
        last_quality[last_quality.size()-1] = getQualityBySensorId(pos, f);
        */
        last_quality.Shift(1);
        last_quality[-1] = getQualityBySensorId(pos, f);

        /*
        auto shifted_input = Vectorf(last.size());
        auto best = 0.0f;
        auto off = -1;
        auto idx = [=](int i, int offset) -> unsigned int {
            return static_cast<unsigned int>((i + offset + last.size()) % last.size());
        };
        for (auto i = 0u; i < shifted_input.size(); i++) {
            shifted_input[idx(i, frame_num)] = last[i];
        }
        normalize(shifted_input);
        auto shifted_dot = [=](const Vectorf &a, int shifta, const Vectorf &b) -> float {
            auto ret = 0.0f;
            for (auto i = 0u; i < a.size() && i < b.size(); i++) {
                ret += a[idx(i, shifta)] * b[i];
            }
            return ret;
        };
        */
        auto best = 0.0f;
        auto off = -1;
        auto shifted_input = last.Clone();
        shifted_input.Shift(frame_num);
        shifted_input.Normalize();

        // for (auto i = 0u; i < shifted_input.size(); i++) {
        for (auto i = 0u; i < shifted_input.Size(); i++) {
            // FIXME: Is this supposed to be +1 or -1?
            shifted_input.Shift(1);
            // auto corr = fabs(shifted_dot(shifted_input, i, templ));
            auto corr = fabs(shifted_input.Dot(templ));
            if (corr > best) {
                best = corr;
                off = static_cast<int>(i);
            }
        }

        if (best > kCorrThreshold) {
            last_corr = off;
        } else {
            // TODO: let the confidence decay, as the old values age
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
        // tmp.clear();
        tmp.Clear();
    } else {
        if (training_data.size() <= 0) {
            std::cerr << "WARNING: no new training data, keeping old values" << std::endl;
            return;
        }

        unsigned int trunc_size = 100000000u;
        for (auto &s: training_data) {
            // if (s.size() < trunc_size) {
            if (s.Size() < trunc_size) {
                // trunc_size = s.size();
                trunc_size = s.Size();
            }
        }

        // average and generate template
        // templ = Vectorf(trunc_size);
        templ = FloatVector(trunc_size);
        // for (auto i = 0u; i < templ.size(); i++) {
        for (auto i = 0u; i < templ.Size(); i++) {
            auto sum = 0.0f;
            for (auto s: training_data) {
                sum += static_cast<float>(s[i]);
            }
            templ[i] = sum/training_data.size();
        }

        auto qual_sum = std::accumulate(data_quality.begin(), data_quality.end(), 0.0f);

        // normalize(templ);
        // last = Vectorf(trunc_size);
        // last_quality = Vectorf(trunc_size);
        templ.Normalize();
        last = FloatVector(trunc_size, 0.0f);
        last_quality = FloatVector(trunc_size, 0.0f);

        // fill(last, 0.0f);
        // fill(last_quality, 0.0f);
        last_corr = -1;
        confidence = qual_sum/data_quality.size();
    }
}

