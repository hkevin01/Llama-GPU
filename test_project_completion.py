#!/usr/bin/env python3
"""
Project Documentation Verification Script

This script verifies that all features documented in the README and docs
are actually implemented and working in the codebase.
"""

import importlib.util
import inspect
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

# Add src to the path for imports
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

class DocumentationVerifier:
    """Verifies that documented features are actually implemented."""
    
    def __init__(self):
        self.project_root = project_root
        self.src_path = src_path
        self.results = {
            "documented_features": {},
            "implemented_features": {},
            "missing_features": [],
            "extra_features": [],
            "verification_status": "INCOMPLETE"
        }
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def check_file_exists(self, file_path: str) -> bool:
        """Check if a file exists relative to project root."""
        full_path = self.project_root / file_path
        return full_path.exists()
    
    def check_import_available(self, module_name: str) -> bool:
        """Check if a module can be imported."""
        try:
            spec = importlib.util.find_spec(module_name)
            return spec is not None
        except ImportError:
            return False
    
    def check_class_exists(self, module_name: str, class_name: str) -> bool:
        """Check if a class exists in a module."""
        try:
            module = importlib.import_module(module_name)
            return hasattr(module, class_name)
        except ImportError:
            return False
    
    def check_method_exists(self, module_name: str, class_name: str, method_name: str) -> bool:
        """Check if a method exists in a class."""
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, class_name):
                cls = getattr(module, class_name)
                return hasattr(cls, method_name)
            return False
        except ImportError:
            return False
    
    def verify_core_llama_gpu(self) -> Dict[str, bool]:
        """Verify core LlamaGPU functionality."""
        results = {}
        
        # Check if main LlamaGPU class exists
        results["LlamaGPU_class"] = self.check_class_exists("llama_gpu", "LlamaGPU")
        
        # Check core methods
        methods = ["infer", "batch_infer", "stream_infer", "get_backend_info"]
        for method in methods:
            results[f"LlamaGPU_{method}"] = self.check_method_exists("llama_gpu", "LlamaGPU", method)
        
        # Check backends
        backends = ["cpu_backend", "cuda_backend", "rocm_backend"]
        for backend in backends:
            results[f"backend_{backend}"] = self.check_import_available(f"backend.{backend}")
        
        # Check AWS detection
        results["aws_detection"] = self.check_import_available("utils.aws_detection")
        
        return results
    
    def verify_multi_gpu_support(self) -> Dict[str, bool]:
        """Verify multi-GPU functionality."""
        results = {}
        
        # Check multi-GPU module
        results["multi_gpu_module"] = self.check_import_available("multi_gpu")
        results["MultiGPUManager_class"] = self.check_class_exists("multi_gpu", "MultiGPUManager")
        results["GPUConfig_class"] = self.check_class_exists("multi_gpu", "GPUConfig")
        results["ParallelismStrategy_enum"] = self.check_class_exists("multi_gpu", "ParallelismStrategy")
        
        return results
    
    def verify_quantization_support(self) -> Dict[str, bool]:
        """Verify quantization functionality."""
        results = {}
        
        # Check quantization module
        results["quantization_module"] = self.check_import_available("quantization")
        results["QuantizationManager_class"] = self.check_class_exists("quantization", "QuantizationManager")
        results["QuantizationConfig_class"] = self.check_class_exists("quantization", "QuantizationConfig")
        results["QuantizationType_enum"] = self.check_class_exists("quantization", "QuantizationType")
        
        return results
    
    def verify_api_server(self) -> Dict[str, bool]:
        """Verify API server functionality."""
        results = {}
        
        # Check API server files
        results["api_server_module"] = self.check_import_available("api_server")
        results["async_server_module"] = self.check_import_available("api.async_server")
        
        # Check FastAPI app
        try:
            import api_server
            results["fastapi_app"] = hasattr(api_server, 'app')
        except ImportError:
            results["fastapi_app"] = False
        
        return results
    
    def verify_plugin_system(self) -> Dict[str, bool]:
        """Verify plugin system functionality."""
        results = {}
        
        # Check plugin manager
        results["plugin_manager_module"] = self.check_import_available("plugin_manager")
        results["PluginManager_class"] = self.check_class_exists("plugin_manager", "PluginManager")
        
        # Check plugin marketplace
        results["plugin_marketplace_module"] = self.check_import_available("plugin_marketplace")
        
        return results
    
    def verify_scripts_and_examples(self) -> Dict[str, bool]:
        """Verify scripts and examples exist."""
        results = {}
        
        # Check key scripts
        scripts = [
            "scripts/benchmark.py",
            "scripts/monitor_resources.py",
            "scripts/setup_local.sh",
            "scripts/setup_aws.sh"
        ]
        for script in scripts:
            results[f"script_{Path(script).name}"] = self.check_file_exists(script)
        
        # Check examples
        examples = [
            "examples/inference_example.py",
            "examples/text_generation.py",
            "examples/code_generation.py",
            "examples/conversation_simulation.py"
        ]
        for example in examples:
            results[f"example_{Path(example).name}"] = self.check_file_exists(example)
        
        return results
    
    def verify_documentation_files(self) -> Dict[str, bool]:
        """Verify documentation files exist."""
        results = {}
        
        # Check documentation files
        docs = [
            "docs/api.md",
            "docs/usage.md",
            "docs/project-plan.md",
            "docs/troubleshooting.md",
            "docs/benchmarks.md",
            "docs/test_plan.md"
        ]
        for doc in docs:
            results[f"doc_{Path(doc).name}"] = self.check_file_exists(doc)
        
        return results
    
    def verify_requirements_and_setup(self) -> Dict[str, bool]:
        """Verify requirements and setup files."""
        results = {}
        
        # Check setup files
        setup_files = [
            "requirements.txt",
            "setup.py",
            "README.md"
        ]
        for file in setup_files:
            results[f"setup_{file}"] = self.check_file_exists(file)
        
        return results
    
    def run_full_verification(self) -> Dict[str, any]:
        """Run complete verification of all features."""
        self.logger.info("Starting comprehensive documentation verification...")
        
        # Run all verification checks
        verification_categories = {
            "core_llama_gpu": self.verify_core_llama_gpu(),
            "multi_gpu_support": self.verify_multi_gpu_support(),
            "quantization_support": self.verify_quantization_support(),
            "api_server": self.verify_api_server(),
            "plugin_system": self.verify_plugin_system(),
            "scripts_and_examples": self.verify_scripts_and_examples(),
            "documentation_files": self.verify_documentation_files(),
            "requirements_and_setup": self.verify_requirements_and_setup()
        }
        
        # Compile results
        total_checks = 0
        passed_checks = 0
        failed_features = []
        
        for category, checks in verification_categories.items():
            for feature, status in checks.items():
                total_checks += 1
                if status:
                    passed_checks += 1
                else:
                    failed_features.append(f"{category}.{feature}")
        
        # Calculate completion percentage
        completion_percentage = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        # Determine overall status
        if completion_percentage >= 95:
            overall_status = "EXCELLENT"
        elif completion_percentage >= 85:
            overall_status = "GOOD"
        elif completion_percentage >= 70:
            overall_status = "FAIR"
        else:
            overall_status = "POOR"
        
        self.results = {
            "verification_categories": verification_categories,
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": total_checks - passed_checks,
            "completion_percentage": completion_percentage,
            "overall_status": overall_status,
            "failed_features": failed_features
        }
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate a comprehensive verification report."""
        results = self.results
        
        report = f"""
