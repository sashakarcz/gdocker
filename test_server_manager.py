import unittest
from unittest.mock import patch, MagicMock
import grpc
from concurrent import futures
import service_manager_pb2
import service_manager_pb2_grpc
from server_manager import ServiceManager, serve

class TestServiceManager(unittest.TestCase):
    @patch('docker.from_env')
    def setUp(self, mock_docker):
        self.mock_docker = mock_docker
        self.mock_client = MagicMock()
        self.mock_docker.return_value = self.mock_client
        self.service_manager = ServiceManager()

    def test_restart_service_success(self):
        request = service_manager_pb2.ServiceRequest(service_name='test_service')
        context = MagicMock()
        mock_container = MagicMock()
        self.mock_client.containers.list.return_value = [mock_container]
        mock_container.name = 'test_service'
        self.mock_client.containers.get.return_value = mock_container

        response = self.service_manager.RestartService(request, context)
        self.assertEqual(response.status, "Service 'test_service' restarted successfully.")
        mock_container.restart.assert_called_once()

    def test_restart_service_not_found(self):
        request = service_manager_pb2.ServiceRequest(service_name='unknown_service')
        context = MagicMock()
        self.mock_client.containers.list.return_value = []

        response = self.service_manager.RestartService(request, context)
        self.assertEqual(response.status, "Service 'unknown_service' not found.")

    def test_restart_service_exception(self):
        request = service_manager_pb2.ServiceRequest(service_name='test_service')
        context = MagicMock()
        self.mock_client.containers.list.side_effect = Exception('Test exception')

        response = self.service_manager.RestartService(request, context)
        self.assertTrue('Error restarting service' in response.status)

class TestServeFunction(unittest.TestCase):
    @patch('grpc.server')
    def test_serve(self, mock_grpc_server):
        mock_server = MagicMock()
        mock_grpc_server.return_value = mock_server

        with patch('builtins.print') as mock_print:
            with self.assertRaises(KeyboardInterrupt):
                serve()
            mock_print.assert_any_call("Server started on port 50051")
            mock_print.assert_any_call("Server stopping...")
            mock_print.assert_any_call("Server stopped")
            mock_server.start.assert_called_once()
            mock_server.wait_for_termination.assert_called_once()
            mock_server.stop.assert_called_once_with(0)

if __name__ == '__main__':
    unittest.main()