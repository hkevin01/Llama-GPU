"""
Edge Deployment Automation Module
Supports K8s, Docker, and serverless deployment automation.
"""

import logging
import subprocess
import yaml
from src.deployment_templates import K8S_TEMPLATE, DOCKER_TEMPLATE, SERVERLESS_TEMPLATE

logging.basicConfig(filename='logs/edge_deploy.log', level=logging.INFO)

def deploy_k8s(config):
    with open('k8s_deploy.yaml', 'w') as f:
        yaml.dump(config, f)
    try:
        subprocess.run(['kubectl', 'apply', '-f', 'k8s_deploy.yaml'], check=True)
        logging.info('Deployed to Kubernetes with config: %s', config)
        return True
    except subprocess.CalledProcessError as e:
        logging.error('K8s deployment failed: %s', e)
        return False

def deploy_docker(image):
    try:
        subprocess.run(['docker', 'run', '-d', image], check=True)
        logging.info('Deployed Docker image: %s', image)
        return True
    except subprocess.CalledProcessError as e:
        logging.error('Docker deployment failed: %s', e)
        return False

def deploy_serverless(provider, config):
    # Example: Simulate serverless deployment
    logging.info('Deployed to %s serverless with config: %s', provider, config)
    return True
