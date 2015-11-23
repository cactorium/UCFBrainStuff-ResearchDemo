#!/usr/bin/bash

# woo this will break if it's called from a different

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
protoc -I=$DIR --python_out=$DIR $DIR/seniordesign.proto
