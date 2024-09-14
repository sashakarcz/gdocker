import unittest
from unittest.mock import patch, MagicMock
from server_manager import ServiceManager

class TestServiceManager(unittest.TestCase):
    @patch('server_manager.docker.from_env')
    def setUp(self, mock_docker):
        self.mock_client = MagicMock()
        mock_docker.return_value = self.mock_client
        self.service_manager = ServiceManager()

    @patch('server_manager.docker.from_env')
    def test_restart_service(self, mock_docker):
        mock_docker.return_value = self.mock_client
        mock_container = MagicMock()
        mock_container.name = "test_service"
        self.mock_client.containers.get.return_value = mock_container

        request = MagicMock()
        request.service_name = "test_service"

        # Mock _get_closest_container to return a container
        self.service_manager._get_closest_container = MagicMock(return_value=mock_container)

        response = self.service_manager.restart_service(request, None)
        mock_container.restart.assert_called_once()
        self.assertEqual(response.status, "Service 'test_service' restarted successfully.")

    @patch('server_manager.docker.from_env')
    def test_search_service(self, mock_docker):
        mock_docker.return_value = self.mock_client
        mock_container = MagicMock()
        mock_container.name = "test_service"
        self.mock_client.containers.list.return_value = [mock_container]

        request = MagicMock()
        request.search_term = "test"

        response = self.service_manager.search_service(request, None)
        self.assertIn("test_service", response.container_names)

    @patch('server_manager.docker.from_env')
    def test_start_service(self, mock_docker):
        mock_docker.return_value = self.mock_client
        mock_container = MagicMock()
        mock_container.name = "test_service"
        self.mock_client.containers.get.return_value = mock_container

        request = MagicMock()
        request.service_name = "test_service"

        # Mock _get_closest_container to return a container
        self.service_manager._get_closest_container = MagicMock(return_value=mock_container)

        response = self.service_manager.start_service(request, None)
        mock_container.start.assert_called_once()
        self.assertEqual(response.status, "Service 'test_service' started successfully.")

    @patch('server_manager.docker.from_env')
    def test_stop_service(self, mock_docker):
        mock_docker.return_value = self.mock_client
        mock_container = MagicMock()
        mock_container.name = "test_service"
        self.mock_client.containers.get.return_value = mock_container

        request = MagicMock()
        request.service_name = "test_service"

        # Mock _get_closest_container to return a container
        self.service_manager._get_closest_container = MagicMock(return_value=mock_container)

        response = self.service_manager.stop_service(request, None)
        mock_container.stop.assert_called_once()
        self.assertEqual(response.status, "Service 'test_service' stopped successfully.")

if __name__ == '__main__':
    unittest.main()