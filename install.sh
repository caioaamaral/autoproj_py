if [ -z "$AUTOPROJ_PY" ]; then
  echo "Please run activate.sh first"
  return 1
fi

pip install --force-reinstall dist/autoproj_py-0.1.0-py3-none-any.whl
