"""
Deployment Templates
Provides YAML/JSON templates for edge/cloud deployment scenarios.
"""

K8S_TEMPLATE = {
    'apiVersion': 'apps/v1',
    'kind': 'Deployment',
    'metadata': {'name': 'llama-gpu'},
    'spec': {
        'replicas': 1,
        'selector': {'matchLabels': {'app': 'llama-gpu'}},
        'template': {
            'metadata': {'labels': {'app': 'llama-gpu'}},
            'spec': {
                'containers': [{
                    'name': 'llama-gpu',
                    'image': 'llama-gpu:latest',
                    'ports': [{'containerPort': 5000}]
                }]
            }
        }
    }
}

DOCKER_TEMPLATE = {
    'image': 'llama-gpu:latest',
    'ports': [5000],
    'env': {'ENV': 'production'}
}

SERVERLESS_TEMPLATE = {
    'provider': 'aws',
    'memory': 512,
    'timeout': 30
}
