
#!/bin/bash

# Check if running inside pipenv
if [ -z "$PIPENV_ACTIVE" ]; then
    exec pipenv run "$0" "$@"
fi
python -V

BASE_PATH="$(git rev-parse --show-toplevel)"
STAGED_CONFIG_FILES="$(git diff --cached --diff-filter=ACMR --oneline --name-only --relative -- 'setup.*')"

# checks if array contains a given element `array_contains [array] [element]`
array_contains () {
  local array="$1[@]"
  local seeking=$2
  local in=1
  for element in "${!array}"; do
      if [[ $element == "$seeking" ]]; then
          in=0
          break
      fi
  done
  return $in
}

if [ -n "$STAGED_CONFIG_FILES" ]; then
  echo "Changed config files, run tests/lint on all files"
  while read -r line; do
    STAGED_PY_FILES_ARRAY+=("${line:2}")
  done <<< "$(find . -path ./.git -prune -o -name '*.py' | grep -v .venv)"
  STAGED_PY_FILES="$BASE_PATH"
else
  while read -r line; do
    STAGED_PY_FILES_ARRAY+=("$line")
  done <<< "$(git diff --cached --diff-filter=ACMR --oneline --name-only -- '*.py')"
  STAGED_PY_FILES="$(git diff --cached --diff-filter=ACMR --oneline --name-only --relative -- '*.py')"
fi

FLAKE8=$(which flake8)
MYPY=$(which mypy)

function test_dependencies {
    if ! type "$FLAKE8" &> /dev/null; then
      printf "\033[41mPlease install Flake8 or make sure that it's in the PATH\033[0m\n"
      return 1
    fi
    if ! type "$MYPY" &> /dev/null; then
      printf "\033[41mPlease install mypy or make sure that it's in the PATH\033[0m\n"
      return 1
    fi

    return 0
}

# Lint check
function call_flake8 {
    if [ -z "$STAGED_PY_FILES" ]; then
        echo "No python files changed, nothing to lint with flake8"
        return 0
    fi

    echo "Linting Python files with Flake8 ($FLAKE8)"

    $FLAKE8 --config $BASE_PATH/setup.cfg $STAGED_PY_FILES
    FLAKE8_EXIT=$?

    if [[ "${FLAKE8_EXIT}" == 0 ]]; then
      printf "\033[42mFLAKE8 SUCCEEDED\033[0m\n"
    else
      printf "\033[41mFLAKE8 FAILED:\033[0m Fix flake8 errors and try again\n"
      return 1
    fi

    return 0
}


# Typing check
function call_mypy {
  MYPY_ERRORS=false
  if [ -z "$STAGED_PY_FILES" ]; then
      echo "No python files changed, nothing to lint with mypy"
      return 0
  fi

  echo "Type checking Python files with mypy ($MYPY)"

  IGNORE=$(awk -F "= " '/mypy_ignore_folder/ {print $2}' "$BASE_PATH"/setup.cfg)
  IGNORE=$(echo "^""$IGNORE" | sed -r "s/[,]+/|^/g")
  for PYFILE in "${STAGED_PY_FILES_ARRAY[@]}"; do
    if ! grep -Eowq "$IGNORE" <<< "${PYFILE//.\/}"; then
      MYPY_EXIT=$($MYPY --config-file "$BASE_PATH"/setup.cfg $PYFILE)

      if [[ $MYPY_EXIT != *"error"* ]]; then
        printf "\033[42mMYPY SUCCEEDED\033[0m for %s\n" "$PYFILE"
      else
        $MYPY --config-file $BASE_PATH/setup.cfg "$PYFILE"
        printf "\033[41mMYPY FOUND PROBLEMS\033[0m for %s$\n" "$PYFILE"
        MYPY_ERRORS=true
      fi

    else
      printf "%s \033[1mignored\033[0m\n" "$PYFILE"
    fi

  done

  if $MYPY_ERRORS; then
    printf "\e[31m\e[1mFix typing errors!\e[0m\n"
    return 1
  fi
  return 0
}

cd "$BASE_PATH" || exit

test_dependencies &&
call_mypy &&
call_flake8 &&
