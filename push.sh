#!/bin/bash

set -e

git add .
git commit -m $(date +%Y-%m-%d-%H%M)
git push origin master

