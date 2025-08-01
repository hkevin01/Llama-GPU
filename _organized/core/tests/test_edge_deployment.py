"""
Unit tests for Edge Deployment
"""
import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.backend.edge_deployment import (
    deploy_to_edge, 
    get_deployment_status
)


class TestEdgeDeployment(unittest.TestCase):
    
    def test_deploy_to_edge_jetson(self):
        """Test deployment to Jetson device"""
        device_info = {
            'type': 'jetson',
            'ip': '192.168.1.100',
            'name': 'jetson-nano-01'
        }
        
        result = deploy_to_edge(device_info, '/path/to/model')
        self.assertTrue(result)
    
    def test_deploy_to_edge_pi(self):
        """Test deployment to Raspberry Pi"""
        device_info = {
            'type': 'pi',
            'ip': '192.168.1.101',
            'name': 'raspberry-pi-01'
        }
        
        result = deploy_to_edge(device_info, '/path/to/model')
        self.assertTrue(result)
    
    def test_deploy_to_edge_generic(self):
        """Test generic deployment"""
        device_info = {
            'type': 'custom',
            'ip': '192.168.1.102',
            'name': 'custom-device-01'
        }
        
        result = deploy_to_edge(device_info, '/path/to/model')
        self.assertTrue(result)
    
    def test_deploy_invalid_inputs(self):
        """Test deployment with invalid inputs"""
        # Empty device info
        result = deploy_to_edge({}, '/path/to/model')
        self.assertFalse(result)
        
        # Empty model path
        result = deploy_to_edge({'type': 'jetson'}, '')
        self.assertFalse(result)
    
    def test_get_deployment_status(self):
        """Test getting deployment status"""
        device_info = {'type': 'jetson', 'ip': '192.168.1.100'}
        status = get_deployment_status(device_info)
        
        self.assertIn('status', status)
        self.assertIn('model_loaded', status)
        self.assertIn('last_inference', status)


if __name__ == '__main__':
    unittest.main()
