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
        Restarts a Docker service based on the provided service name.

        Args:
            request: The gRPC request containing the service name.
            context: The gRPC context.

        Returns:
            A ServiceResponse message indicating the result of the restart operation.
        """
        service_name = request.service_name
        try:
            container = self._get_closest_container(service_name)
            if container:
                container.restart()
                return service_manager_pb2.ServiceResponse(
                    status=f"Service '{container.name}' restarted successfully."
                )
            return service_manager_pb2.ServiceResponse(
                status=f"Service '{service_name}' not found."
            )
        except docker.errors.DockerException as error:
            return service_manager_pb2.ServiceResponse(
                status=f"Error restarting service: {str(error)}"
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
        container_list = self.client.containers.list(all=True)
        container_names = [container.name for container in container_list]
        matches = difflib.get_close_matches(service_name, container_names, n=1, cutoff=0.6)

        if matches:
            return self.client.containers.get(matches[0])
        return None


def serve():
    """
    Starts the gRPC server and listens for incoming requests.
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_manager_pb2_grpc.add_ServiceManagerServicer_to_server(ServiceManager(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Server stopping...")
        server.stop(0)


if __name__ == "__main__":
    serve()
