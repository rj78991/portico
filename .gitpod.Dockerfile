# Dockerfile sourced from:
# Base image from https://hub.docker.com/r/amancevice/pandas

FROM amancevice/pandas

# ADDITIONAL PYTHON PACKAGES
#   * requests: an elegant and simple HTTP library for Python, built for human beings
ENV PYTHON_PACKAGES="\
    requests \
" 

RUN pip install --upgrade pip \
    && pip install --no-cache-dir $PYTHON_PACKAGES

CMD ["python"]
