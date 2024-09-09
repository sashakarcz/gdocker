#!/usr/bin/env python3

"""
Client to manage Docker services via gRPC.
"""

import argparse
import yaml
import grpc
import service_manager_pb2
import service_manager_pb2_grpc
from grpc._channel import _InactiveRpcError


def manage_service(current_host, service_name, action):
    """
    Manage a Docker service (start, stop, restart) on the given host.

    Args:
        current_host (str): The host IP or hostname.
        service_name (str): The name of the service to manage.
        action (str): The action to perform (start, stop, restart).
    """
    try:
        with grpc.insecure_channel(f"{current_host}:50051") as channel:
            stub = service_manager_pb2_grpc.ServiceManagerStub(channel)

            response = None
            if action == 'restart':
                request = service_manager_pb2.ServiceRequest(service_name=service_name)
                response = stub.restart_service(request)
            elif action == 'start':
                request = service_manager_pb2.ServiceRequest(service_name=service_name)
                response = stub.start_service(request)
            elif action == 'stop':
                request = service_manager_pb2.ServiceRequest(service_name=service_name)
                response = stub.stop_service(request)

            if response:
                print(f"[{current_host}] {response.status}")
    except _InactiveRpcError as error:
        print(f"[{current_host}] Failed to connect to gRPC server: {error.details()}")


def search_service(current_host, search_term):
    """
    Search for a Docker service by name on the given host.

    Args:
        current_host (str): The host IP or hostname.
        search_term (str): The term to search for in service names.
    """
    try:
        with grpc.insecure_channel(f"{current_host}:50051") as channel:
            stub = service_manager_pb2_grpc.ServiceManagerStub(channel)
            request = service_manager_pb2.SearchRequest(search_term=search_term)
            response = stub.search_service(request)

            if response.container_names:
                print(f"[{current_host}] Found matching containers: "
                      f"{', '.join(response.container_names)}")
            else:
                print(f"[{current_host}] No containers found matching '{search_term}'")
    except _InactiveRpcError as error:
        print(f"[{current_host}] Failed to connect to gRPC server: {error.details()}")


def load_hosts_from_config(file_path):
    """
    Load the list of hosts from the specified configuration file.

    Args:
        file_path (str): The path to the configuration file.

    Returns:
        list: The list of hosts.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
        return config['docker_hosts']


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description="Manage Docker services on specified hosts"
    )
    parser.add_argument(
        "action", choices=['start', 'stop', 'restart', 'search'],
        help="The action to perform"
    )
    parser.add_argument(
        "service_name", help="The name of the service to manage or search term"
    )
    parser.add_argument(
        "--config", default="/etc/gdocker/hosts.yaml",
        help="Path to the configuration file with the list of hosts "
             "(default: /etc/gdocker/hosts.yaml)"
    )

    args = parser.parse_args()

    # Load hosts from the configuration file
    hosts = load_hosts_from_config(args.config)

    for current_host in hosts:
        if args.action == 'search':
            search_service(current_host, args.service_name)
        else:
            manage_service(current_host, args.service_name, args.action)

