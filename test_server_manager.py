# pylint: disable=W0221, E1111, E1101

"""
Unit tests for ServiceManager and serve function.
"""

import unittest
from unittest.mock import patch, MagicMock
from server_manager import ServiceManager, serve
import warnings

# Suppress ResourceWarning for unclosed sockets
warnings.filterwarnings("ignore", category=ResourceWarning)


class TestServiceManager(unittest.TestCase):
    """
    Test cases for the ServiceManager class.
    """

    @patch('docker.from_env')
    def setUp(self, mock_docker):
        """
        Set up the test environment with mocked Docker client.
        """
        self.mock_docker = mock_docker
        self.mock_client = MagicMock()
        self.mock_docker.return_value = self.mock_client
        self.service_manager = ServiceManager()

    def test_restart_service_success(self):
        """
        Test successful service restart when service is found.
        """
        request = MagicMock(service_name='test_service')
        context = MagicMock()
        mock_container = MagicMock()
        self.mock_client.containers.list.return_value = [mock_container]
        mock_container.name = 'test_service'
        self.mock_client.containers.get.return_value = mock_container

        response = self.service_manager.restart_service(request, context)
        self.assertEqual(
            response.status, "Service 'test_service' restarted successfully."
        )
        mock_container.restart.assert_called_once()

    def test_restart_service_not_found(self):
        """
        Test service restart when the service is not found.
        """
        request = MagicMock(service_name='unknown_service')
        context = MagicMock()
        self.mock_client.containers.list.return_value = []

        response = self.service_manager.restart_service(request, context)
        self.assertEqual(response.status, "Service 'unknown_service' not found.")

    def test_restart_service_exception(self):
        """
        Test handling of an exception during service restart.
        """
        request = MagicMock(service_name='test_service')
        context = MagicMock()
        self.mock_client.containers.list.side_effect = Exception('Test exception')

        # Ensure the exception is caught and an error message is returned
        response = self.service_manager.restart_service(request, context)
        self.assertIn('Error restarting service', response.status)

    def test_start_service_success(self):
        """
        Test successful service start when service is found.
        """
        request = MagicMock(service_name='test_service')
        context = MagicMock()
        mock_container = MagicMock()
        self.mock_client.containers.list.return_value = [mock_container]
        mock_container.name = 'test_service'
        self.mock_client.containers.get.return_value = mock_container

        response = self.service_manager.start_service(request, context)
        self.assertEqual(
            response.status, "Service 'test_service' started successfully."
        )
        mock_container.start.assert_called_once()

    def test_search_service(self):
        """
        Test searching for a service by name.
        """
        request = MagicMock(search_term='test_service')
        context = MagicMock()
        mock_container = MagicMock()
        mock_container.name = 'test_service'
        self.mock_client.containers.list.return_value = [mock_container]

        response = self.service_manager.search_service(request, context)
        self.assertEqual(response.container_names, ['test_service'])

    def test_search_service_no_matches(self):
        """
        Test searching for a service when no matches are found.
        """
        request = MagicMock(search_term='unknown_service')
        context = MagicMock()
        self.mock_client.containers.list.return_value = []

        response = self.service_manager.search_service(request, context)
        self.assertEqual(response.container_names, [])


class TestServeFunction(unittest.TestCase):
    """
    Test cases for the serve function.
    """

    @patch('docker.from_env')  # Mock docker client
    @patch('grpc.server')
    def test_serve(self, mock_grpc_server, mock_docker):
        """
        Test the serve function to ensure it starts and stops the gRPC server.
        """
        mock_server = MagicMock()
        mock_grpc_server.return_value = mock_server

        mock_client = MagicMock()
        mock_docker.return_value = mock_client  # Mock Docker client return

        with patch('builtins.print') as mock_print:
            # Simulate KeyboardInterrupt by calling stop on server
            mock_server.wait_for_termination.side_effect = KeyboardInterrupt

            serve()

            # Check that the server was started, stopped and correct messages printed
            mock_print.assert_any_call("Server started on port 50051")
            mock_server.start.assert_called_once()
            mock_server.wait_for_termination.assert_called_once()

            mock_server.stop.assert_called_once_with(0)
            mock_print.assert_any_call("Server stopping...")
            mock_print.assert_any_call("Server stopped")


if __name__ == '__main__':
    unittest.main()