"""Helper utilities for test documentation and JSON output generation."""

import json
import inspect
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


def generate_test_documentation(test_module_path: str, test_classes: List[type]) -> Dict[str, Any]:
    """
    Generate comprehensive documentation for a test module.
    
    Args:
        test_module_path: Path to the test module file
        test_classes: List of test class objects
        
    Returns:
        Dictionary containing test documentation
    """
    module_name = Path(test_module_path).stem
    
    documentation = {
        "test_module": module_name,
        "file_path": test_module_path,
        "generated_at": datetime.now().isoformat(),
        "total_test_classes": len(test_classes),
        "total_test_cases": 0,
        "test_classes": []
    }
    
    for test_class in test_classes:
        class_info = {
            "class_name": test_class.__name__,
            "description": test_class.__doc__.strip() if test_class.__doc__ else "",
            "test_cases": []
        }
        
        # Get all test methods
        test_methods = [
            method for method in dir(test_class)
            if method.startswith('test_') and callable(getattr(test_class, method))
        ]
        
        for method_name in test_methods:
            method = getattr(test_class, method_name)
            test_case = {
                "test_name": method_name,
                "description": method.__doc__.strip() if method.__doc__ else "No description",
                "test_type": "unit"
            }
            
            # Check for markers
            if hasattr(method, 'pytestmark'):
                markers = [mark.name for mark in method.pytestmark]
                test_case["markers"] = markers
                if "integration" in markers:
                    test_case["test_type"] = "integration"
                if "asyncio" in markers:
                    test_case["async"] = True
            
            class_info["test_cases"].append(test_case)
            documentation["total_test_cases"] += 1
        
        class_info["test_case_count"] = len(class_info["test_cases"])
        documentation["test_classes"].append(class_info)
    
    return documentation


def save_test_documentation(documentation: Dict[str, Any], output_dir: str = "tests/docs") -> str:
    """
    Save test documentation to a JSON file.
    
    Args:
        documentation: Test documentation dictionary
        output_dir: Directory to save the JSON file
        
    Returns:
        Path to the saved JSON file
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    module_name = documentation["test_module"]
    json_file = output_path / f"{module_name}_documentation.json"
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(documentation, f, indent=2, ensure_ascii=False)
    
    return str(json_file)
