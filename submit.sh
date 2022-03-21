#!/bin/bash

set -e

git tag -am "submission-$1" submission-$1
git push origin master
git push origin submission-$1

