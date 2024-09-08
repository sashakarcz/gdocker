FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install necessary build tools and dependencies
RUN apt-get update && apt-get install -y \
    protobuf-compiler \
    python3-pip \
    gcc \
    python3-dev \
    libprotobuf-dev

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the proto file
COPY service_manager.proto .

# Generate the gRPC Python code from the proto file
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. service_manager.proto

# Copy the rest of the application code
COPY . .

# Expose the gRPC port
EXPOSE 50051

# Run the gRPC server
CMD ["python", "server_manager.py"]

