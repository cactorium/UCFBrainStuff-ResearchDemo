#!/usr/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
protoc -I=$DIR --python_out=$DIR $DIR/seniordesign.proto
