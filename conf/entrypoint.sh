#!/bin/bash

set -e

nginx
keystone-api "$@"
