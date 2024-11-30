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
        self.mock_container.logs.return_value = b"test logs"
        self.mock_container.status = "running"

    def test_restart_service(self):
        """
        Test the restart_service method.
        """
        self.mock_client.containers.list.return_value = [self.mock_container]

        request = MagicMock()
        request.service_name = "test_service"
        response = self.service_manager.restart_service(request, None)

        self.mock_container.restart.assert_called_once()
        self.assertEqual(response.status, "Service 'test_service' restarted successfully.")

    def test_stop_service(self):
        """
        Test the stop_service method.
        """
        self.mock_client.containers.list.return_value = [self.mock_container]

        request = MagicMock()
        request.service_name = "test_service"
        response = self.service_manager.stop_service(request, None)

        self.mock_container.stop.assert_called_once()
        self.assertEqual(response.status, "Service 'test_service' stopped successfully.")

    def test_start_service(self):
        """
        Test the start_service method.
        """
        self.mock_client.containers.list.return_value = [self.mock_container]

        request = MagicMock()
        request.service_name = "test_service"
        response = self.service_manager.start_service(request, None)

        self.mock_container.start.assert_called_once()
        self.assertEqual(response.status, "Service 'test_service' started successfully.")

    def test_status_service(self):
        """
        Test the status_service method.
        """
        self.mock_client.containers.list.return_value = [self.mock_container]

        request = MagicMock()
        request.service_name = "test_service"
        response = self.service_manager.status_service(request, None)

        self.assertEqual(response.statuses, ["Container 'test_service' is running"])

    def test_logs_service(self):
        """
        Test the logs_service method.
        """
        self.mock_client.containers.list.return_value = [self.mock_container]

        request = MagicMock()
        request.service_name = "test_service"
        request.follow = False
        response = self.service_manager.logs_service(request, None)

        self.mock_container.logs.assert_called_once_with(follow=False)
        self.assertEqual(response.logs, ["Logs for container 'test_service':\ntest logs"])

    def test_logs_service_no_containers(self):
        """
        Test the logs_service method when no containers are found.
        """
        self.mock_client.containers.list.return_value = []

        request = MagicMock()
        request.service_name = "test_service"
        request.follow = False
        response = self.service_manager.logs_service(request, None)

        self.assertEqual(response.logs, ["No containers found for service 'test_service'."])

    def test_logs_service_error(self):
        """
        Test the logs_service method when an error occurs.
        """
        self.mock_client.containers.list.side_effect = docker.errors.DockerException("Error")

        request = MagicMock()
        request.service_name = "test_service"
        request.follow = False
        response = self.service_manager.logs_service(request, None)

        self.assertEqual(response.logs, ["Error retrieving logs: Error"])

if __name__ == '__main__':
    unittest.main()