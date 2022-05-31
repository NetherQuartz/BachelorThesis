FROM python:3.7.12-slim

ENV aptDeps="wget unzip" \
    pipDeps="poetry gdown" \
    driveID="1L03nroUBlX7Q8K286eKapo8kk0Nmuiia"

WORKDIR /ctc

RUN apt-get update && \
    apt-get install -y --no-install-recommends ${aptDeps} && \
    ln -snf /usr/share/zoneinfo/Europe/Moscow /etc/localtime && echo Europe/Moscow > /etc/timezone && \
    pip install ${pipDeps} && \
    gdown --id ${driveID} -O model_cache.zip && \
    unzip model_cache.zip -d model_cache && \
    rm model_cache.zip

COPY pyproject.toml poetry.lock /ctc/

RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi && \
    pip install torch==1.4.0+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html && \
    python -m pip uninstall -y ${pipDeps} && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives /tmp/* /var/tmp/* /root/.cache/pip/*
    
RUN apt-get remove -y ${aptDeps} && \
    apt-get autoremove -y && \
    apt-get clean

COPY .streamlit /ctc/.streamlit
COPY demo /ctc/demo

EXPOSE 8501

CMD streamlit run /ctc/demo/demo.py --server.port 8501
