#!/usr/bin/bash

# woo this will break if it's called from a different

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
protoc -I=$DIR --python_out=$DIR --grpc_out=$DIR \
    --plugin=protoc-gen-grpc=`which grpc_python_plugin` $DIR/seniordesign.proto
