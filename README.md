# DeepEdgeBench: Benchmarking Dependability of Edge Applications and Devices

## What is DeepEdgeBench?

[DeepEdgeBench](https://github.com/mpourrez/EDB) is a novel benchmark tool to evaluate the performance of edge applications under various resource stress on edge devices. The aim is to understand which resource-stressing faults have the most disruptive impact on each category of edge computing applications. 

DeepEdgeBench contains 14 different edge applications performing micro- and application-level benchmarking on edge devices. Micro-benchmark workloads are to measure the performance of a specific resource type on the devices, e.g., CPU, memory, network bandwidth, and disk I/O. Application-level benchmark workloads are developed based on real-world edge computing use-cases. In particular, various machine learning and AI applications, e.g., [image classification](https://en.wikipedia.org/wiki/Computer_vision#Recognition), and [object detection](https://en.wikipedia.org/wiki/Object_detection), are developed for DeepEdgeBench.

## Getting Started
To get started, install the proper dependencies via Anaconda.

### Conda (Recommended)

```bash
# Tensorflow CPU
conda create --name benchmarkPython39 python=3.9    
conda activate benchmarkPython39
pip install grpcio google numpy scipy psutil Pillow nltk textblob pocketsphinx
pip install --upgrade protobuf
sudo apt-get install libxml2-dev
sudo apt-get install libxslt-dev
pip install lxml
cd aeneas
pip install -r requirements.txt
python setup.py install
cd darknet
make



# Tensorflow GPU
conda env create -f conda-gpu.yml
conda activate benchmark-gpu
```
# EDBPython3.9
