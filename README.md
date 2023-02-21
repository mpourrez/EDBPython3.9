# EdgeDependabilityBenchmark

After making changes in the proto file (protos/unary.proto), execute the following code to generate the stubs:


``cd protos``

``python -m grpc_tools.protoc --proto_path=. ./object_tracking.proto --python_out=. --grpc_python_out=.
``