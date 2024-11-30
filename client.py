"""
Client for ServiceManager gRPC service.
"""

import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=UserWarning, module='google.protobuf')
    import argparse
    import grpc
    from grpc._channel import _InactiveRpcError
    import yaml
    import service_manager_pb2
    import service_manager_pb2_grpc

# pylint: disable=E1101

def manage_service(current_host, service_name, action):
    """
    Manage a Docker service (start, stop, restart, status) on the given host.

    Args:
        current_host (str): The host IP or hostname.
        service_name (str): The name of the service to manage.
        action (str): The action to perform (start, stop, restart, status).
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
            elif action == 'status':
                request = service_manager_pb2.ServiceRequest(service_name=service_name)
                response = stub.status_service(request)

            if response and hasattr(response, 'status') and response.status:
                print(f"{action.capitalize()} response: {response.status}")
            elif response and hasattr(response, 'statuses') and response.statuses:
                print(f"{action.capitalize()} response: {', '.join(response.statuses)}")
    except _InactiveRpcError:
        pass  # Suppress connection errors

def search_service(current_host, search_term):
    """
    Search for Docker services by name on the given host.

    Args:
        current_host (str): The host IP or hostname.
        search_term (str): The search term for the service.
    """
    try:
        with grpc.insecure_channel(f"{current_host}:50051") as channel:
            stub = service_manager_pb2_grpc.ServiceManagerStub(channel)
            request = service_manager_pb2.SearchRequest(search_term=search_term)
            response = stub.search_service(request)
            if response.container_names:
                print(f"[{current_host}] Found matching containers: {', '
                      .join(response.container_names)}")
    except _InactiveRpcError:
        pass  # Suppress connection errors

def logs_service(current_host, service_name):
    """
    Get logs of Docker containers based on the provided service name.

    Args:
        current_host (str): The host IP or hostname.
        service_name (str): The name of the service to get logs for.
    """
    try:
        with grpc.insecure_channel(f"{current_host}:50051") as channel:
            stub = service_manager_pb2_grpc.ServiceManagerStub(channel)
            request = service_manager_pb2.LogsRequest(service_name=service_name, follow=False)
            response = stub.logs_service(request)
            if response.logs:
                for log in response.logs:
                    print(f"[{current_host}] {log}")
    except _InactiveRpcError:
        pass  # Suppress connection errors

def main():
    """
    Main function to parse arguments and execute the appropriate command.
    """
    parser = argparse.ArgumentParser(description='Client for ServiceManager gRPC service.')
    parser.add_argument('--config', type=str,
                        required=True,
                        help='Path to the hosts configuration file.')
    parser.add_argument(
        'command', choices=['restart', 'start', 'stop', 'search', 'status', 'logs'],
        help='Command to execute.'
    )
    parser.add_argument('service_name', type=str, help='Name of the service or search term.')

    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    for host in config['docker_hosts']:
        if args.command == 'search':
            search_service(host, args.service_name)
        elif args.command == 'logs':
            logs_service(host, args.service_name)
        else:
            manage_service(host, args.service_name, args.command)

if __name__ == '__main__':
    main()

