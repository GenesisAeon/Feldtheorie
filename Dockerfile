FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN python -m pip install --upgrade pip \
 && pip install numpy pandas scipy matplotlib xarray dask fsspec zarr

ENV RG_SIM_ENTRYPOINT="scripts.stubs.rg_sim_stub:simulate"

CMD ["bash", "-lc", "make reproduce && ls -lh analysis/results && echo 'Done'"]
