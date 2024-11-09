#!/bin/bash

grep -v '^#' .env | awk '{print "--test_env "$0}' | tr '\n' ' ' | sed 's/ $//'