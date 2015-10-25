#pragma once

#ifndef OPTION_H
#define OPTION_H

#include <memory>
#include <utility>

template <class T> class Option {
protected:
    bool success;
    union {
        T t;
    };
public:
    Option(): success(false) {;}
    Option(T& t): success(true), t(T(t)) {;}
    Option(T&& t): success(true), t(T(std::move(t))) {;}

    Option(Option<T>&& rhs): success(rhs.success), t(T(std::move(t))) {;}

    ~Option() { if (success) t.~T(); }

    bool Empty() { return !success; }
    T Unwrap() {
        assert(success);
        return std::move(t);
    }
};

// Woo template inheritance is hard so all the stuff's copied here
template <class T> class CopyableOption: public Option<T> {
protected:
    bool success;
    union {
        T t;
    };
public:
    CopyableOption(): success(false) {;}
    CopyableOption(const T& t): success(true), t(T(t)) {;}

    CopyableOption(const CopyableOption<T>& rhs): 
            success(rhs.Option<T>::success), t(T(t)) {;}

    CopyableOption<T>& operator=(const CopyableOption<T>& rhs) {
        this->success = rhs.success;
        if (this->success) { this->t = rhs.t; }
        return *this;
    }

    ~CopyableOption() { if (success) t.~T(); }

    bool Empty() { return !success; }
    T Unwrap() {
        assert(success);
        return std::move(t);
    }

};

#endif
