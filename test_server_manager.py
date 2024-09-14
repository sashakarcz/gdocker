"""
Unit tests for the ServiceManager class.
"""

import unittest
from unittest.mock import patch, MagicMock
import docker
from server_manager import ServiceManager

class TestServiceManager(unittest.TestCase):
    """
    Test case for the ServiceManager class.
    """

    def setUp(self):
        """
        Set up the test case with a mocked Docker client.
        """
        patcher = patch('server_manager.docker.from_env')
        self.addCleanup(patcher.stop)
        mock_docker = patcher.start()
        self.mock_client = MagicMock()
        mock_docker.return_value = self.mock_client
        self.service_manager = ServiceManager()
        self.mock_container = MagicMock()
        self.mock_container.name = "test_service"

    def test_restart_service(self):
        """
        Test the restart_service method.
        """
        self.mock_client.containers.get.return_value = self.mock_container

        request = MagicMock()
        request.service_name = "test_service"

        # Mock _get_closest_container to return a container
        with patch.object(self.service_manager, '_get_closest_container',
                          return_value=self.mock_container):
            response = self.service_manager.restart_service(request, None)

        self.mock_container.restart.assert_called_once()
        self.assertEqual(response.status, "Service 'test_service' restarted successfully.")

    def test_search_service(self):
        """
        Test the search_service method.
        """
        self.mock_client.containers.list.return_value = [self.mock_container]

        request = MagicMock()
        request.search_term = "test"

        response = self.service_manager.search_service(request, None)
        self.assertIn("test_service", response.container_names)

    def test_start_service(self):
        """
        Test the start_service method.
        """
        self.mock_client.containers.get.return_value = self.mock_container

        request = MagicMock()
        request.service_name = "test_service"

        # Mock _get_closest_container to return a container
        with patch.object(self.service_manager, '_get_closest_container',
                          return_value=self.mock_container):
            response = self.service_manager.start_service(request, None)

        self.mock_container.start.assert_called_once()
        self.assertEqual(response.status, "Service 'test_service' started successfully.")

    def test_stop_service(self):
        """
        Test the stop_service method.
        """
        self.mock_client.containers.get.return_value = self.mock_container

        request = MagicMock()
        request.service_name = "test_service"

        # Mock _get_closest_container to return a container
        with patch.object(self.service_manager, '_get_closest_container',
                          return_value=self.mock_container):
            response = self.service_manager.stop_service(request, None)

        self.mock_container.stop.assert_called_once()
        self.assertEqual(response.status, "Service 'test_service' stopped successfully.")

    def test_restart_service_not_found(self):
        """
        Test the restart_service method when the service is not found.
        """
        request = MagicMock()
        request.service_name = "unknown_service"

        # Mock _get_closest_container to return None
        with patch.object(self.service_manager, '_get_closest_container',
                          return_value=None):
            response = self.service_manager.restart_service(request, None)

        self.assertEqual(response.status, "Service 'unknown_service' not found.")
        self.mock_container.restart.assert_not_called()

    def test_restart_service_docker_exception(self):
        """
        Test the restart_service method when a Docker exception occurs.
        """
        request = MagicMock()
        request.service_name = "test_service"

        # Mock _get_closest_container to raise a DockerException
        with patch.object(self.service_manager, '_get_closest_container',
                          side_effect=docker.errors.DockerException("Test exception")):
            response = self.service_manager.restart_service(request, None)

        self.assertIn("Error restarting service", response.status)

    def test_search_service_no_matches(self):
        """
        Test the search_service method when no services match the search term.
        """
        self.mock_client.containers.list.return_value = []

        request = MagicMock()
        request.search_term = "nonexistent_service"

        response = self.service_manager.search_service(request, None)
        self.assertEqual(response.container_names, [])


if __name__ == '__main__':
    unittest.main()
