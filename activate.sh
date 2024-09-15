#!/bin/bash

get_git_branch() {
  if git rev-parse --is-inside-work-tree &> /dev/null; then
    git branch --show-current
  fi
}

export AUTOPROJ_PY=1

export PATH_OLD=$PATH
export PATH=$PATH:~/caio_ws/autoproj-py/dist/bin

export PYTHONUSERBASE_OLD=$PYTHONUSERBASE
export PYTHONUSERBASE=~/caio_ws/autoproj-py/dist

export PS1_OLD=$PS1
export PS1="\[\e[32m\][autoproj-py]\[\e[0m\] $PS1"

echo "autoproj-py environment configured"
