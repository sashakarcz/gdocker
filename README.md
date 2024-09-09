# Docker gRPC Service Manager
[![Publish Docker image](https://github.com/sashakarcz/gdocker/actions/workflows/docker-image.yml/badge.svg)](https://github.com/sashakarcz/gdocker/actions/workflows/docker-image.yml) [![pylint Passing](https://github.com/sashakarcz/gdocker/actions/workflows/pylint.yml/badge.svg)](https://github.com/sashakarcz/gdocker/actions/workflows/pylint.yml)


A Python-based gRPC service for managing Docker containers across multiple hosts. This project allows users to **search**, **start**, **stop**, and **restart** Docker containers running on different Docker hosts. It uses a client-server architecture, where the server exposes gRPC endpoints for managing Docker containers and the client interacts with these endpoints.

## Features

- **Search Docker Containers**: Search for Docker containers on a specific host by providing a partial or complete container name.
- **Start Docker Containers**: Start a stopped Docker container by name.
- **Stop Docker Containers**: Stop a running Docker container by name.
- **Restart Docker Containers**: Restart a running Docker container by name.
- **Fuzzy Matching**: Supports fuzzy matching to find containers even if the exact name is not known.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Server](#server)
  - [Client](#client)
- [Command-line Options](#command-line-options)
- [Configuration](#configuration)
- [gRPC Service API](#grpc-service-api)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

- Python 3.8+
- Docker
- Docker SDK for Python
- gRPC and Protocol Buffers (`grpcio`, `grpcio-tools`)
- YAML support via `PyYAML`

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/docker-grpc-service-manager.git
cd docker-grpc-service-manager
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Generate gRPC Files

Generate the gRPC code from the `.proto` file by running:

```bash
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. service_manager.proto
```

## Usage

## Server

The gRPC server runs on each Docker host and provides endpoints to manage Docker containers.

### Run the gRPC Server

To start the gRPC server on a Docker host, first build the Docker image and then run it:

```bash
docker build -t grpc-service-manager .
docker run -d -p 50051:50051 -v /var/run/docker.sock:/var/run/docker.sock --name grpc_service_manager grpc-service-manager
```

Or, use `docker compose`:

```bash
docker compose up -d
```

This starts the gRPC service on port `50051` and mounts the Docker socket to allow interaction with Docker.

## Client

The client interacts with the gRPC server to perform various operations on Docker containers.

### Running the Client

To use the client, run it locally or from a different machine that has access to the Docker hosts.

Example to search for a container:

```bash
python3 client.py search homeassistant
```

Example to start a container:

```bash
python3 client.py start plex
```

### Command-line Options

The client supports multiple actions (`start`, `stop`, `restart`, `search`) and takes the service name (or search term) as an argument. It also supports an optional `--config` argument to specify the path to the hosts configuration file.

#### Available Commands

- `start`:  Start a Docker container by name.
- `stop`:  Stop a Docker container by name.
- `restart`:  Restart a Docker container by name.
- `search`: Search for a Docker container by name or partial name.

#### Useage

```bash
python3 client.py <action> <service_name> [--config path/to/hosts.yaml]
```

- `action`: The action to perform. Choices are: `start`, `stop`, `restart`, `search`
- `service_name`: The name of the Docker service (or search term for `search` action).
- `--config`: Path to the the YAML configuration file that lists the Docker hosts. Default is `./hosts.yaml`

## Configuration

The hosts are defined in a YAML file (`hosts.yaml`). This file contains a list of Docker hosts that the client will interact with.

Example `hosts.yaml`:

```yaml
docker_hosts:
  - 192.168.1.100
  - 192.168.1.101
  - 192.168.1.102
  - 192.168.1.103
```

## gRPC Service API

### Proto File Definition

The gRPC service is defined in [service_manager.proto](service_manager.proto)

### Available RPC Methods

- `restart_service`: Restarts a container by name.
- `start_service`: Starts a container by name.
- `stop_service`: Stops a container by name.
- `search_service`: Searches for containers by name or partial name.

## Deployment

The whole deployment can be built and run via `docker compose`:

```bash
docker compose up -d
```

Or manually via Docker:

### 1. Build the Docker image

```bash
docker build -t grpc-service-manager .
```

### 2. Run the Server

```bash
docker run -d -p 50051:50051 -v /var/run/docker.sock:/var/run/docker.sock --name grpc_service_manager grpc-service-manager
```

This mounts the Docker socket and exposes the gRPC server on port `50051`.

## Client Deployment

Simply run the Python client on any machine that can reach the gRPC servers running on Docker hosts. Ensure Python dependencies are installed, and the `hosts.yaml` file is set up correctly.

## Contributing

We welcome contributions to improve the project! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit and push (`git push origin feature-branch`).
5. Open a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](license) file for details.
