# EdgeDependabilityBenchmark

## Getting Started

We use Anaconda to install dependencies for this project. Anaconda route is recommended for people using a GPU as it configures CUDA toolkit version.


### Installing Anaconda on Ubuntu
First update system repositories:
```bash
sudo apt update
```

Then we will download the “curl” utility as it permits fetching the installation script of Anaconda:
```bash
sudo apt install curl -y
```

Then, we prepare anaconda installer using the following commands:

```bash
cd /tmp
curl --output anaconda.sh https://repo.anaconda.com/archive/Anaconda3-5.3.1-Linux-x86_64.sh
sha256sum anaconda.sh
```

Finally, we install Anaconda and activate the environment settings:

```bash
bash anaconda.sh

source ~/.bashrc
```

### Running the Benchmark

For running the benchmark which is based on stress tests on the edge device, you need to install stress package using the following commands:
```bash
sudo apt-get install stress
```

Then after cloning the git repository, use the following commands to install all dependencies: 

For CPU tests:
```bash
# Tensorflow CPU
conda env create -f conda-cpu.yml
conda activate tracking-yolov4-cpu
```
For GPU tests:
```bash
# Tensorflow GPU
conda env create -f conda-gpu.yml
conda activate tracking-yolov4-gpu
```

Then you need to make changes to the 'configs.py' file to set the information regarding your edge device.
These information may include: EDGE_DEVICE_NAME and EDGE_DEVICE_IP.
   
Then run the server on your edge device by using the following line:

```bash
python edge_device.py
```

On your laptop (or benchmark orchestrator machine) run the following command:

```bash
python benchmark_orchestrator.py
```

## Making Changes in the Benchmark

After making changes in the proto file (protos/benchmark.proto), execute the following code to generate the stubs:


```bash
cd protos
python -m grpc_tools.protoc --proto_path=. ./benchmark.proto --python_out=. --grpc_python_out=.
```

## Applications

### 1- Object Tracking

For this application, we are using the "yolov4-deepsort" github repository which includes object tracking for both CPU and GPU.

[yolov4-deepsort](https://github.com/theAIGuysCode/yolov4-deepsort)


### 2- Object Detection

For this application, we are using the "yolov3" github repository which includes object tracking for both CPU and GPU.

[yolov3](https://github.com/theAIGuysCode/Object-Detection-API)