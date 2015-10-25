#include "processor.h"

int getValueBySensorId(const SensorPosition &p, const Emotiv::Frame &f) {
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

short getQualityBySensorId(const SensorPosition &p, const Emotiv::Frame &f) {
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


