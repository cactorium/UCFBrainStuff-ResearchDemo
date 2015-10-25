#pragma once

#ifndef ECHO_BUFFER_H_
#define ECHO_BUFFER_H_

#include <vector>

template <typename T> class EchoBuffer {
public:
    EchoBuffer() : EchoBuffer(64) {;}
    EchoBuffer(size_t s) : data(s), lastPos(0), lenUsed(0) {;}

    T& operator[](size_t idx) {
        if (idx > lenUsed) {
            return T();
        } else {
            if (lastPos - idx < 0) {
                return data[data.size() + lastPos - idx];
            } else {
                return data[lastPos - idx];
            }
        }
    }
    void Clear() {
        lastPos = 0;
        lenUsed = 0;
    }
    void Push(T val) {
        ++lastPos;
        if (lastPos >= data.size()) { lastPos -= data.size(); }
        data[lastPos] = val;
        if (lenUsed < data.size()) { ++lenUsed; }
    }
    void Resize(size_t sz) {
        if (data.size() < sz) {
            // grow
            size_t oldSz = data.size();
            data.resize(sz);
            for (int i = 1; (oldSz - i) > lastPos; ++i) {
                data[data.size()-i] = data[oldSz-i];
            }
        } else {
            // shrink
            for (int i = data.size() - 1; i + sz - data.size() > lastPos; i--) {
                data[i + sz - data.size()] = data[i];
            }
            if (lenUsed > sz) {
                lenUsed = sz;
            }
            data.resize(sz);
        }
    }
    std::vector<T> &Data() {
        return data;
    }
protected:
    std::vector <T> data;
    size_t lastPos;
    size_t lenUsed;
};

#endif

