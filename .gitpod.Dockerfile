# Dockerfile sourced from:
# Base image from https://hub.docker.com/r/amancevice/pandas

FROM amancevice/pandas

# ADDITIONAL PYTHON PACKAGES
#   * requests: an elegant and simple HTTP library for Python, built for human beings
ENV PYTHON_PACKAGES="\
    requests \
" 

RUN apk add --no-cache --virtual build-dependencies python --update py-pip \
    && pip install --upgrade pip \
    && pip install --no-cache-dir $PYTHON_PACKAGES \
    && apk add --no-cache --virtual build-dependencies $PACKAGES \
    && rm -rf /var/cache/apk/*

CMD ["python"]
