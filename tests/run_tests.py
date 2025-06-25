#!/usr/bin/env python3
"""
Test Runner for PDF Bank Statement Obfuscator.

This script runs the tests and generates a comprehensive report.
"""

import os
import sys
import argparse
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import pytest
import pandas as pd
import matplotlib.pyplot as plt


def run_tests(test_types: List[str], output_dir: str, verbose: bool = False) -> Dict:
    """
    Run the specified types of tests and return the results.
    
    Args:
        test_types: List of test types to run (unit, integration, end_to_end, performance, ui)
        output_dir: Directory to save test results
        verbose: Whether to show verbose output
    
    Returns:
        Dictionary with test results
    """
    results = {}
    start_time = time.time()
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Map test types to directories
    test_dirs = {
        "unit": ["tests/pii_detection/test_detector_unit.py", "tests/obfuscation", "tests/pdf_parser"],
        "integration": ["tests/integration"],
        "end_to_end": ["tests/end_to_end"],
        "performance": ["tests/performance"],
        "ui": ["tests/ui"]
    }
    
    # Run each test type
    for test_type in test_types:
        if test_type not in test_dirs:
            print(f"Unknown test type: {test_type}")
            continue
        
        print(f"\n=== Running {test_type} tests ===\n")
        
        # Build the pytest command
        cmd = ["pytest"]
        
        # Add test directories
        for test_dir in test_dirs[test_type]:
            cmd.append(test_dir)
        
        # Add options
        if verbose:
            cmd.append("-v")
        
        # Add JUnit XML output
        xml_output = os.path.join(output_dir, f"{test_type}_results.xml")
        cmd.extend(["--junitxml", xml_output])
        
        # Add HTML report
        html_output = os.path.join(output_dir, f"{test_type}_report.html")
        cmd.extend(["--html", html_output, "--self-contained-html"])
        
        # Run the tests
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Store the results
        results[test_type] = {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "xml_output": xml_output if os.path.exists(xml_output) else None,
            "html_output": html_output if os.path.exists(html_output) else None
        }
        
        # Print the output
        print(result.stdout)
        if result.stderr:
            print(f"Errors:\n{result.stderr}")
        
        print(f"\n=== {test_type} tests completed with return code {result.returncode} ===\n")
    
    # Calculate total time
    total_time = time.time() - start_time
    
    # Add summary to results
    results["summary"] = {
        "total_time": total_time,
        "timestamp": datetime.now().isoformat(),
        "test_types": test_types
    }
    
    return results


def generate_report(results: Dict, output_dir: str) -> None:
    """
    Generate a comprehensive report from the test results.
    
    Args:
        results: Dictionary with test results
        output_dir: Directory to save the report
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a summary report
    summary = {
        "timestamp": results["summary"]["timestamp"],
        "total_time": results["summary"]["total_time"],
        "test_types": results["summary"]["test_types"],
        "results": {}
    }
    
    # Add results for each test type
    for test_type in results["summary"]["test_types"]:
        if test_type not in results:
            continue
        
        summary["results"][test_type] = {
            "returncode": results[test_type]["returncode"],
            "passed": results[test_type]["returncode"] == 0,
            "xml_output": results[test_type]["xml_output"],
            "html_output": results[test_type]["html_output"]
        }
    
    # Save the summary report
    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    
    # Create a summary HTML report
    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>PDF Bank Statement Obfuscator Test Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            h2 {{ color: #666; }}
            .passed {{ color: green; }}
            .failed {{ color: red; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        <h1>PDF Bank Statement Obfuscator Test Report</h1>
        <p>Generated on: {summary["timestamp"]}</p>
        <p>Total time: {summary["total_time"]:.2f} seconds</p>
        
        <h2>Summary</h2>
        <table>
            <tr>
                <th>Test Type</th>
                <th>Status</th>
                <th>Reports</th>
            </tr>
    """
    
    for test_type, result in summary["results"].items():
        status_class = "passed" if result["passed"] else "failed"
        status_text = "PASSED" if result["passed"] else "FAILED"
        
        html_report += f"""
            <tr>
                <td>{test_type}</td>
                <td class="{status_class}">{status_text}</td>
                <td>
        """
        
        if result["html_output"]:
            html_report += f'<a href="{os.path.basename(result["html_output"])}">HTML Report</a>'
        
        html_report += """
                </td>
            </tr>
        """
    
    html_report += """
        </table>
    </body>
    </html>
    """
    
    # Save the HTML report
    html_path = os.path.join(output_dir, "summary.html")
    with open(html_path, "w") as f:
        f.write(html_report)
    
    print(f"\nSummary report saved to {html_path}")
    print(f"Open this file in a web browser to view the test results.")


def main():
    """Main function to run the tests and generate a report."""
    parser = argparse.ArgumentParser(description="Run tests for PDF Bank Statement Obfuscator")
    parser.add_argument("--test-types", nargs="+", default=["unit", "integration", "end_to_end"],
                        choices=["unit", "integration", "end_to_end", "performance", "ui", "all"],
                        help="Types of tests to run")
    parser.add_argument("--output-dir", default="test_results",
                        help="Directory to save test results")
    parser.add_argument("--verbose", action="store_true",
                        help="Show verbose output")
    
    args = parser.parse_args()
    
    # Handle "all" test type
    if "all" in args.test_types:
        args.test_types = ["unit", "integration", "end_to_end", "performance", "ui"]
    
    # Run the tests
    results = run_tests(args.test_types, args.output_dir, args.verbose)
    
    # Generate the report
    generate_report(results, args.output_dir)


if __name__ == "__main__":
    main()