#!/bin/bash

BASE_PATH="$(git rev-parse --show-toplevel)"

ln -sf $BASE_PATH/utils/git/pre-commit.sh $BASE_PATH/.git/hooks/pre-commit
ln -sf $BASE_PATH/utils/git/pre-push.sh $BASE_PATH/.git/hooks/pre-push

chmod +x $BASE_PATH/.git/hooks/pre-push
chmod +x $BASE_PATH/.git/hooks/pre-commit