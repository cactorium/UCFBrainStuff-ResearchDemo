#pragma once

#ifndef OPTION_H
#define OPTION_H

#include <memory>
#include <utility>

template <class T> class Option {
private:
    bool success;
    T* t;
public:
    Option(): success(false), t(nullptr) {;}
    Option(T& t): success(true), t(new T(t)) {;}
    Option(T&& t): success(true), t(new T(std::move(t))) {;}
    ~Option() { if (t != nullptr) delete t; }

    bool Empty() { return !success; }
    T Unwrap() {
        assert(success);
        return std::move(*t);
    }
};

#endif
