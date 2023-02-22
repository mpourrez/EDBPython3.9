# EdgeDependabilityBenchmark

## Getting Started

We use Anaconda to install dependencies for this project. Anaconda route is recommended for people using a GPU as it configures CUDA toolkit version.

```bash
# Tensorflow CPU
conda env create -f conda-cpu.yml
conda activate tracking-yolov4-cpu

# Tensorflow GPU
conda env create -f conda-gpu.yml
conda activate tracking-yolov4-gpu
```

## Making Changes

After making changes in the proto file (protos/unary.proto), execute the following code to generate the stubs:


```bash
cd protos
python -m grpc_tools.protoc --proto_path=. ./object_tracking.proto --python_out=. --grpc_python_out=.
```

## Applications

### 1- Object Tracking

For this application, we are using the "yolov4-deepsort" github repository which includes object tracking for both CPU and GPU.

[yolov4-deepsort](https://github.com/theAIGuysCode/yolov4-deepsort)


### 2- Object Detection