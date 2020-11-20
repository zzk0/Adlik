#!/usr/bin/env bash

if [[ ${CUDA_VERSION} = '10.0' ]]; then
  apt-get update && \
  apt-get install --no-install-recommends -y cuda-nvrtc-10-0
elif [[ ${CUDA_VERSION} = '10.2' ]]; then
  apt-get update && \
  apt-get install --no-install-recommends -y cuda-nvrtc-10-2
elif [[ ${CUDA_VERSION} = '11.0' ]]; then
  apt-get update && \
  apt-get install --no-install-recommends -y cuda-nvrtc-11-0
fi

apt-get update && \
apt-get install --no-install-recommends -y \
    libnvinfer7=${TENSORRT_VERSION}-1+cuda${CUDA_VERSION} \
    libnvinfer-dev=${TENSORRT_VERSION}-1+cuda${CUDA_VERSION} \
    libnvinfer-plugin7=${TENSORRT_VERSION}-1+cuda${CUDA_VERSION} \
    libnvparsers7=${TENSORRT_VERSION}-1+cuda${CUDA_VERSION} \
    libnvonnxparsers7=${TENSORRT_VERSION}-1+cuda${CUDA_VERSION} \
    libnvonnxparsers-dev=${TENSORRT_VERSION}-1+cuda${CUDA_VERSION} \
    python3-libnvinfer=${TENSORRT_VERSION}-1+cuda${CUDA_VERSION}

if [[ ${TENSORRT_VERSION} = 7.0.* ]] ; then
  apt-get install --no-install-recommends -y \
    libcudnn7=*+cuda${CUDA_VERSION} \
    libcudnn7-dev=*+cuda${CUDA_VERSION}
  apt-mark hold libcudnn7 libcudnn7-dev libnvinfer7 libnvinfer-dev libnvonnxparsers7 libnvonnxparsers-dev
elif [[ ${TENSORRT_VERSION} = 7.1.* ]] || [[ ${TENSORRT_VERSION} = 7.2.* ]] ; then
  if [[ ${CUDA_VERSION} = '10.2' ]]; then
    apt-get autoremove --purge -y libcudnn8 \
      libcudnn8-dev
  fi
  apt-get install --no-install-recommends -y \
    libcudnn8=*+cuda${CUDA_VERSION} \
    libcudnn8-dev=*+cuda${CUDA_VERSION}
  apt-mark hold libcudnn8 libcudnn8-dev libnvinfer7 libnvinfer-dev libnvonnxparsers7 libnvonnxparsers-dev
else
  echo "Not support this CUDA version and TensorRT version"
fi