#!/bin/bash

BASE_PATH="$(git rev-parse --show-toplevel)"

ln -s $BASE_PATH/utils/pre-commit.sh $BASE_PATH/.git/hooks/pre-commit
ln -s $BASE_PATH/utils/pre-push.sh $BASE_PATH/.git/hooks/pre-push
