# Build llama.cpp (server only)
FROM debian:bookworm AS build
RUN apt-get update && apt-get install -y --no-install-recommends \
    git cmake build-essential ca-certificates curl libcurl4-openssl-dev && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /src
RUN git clone --depth 1 https://github.com/ggml-org/llama.cpp .
RUN cmake -S . -B build -DCMAKE_BUILD_TYPE=Release \
    -DLLAMA_BUILD_SERVER=ON -DLLAMA_BUILD_EXAMPLES=OFF
RUN cmake --build build -j"$(nproc)"

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl libcurl4 libgomp1 && \
    rm -rf /var/lib/apt/lists/*
COPY --from=build /src/build/bin /app/bin
ENV PATH=/app/bin:$PATH \
    LD_LIBRARY_PATH=/app/bin
ENTRYPOINT ["llama-server"]