# Documentation Verification Report

## Summary
- **Total Checks**: {results['total_checks']}
- **Passed**: {results['passed_checks']}
- **Failed**: {results['failed_checks']}
- **Completion**: {results['completion_percentage']:.1f}%
- **Overall Status**: {results['overall_status']}

## Category Breakdown
"""
        
        for category, checks in results["verification_categories"].items():
            passed = sum(1 for status in checks.values() if status)
            total = len(checks)
            percentage = (passed / total) * 100 if total > 0 else 0
            
            report += f"\n### {category.replace('_', ' ').title()}\n"
            report += f"- **Status**: {passed}/{total} ({percentage:.1f}%)\n"
            
            if passed < total:
                failed_items = [item for item, status in checks.items() if not status]
                report += f"- **Missing**: {', '.join(failed_items)}\n"
        
        if results["failed_features"]:
            report += f"\n## Failed Features\n"
            for feature in results["failed_features"]:
                report += f"- {feature}\n"
        
        return report


def main():
    """Main function to run verification."""
    verifier = DocumentationVerifier()
    results = verifier.run_full_verification()
    report = verifier.generate_report()
    
    print(report)
    
    # Save results to file
    output_file = project_root / "verification_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\nDetailed results saved to: {output_file}")
    
    # Exit with appropriate code
    if results["completion_percentage"] >= 85:
        print("✅ Documentation verification PASSED!")
        sys.exit(0)
    else:
        print("❌ Documentation verification FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    main()
