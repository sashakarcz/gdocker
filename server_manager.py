# pylint: disable=E1101

"""
Server manager module for managing Docker services via gRPC.
"""

import difflib
from concurrent import futures
import docker
import grpc
import service_manager_pb2
import service_manager_pb2_grpc


class ServiceManager(service_manager_pb2_grpc.ServiceManagerServicer):
    """
    gRPC ServiceManager class to manage Docker services.
    """

    def __init__(self):
        """
        Initializes the ServiceManager with a Docker client.
        """
        self.client = docker.from_env()

    def restart_service(self, request, context):
        """
        Restarts Docker containers based on the provided service name.

        Args:
            request: The gRPC request containing the service name.
            context: The gRPC context.

        Returns:
            A ServiceResponse message indicating the result of the restart operation.
        """
        service_name = request.service_name
        try:
            container_list = self.client.containers.list(all=True)
            matching_containers = [
                container for container in container_list if
                container.name.startswith(service_name)
            ]

            if not matching_containers:
                return service_manager_pb2.ServiceResponse(
                    status=f"No containers found for service '{service_name}'."
                )

            for container in matching_containers:
                container.restart()

            return service_manager_pb2.ServiceResponse(
                status=f"Service '{service_name}' restarted successfully."
            )
        except docker.errors.DockerException as error:
            return service_manager_pb2.ServiceResponse(
                status=f"Error restarting service: {str(error)}"
            )

    def stop_service(self, request, context):
        """
        Stops Docker containers based on the provided service name.

        Args:
            request: The gRPC request containing the service name.
            context: The gRPC context.

        Returns:
            A ServiceResponse message indicating the result of the stop operation.
        """
        service_name = request.service_name
        try:
            container_list = self.client.containers.list(all=True)
            matching_containers = [
                container for container in container_list if container.name.startswith(service_name)
            ]

            if not matching_containers:
                return service_manager_pb2.ServiceResponse(
                    status=f"No containers found for service '{service_name}'."
                )

            for container in matching_containers:
                container.stop()

            return service_manager_pb2.ServiceResponse(
                status=f"Service '{service_name}' stopped successfully."
            )
        except docker.errors.DockerException as error:
            return service_manager_pb2.ServiceResponse(
                status=f"Error stopping service: {str(error)}"
            )

    def start_service(self, request, context):
        """
        Starts Docker containers based on the provided service name.

        Args:
            request: The gRPC request containing the service name.
            context: The gRPC context.

        Returns:
            A ServiceResponse message indicating the result of the start operation.
        """
        service_name = request.service_name
        try:
            container_list = self.client.containers.list(all=True)
            matching_containers = [
                container for container in container_list if container.name.startswith(service_name)
            ]

            if not matching_containers:
                return service_manager_pb2.ServiceResponse(
                    status=f"No containers found for service '{service_name}'."
                )

            for container in matching_containers:
                container.start()

            return service_manager_pb2.ServiceResponse(
                status=f"Service '{service_name}' started successfully."
            )
        except docker.errors.DockerException as error:
            return service_manager_pb2.ServiceResponse(
                status=f"Error starting service: {str(error)}"
            )

    def status_service(self, request, context):
        """
        Gets the status of Docker containers based on the provided service name.

        Args:
            request: The gRPC request containing the service name.
            context: The gRPC context.

        Returns:
            A StatusResponse message containing the list of container statuses.
        """
        service_name = request.service_name
        try:
            container_list = self.client.containers.list(all=True)
            matching_containers = [
                container for container in container_list if container.name.startswith(service_name)
            ]

            if not matching_containers:
                return service_manager_pb2.StatusResponse(
                    statuses=[f"No containers found for service '{service_name}'."]
                )

            statuses = [
                f"Container '{container.name}' is {container.status}" for
                container in matching_containers
            ]

            return service_manager_pb2.StatusResponse(
                statuses=statuses
            )
        except docker.errors.DockerException as error:
            return service_manager_pb2.StatusResponse(
                statuses=[f"Error retrieving status: {str(error)}"]
            )

    def logs_service(self, request, context):
        """
        Gets the logs of Docker containers based on the provided service name.

        Args:
            request: The gRPC request containing the service name and follow flag.
            context: The gRPC context.

        Returns:
            A LogsResponse message containing the logs of the containers.
        """
        service_name = request.service_name
        try:
            container_list = self.client.containers.list(all=True)
            matching_containers = [
                container for container in container_list if container.name.startswith(service_name)
            ]

            if not matching_containers:
                return service_manager_pb2.LogsResponse(
                    logs=[f"No containers found for service '{service_name}'."]
                )

            logs = []
            for container in matching_containers:
                log_output = container.logs().decode('utf-8')
                logs.append(f"Logs for container '{container.name}':\n{log_output}")

            return service_manager_pb2.LogsResponse(
                logs=logs
            )
        except docker.errors.DockerException as error:
            return service_manager_pb2.LogsResponse(
                logs=[f"Error retrieving logs: {str(error)}"]
            )

    def search_service(self, request, context):
        """
        Searches for Docker services by name.

        Args:
            request: The gRPC request containing the search term.
            context: The gRPC context.

        Returns:
            A SearchResponse message containing the list of matching container names.
        """
        search_term = request.search_term
        try:
            container_list = self.client.containers.list(all=True)
            container_names = [container.name for container in container_list]

            # Find all matches with the search term
            matches = difflib.get_close_matches(
                search_term, container_names, n=5, cutoff=0.1
            )

            return service_manager_pb2.SearchResponse(container_names=matches)
        except docker.errors.DockerException:
            return service_manager_pb2.SearchResponse(container_names=[])

    def _get_closest_container(self, service_name):
        """
        Helper method to find the closest matching container by name.

        Args:
            service_name: The name of the service to find.

        Returns:
            The closest matching Docker container, or None if no match is found.
        """
        try:
            container_list = self.client.containers.list(all=True)
            container_names = [container.name for container in container_list]
            matches = difflib.get_close_matches(service_name, container_names, n=1, cutoff=0.6)

            if matches:
                return self.client.containers.get(matches[0])
            return None
        except docker.errors.DockerException as error:
            print(f"Error retrieving container: {str(error)}")
            return None

def serve():
    """
    Starts the gRPC server and listens for incoming requests.
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_manager_pb2_grpc.add_ServiceManagerServicer_to_server(ServiceManager(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
