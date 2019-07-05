#pragma once

#include <vector>
#include <string>

template <typename T>
class sequence: public std::vector<T> {
};

using integer = int32_t;
