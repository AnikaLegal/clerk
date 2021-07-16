#!/bin/bash
# Push develop to master
set -e
git fetch
git checkout develop
git push
git fetch
git checkout master
git rebase origin/develop
git push
git checkout develop
