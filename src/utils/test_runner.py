import os
import pytest
from typing import Dict, List, Tuple
from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class TestResult:
    total_tests: int
    passed_tests: int
    failed_tests: int
    error_tests: int
    skipped_tests: int
    failures: List[Dict[str, str]]  # List of failure details

class TestRunner:
    def __init__(self, test_dir: str):
        self.test_dir = test_dir
        
    def run_tests(self, test_files: List[str] = None) -> Dict[str, TestResult]:
        """Run tests and return results for each file."""
        if test_files is None:
            test_files = self._find_test_files()
            
        results = {}
        for test_file in test_files:
            result = self._run_single_test_file(test_file)
            results[test_file] = result
            
        return results
    
    def _find_test_files(self) -> List[str]:
        """Find all test files in the test directory."""
        test_files = []
        for root, _, files in os.walk(self.test_dir):
            for file in files:
                if file.endswith('_test.py'):
                    test_files.append(os.path.join(root, file))
        return test_files
    
    def _run_single_test_file(self, test_file: str) -> TestResult:
        """Run tests for a single file and return results."""
        # Run pytest and capture results
        result = pytest.main([
            test_file,
            '-v',
            '--tb=short',
            '--capture=sys'
        ])
        
        # Parse pytest output
        report = pytest.main([
            test_file,
            '--json-report',
            '--json-report-file=none'
        ])
        
        # Extract test results
        total = 0
        passed = 0
        failed = 0
        errors = 0
        skipped = 0
        failures = []
        
        for test in report.report.get('tests', []):
            total += 1
            outcome = test.get('outcome', '')
            
            if outcome == 'passed':
                passed += 1
            elif outcome == 'failed':
                failed += 1
                failures.append({
                    'name': test.get('nodeid', ''),
                    'message': test.get('message', ''),
                    'traceback': test.get('traceback', '')
                })
            elif outcome == 'error':
                errors += 1
                failures.append({
                    'name': test.get('nodeid', ''),
                    'message': test.get('message', ''),
                    'traceback': test.get('traceback', '')
                })
            elif outcome == 'skipped':
                skipped += 1
        
        return TestResult(
            total_tests=total,
            passed_tests=passed,
            failed_tests=failed,
            error_tests=errors,
            skipped_tests=skipped,
            failures=failures
        )

class TestReporter:
    @staticmethod
    def print_report(results: Dict[str, TestResult]):
        """Print a formatted report of test results."""
        print("\n=== Test Execution Report ===\n")
        
        # Per-file results
        print("Per-File Results:")
        print("-" * 80)
        for file_path, result in results.items():
            file_name = os.path.basename(file_path)
            pass_rate = (result.passed_tests / result.total_tests * 100) if result.total_tests > 0 else 0
            print(f"\n{file_name}:")
            print(f"  Total Tests: {result.total_tests}")
            print(f"  Passed: {result.passed_tests} ({pass_rate:.1f}%)")
            print(f"  Failed: {result.failed_tests}")
            print(f"  Errors: {result.error_tests}")
            print(f"  Skipped: {result.skipped_tests}")
            
            if result.failures:
                print("\n  Failures:")
                for failure in result.failures:
                    print(f"    - {failure['name']}")
                    print(f"      {failure['message']}")
        
        # Overall results
        total_tests = sum(r.total_tests for r in results.values())
        total_passed = sum(r.passed_tests for r in results.values())
        total_failed = sum(r.failed_tests for r in results.values())
        total_errors = sum(r.error_tests for r in results.values())
        total_skipped = sum(r.skipped_tests for r in results.values())
        
        overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print("\nOverall Results:")
        print("-" * 80)
        print(f"Total Files: {len(results)}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_passed} ({overall_pass_rate:.1f}%)")
        print(f"Failed: {total_failed}")
        print(f"Errors: {total_errors}")
        print(f"Skipped: {total_skipped}")
        print("-" * 80) 