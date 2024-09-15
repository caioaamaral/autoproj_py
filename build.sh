if [ -z "$AUTOPROJ_PY" ]; then
  echo "Please run activate.sh first"
  return 1
fi

pip install --upgrade --user wheel build
python3 -m build