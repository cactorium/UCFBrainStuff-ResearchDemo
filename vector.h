#pragma once

#ifndef VECTOR_H
#define VECTOR_H

#include <algorithm>
#include <vector>

#include <cmath>

template <typename T> class ShiftableVector {
public:
    ShiftableVector() : ShiftableVector<T>(0) {;}
    ShiftableVector(size_t sz) : ShiftableVector<T>(0, T()) {;}
    ShiftableVector(size_t sz, const T& val) : data(sz), shift(0) {
        std::for_each(data.begin(), data.end(), [&](T& a) {
            a = val;
        });
    }

    size_t Size() {
        return data.size();
    }

    ShiftableVector<T> Clone() {
        auto ret = ShiftableVector<T>(data.size());
        for (auto i = data.begin(); i != data.end(); i++) {
            ret.data[i - data.begin()] = *i;
        }
        ret.shift = shift;
        return ret;
    }
    T& operator[](size_t i) { return Idx(i); }
    T& Idx(size_t i) {
        return data[(i + data.size() + shift) % data.size()];
    }
    void Append(T val) {
        if (shift == 0) {
            data.push_back(val);
        } else {
            data.push_back(T());
            for (auto i = shift; i < data.size() - 1; i++) {
                data[i + 1] = data[i];
            }
            data[shift] = val;
        }
    }
    void Clear() {
        data.clear();
        shift = 0;
    }
    void Shift(size_t amount) {
        shift = (shift + data.size() + amount) % data.size();
    }
    void SetShift(size_t amount) {
        shift = (data.size() + amount) % data.size();
    }
    void Normalize() {
        const T norm = std::sqrt(Dot(*this));
        std::for_each(data.begin(), data.end(), [&](T &t) {
            t = t / norm;
        });
    }
    // FIXME: add consts as necessary to improve safety
    T Dot(ShiftableVector<T>& rhs) {
        auto ret = T();
        for (auto i = 0u; i < data.size() && i < rhs.data.size(); i++) {
            ret += ((*this)[i]) * (rhs[i]);
        }
        return ret;
    }
    template <typename Arg, typename F> auto Fold(F f, Arg arg) -> decltype(f(std::declval<Arg>(), std::declval<T>())) {
        auto a = arg;
        for (auto i = 0u; i < data.size(); i++) {
            a = f(a, data[i]);
        }
        return a;
    }

    // TODO: make iterator class
protected:
    std::vector<T> data;
    size_t shift;
private:
};

typedef ShiftableVector<float> FloatVector;

inline static void test_fold() {
    auto a = FloatVector(3, 1.0f);
    a.Fold([](float a, float b) -> float {
        return a + b;
    }, 0.0f); //T());
}

#endif
