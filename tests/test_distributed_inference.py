"""
Unit tests for Distributed Inference
"""
import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.backend.distributed_inference import (
    run_distributed_inference, 
    setup_cluster
)


class TestDistributedInference(unittest.TestCase):
    
    def test_run_distributed_inference(self):
        """Test distributed inference execution"""
        cluster_config = {
            'name': 'test-cluster',
            'nodes': [
                {'id': 'node-1', 'ip': '192.168.1.10'},
                {'id': 'node-2', 'ip': '192.168.1.11'}
            ]
        }
        
        result = run_distributed_inference(
            cluster_config, 
            '/path/to/model', 
            'test input data'
        )
        
        self.assertEqual(result['status'], 'completed')
        self.assertIn('total_tokens_generated', result)
        self.assertIn('average_inference_time', result)
        self.assertEqual(result['nodes_used'], 2)
    
    def test_run_distributed_inference_invalid_config(self):
        """Test with invalid cluster configuration"""
        # Empty cluster config
        result = run_distributed_inference({}, '/path/to/model', 'data')
        self.assertEqual(result['status'], 'failed')
        self.assertIn('error', result)
        
        # No nodes in config
        result = run_distributed_inference(
            {'name': 'test', 'nodes': []}, 
            '/path/to/model', 
            'data'
        )
        self.assertEqual(result['status'], 'failed')
    
    def test_setup_cluster(self):
        """Test cluster setup"""
        cluster_config = {
            'name': 'test-cluster',
            'nodes': [
                {'id': 'node-1', 'ip': '192.168.1.10'},
                {'id': 'node-2', 'ip': '192.168.1.11'}
            ]
        }
        
        result = setup_cluster(cluster_config)
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
