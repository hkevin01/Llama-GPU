#!/usr/bin/env python3
"""
Code Analysis Tool Integration
Provides code quality analysis, complexity metrics, and suggestions
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

try:
    from radon.complexity import cc_visit
    from radon.metrics import h_visit, mi_visit
    from radon.raw import analyze
    RADON_AVAILABLE = True
except ImportError:
    RADON_AVAILABLE = False
    logging.warning("Radon not available. Install with: pip install radon")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """
    Analyzes Python code for complexity, quality metrics, and potential issues.
    Integrates with RAG system to provide code analysis context.
    """
    
    def __init__(self):
        self.radon_available = RADON_AVAILABLE
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a Python file for various metrics.
        
        Args:
            file_path: Path to Python file
        
        Returns:
            Dictionary with analysis results
        """
        if not Path(file_path).exists():
            return {"error": f"File not found: {file_path}"}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            return self.analyze_code(code, file_path)
        except Exception as e:
            return {"error": f"Error analyzing file: {str(e)}"}
    
    def analyze_code(self, code: str, source_name: str = "<string>") -> Dict[str, Any]:
        """
        Analyze Python code string.
        
        Args:
            code: Python code as string
            source_name: Name of source for reporting
        
        Returns:
            Dictionary with analysis results
        """
        results = {
            "source": source_name,
            "basic_stats": {},
            "complexity": {},
            "issues": [],
            "suggestions": []
        }
        
        # Basic AST analysis
        try:
            tree = ast.parse(code)
            results["basic_stats"] = self._analyze_ast(tree)
        except SyntaxError as e:
            results["issues"].append({
                "type": "SyntaxError",
                "message": str(e),
                "line": e.lineno
            })
            return results
        
        # Radon analysis (if available)
        if self.radon_available:
            try:
                # Cyclomatic complexity
                complexity_results = cc_visit(code)
                results["complexity"]["cyclomatic"] = [
                    {
                        "name": item.name,
                        "complexity": item.complexity,
                        "line": item.lineno,
                        "rank": item.letter
                    }
                    for item in complexity_results
                ]
                
                # Maintainability Index
                mi_score = mi_visit(code, multi=True)
                results["complexity"]["maintainability_index"] = mi_score
                
                # Halstead metrics
                halstead = h_visit(code)
                if halstead:
                    results["complexity"]["halstead"] = {
                        "difficulty": halstead[0].difficulty,
                        "effort": halstead[0].effort,
                        "volume": halstead[0].volume
                    }
                
                # Raw metrics
                raw = analyze(code)
                results["basic_stats"].update({
                    "loc": raw.loc,
                    "lloc": raw.lloc,
                    "sloc": raw.sloc,
                    "comments": raw.comments,
                    "blank": raw.blank
                })
                
                # Generate suggestions based on complexity
                results["suggestions"] = self._generate_suggestions(results)
                
            except Exception as e:
                logger.warning(f"Radon analysis error: {e}")
        
        return results
    
    def _analyze_ast(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze AST for basic statistics"""
        stats = {
            "functions": 0,
            "classes": 0,
            "imports": 0,
            "function_names": [],
            "class_names": []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                stats["functions"] += 1
                stats["function_names"].append(node.name)
            elif isinstance(node, ast.ClassDef):
                stats["classes"] += 1
                stats["class_names"].append(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                stats["imports"] += 1
        
        return stats
    
    def _generate_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions based on analysis"""
        suggestions = []
        
        # Check cyclomatic complexity
        if "cyclomatic" in analysis.get("complexity", {}):
            high_complexity = [
                item for item in analysis["complexity"]["cyclomatic"]
                if item["complexity"] > 10
            ]
            if high_complexity:
                for item in high_complexity:
                    suggestions.append(
                        f"Function '{item['name']}' (line {item['line']}) has high complexity "
                        f"({item['complexity']}). Consider refactoring into smaller functions."
                    )
        
        # Check maintainability index
        mi = analysis.get("complexity", {}).get("maintainability_index")
        if mi and mi < 65:
            suggestions.append(
                f"Code has low maintainability index ({mi:.1f}). "
                "Consider refactoring to improve readability and reduce complexity."
            )
        
        # Check function count
        if analysis.get("basic_stats", {}).get("functions", 0) > 50:
            suggestions.append(
                "File has many functions. Consider splitting into multiple modules."
            )
        
        # Check comments ratio
        stats = analysis.get("basic_stats", {})
        if stats.get("loc", 1) > 0:
            comment_ratio = stats.get("comments", 0) / stats.get("loc", 1)
            if comment_ratio < 0.1 and stats.get("loc", 0) > 100:
                suggestions.append(
                    f"Code has low comment ratio ({comment_ratio:.1%}). "
                    "Consider adding more documentation."
                )
        
        return suggestions
    
    def get_analysis_summary(self, analysis: Dict[str, Any]) -> str:
        """
        Get human-readable summary of analysis.
        
        Args:
            analysis: Analysis results dictionary
        
        Returns:
            Formatted summary string
        """
        if "error" in analysis:
            return f"Error: {analysis['error']}"
        
        summary = []
        summary.append(f"# Code Analysis: {analysis['source']}\n")
        
        # Basic stats
        stats = analysis.get("basic_stats", {})
        if stats:
            summary.append("## Basic Statistics")
            summary.append(f"- Lines of Code: {stats.get('loc', 'N/A')}")
            summary.append(f"- Logical LOC: {stats.get('lloc', 'N/A')}")
            summary.append(f"- Comments: {stats.get('comments', 'N/A')}")
            summary.append(f"- Functions: {stats.get('functions', 0)}")
            summary.append(f"- Classes: {stats.get('classes', 0)}")
            summary.append("")
        
        # Complexity
        complexity = analysis.get("complexity", {})
        if complexity:
            summary.append("## Complexity Metrics")
            
            mi = complexity.get("maintainability_index")
            if mi:
                mi_rating = "Good" if mi > 85 else "Fair" if mi > 65 else "Poor"
                summary.append(f"- Maintainability Index: {mi:.1f} ({mi_rating})")
            
            cyclomatic = complexity.get("cyclomatic", [])
            if cyclomatic:
                avg_complexity = sum(item["complexity"] for item in cyclomatic) / len(cyclomatic)
                max_complexity = max(item["complexity"] for item in cyclomatic)
                summary.append(f"- Average Cyclomatic Complexity: {avg_complexity:.1f}")
                summary.append(f"- Maximum Cyclomatic Complexity: {max_complexity}")
                
                high_complexity = [item for item in cyclomatic if item["complexity"] > 10]
                if high_complexity:
                    summary.append(f"- Functions with high complexity: {len(high_complexity)}")
            
            summary.append("")
        
        # Issues
        issues = analysis.get("issues", [])
        if issues:
            summary.append("## Issues")
            for issue in issues:
                summary.append(f"- [{issue['type']}] {issue['message']} (line {issue.get('line', '?')})")
            summary.append("")
        
        # Suggestions
        suggestions = analysis.get("suggestions", [])
        if suggestions:
            summary.append("## Suggestions")
            for suggestion in suggestions:
                summary.append(f"- {suggestion}")
            summary.append("")
        
        return "\n".join(summary)
    
    def analyze_directory(self, directory: str, pattern: str = "**/*.py") -> Dict[str, Any]:
        """
        Analyze all Python files in a directory.
        
        Args:
            directory: Directory path
            pattern: File pattern to match
        
        Returns:
            Dictionary mapping file paths to analysis results
        """
        results = {}
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return {"error": f"Directory not found: {directory}"}
        
        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                results[str(file_path)] = self.analyze_file(str(file_path))
        
        return results


def main():
    """Test code analyzer"""
    analyzer = CodeAnalyzer()
    
    # Test with sample code
    sample_code = """
def complex_function(x, y, z):
    '''This function has high complexity'''
    if x > 0:
        if y > 0:
            if z > 0:
                result = x + y + z
            else:
                result = x + y - z
        else:
            if z > 0:
                result = x - y + z
            else:
                result = x - y - z
    else:
        if y > 0:
            if z > 0:
                result = -x + y + z
            else:
                result = -x + y - z
        else:
            if z > 0:
                result = -x - y + z
            else:
                result = -x - y - z
    return result

class MyClass:
    def __init__(self):
        self.value = 0
    
    def simple_method(self):
        return self.value * 2
"""
    
    print("Analyzing sample code...\n")
    analysis = analyzer.analyze_code(sample_code, "sample.py")
    summary = analyzer.get_analysis_summary(analysis)
    print(summary)


if __name__ == "__main__":
    main()
