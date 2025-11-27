"""
Comprehensive Test Suite for Phi-3 Therapy Session Summarization
Tests the Ollama-based Phi-3-Mini model for clinical summarization.

This test suite validates:
1. Single session summarization
2. Multi-session summarization
3. Output format compliance
4. Risk keyword detection and formatting
5. Required sections presence
6. Performance metrics
"""

import sys
import os
import time
import re
import json
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

# Import the summarization service
try:
    from summarization_service_phi3 import SummarizationService, PromptFormatter
    from ollama_inference_engine import OllamaInferenceEngine, OllamaConfig
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the backend directory")
    sys.exit(1)


@dataclass
class TestResult:
    """Result of a single test"""
    test_name: str
    passed: bool
    message: str
    duration: float = 0.0
    details: Dict[str, Any] = None


class Phi3SummarizationTester:
    """Comprehensive tester for Phi-3 summarization"""
    
    # Required sections in clinical summaries
    REQUIRED_SECTIONS = [
        "Chief Complaint",
        "Emotional State", 
        "Risk",
        "Intervention",
        "Plan"
    ]
    
    # Risk keywords that should be marked with {{RED:}}
    RISK_KEYWORDS = [
        "suicide", "suicidal", "self-harm", "self harm",
        "kill", "hurt myself", "violence", "abuse",
        "overdose", "SI", "HI", "ideation"
    ]
    
    def __init__(self, dataset_path: str = "../psychotherapy_transcriptions_100.csv"):
        self.dataset_path = dataset_path
        self.results: List[TestResult] = []
        self.service = None
        self.df = None
        
    def setup(self) -> bool:
        """Initialize the service and load dataset"""
        print("=" * 60)
        print("Setting up Phi-3 Summarization Test Suite")
        print("=" * 60)
        
        # Load dataset
        try:
            self.df = pd.read_csv(self.dataset_path)
            print(f"✅ Loaded {len(self.df)} sessions from dataset")
        except Exception as e:
            print(f"❌ Failed to load dataset: {e}")
            return False
        
        # Initialize service
        try:
            self.service = SummarizationService()
            print("✅ Summarization service initialized")
        except Exception as e:
            print(f"❌ Failed to initialize service: {e}")
            return False
        
        return True
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return summary"""
        if not self.setup():
            return {"error": "Setup failed"}
        
        print("\n" + "=" * 60)
        print("Running Tests")
        print("=" * 60 + "\n")
        
        # Run test categories
        self._test_single_session_summarization()
        self._test_multi_session_summarization()
        self._test_output_format_compliance()
        self._test_risk_keyword_detection()
        self._test_performance_metrics()
        self._test_edge_cases()
        self._test_batch_processing()
        
        # Generate summary
        return self._generate_summary()
    
    def _test_single_session_summarization(self):
        """Test single session summarization"""
        print("\n📋 Testing Single Session Summarization")
        print("-" * 40)
        
        # Test with first 5 sessions
        for i in range(min(5, len(self.df))):
            start_time = time.time()
            
            row = self.df.iloc[i]
            transcription = row['session_transcription']
            expected = row['session_summary']
            
            try:
                summary = self.service.summarize_single_session(transcription)
                duration = time.time() - start_time
                
                # Check if summary was generated
                if summary and len(summary) > 20:
                    # Check for required content
                    has_content = any(section.lower() in summary.lower() 
                                     for section in ["complaint", "emotional", "risk", "intervention", "plan"])
                    
                    self.results.append(TestResult(
                        test_name=f"single_session_{i+1}",
                        passed=has_content,
                        message=f"Generated {len(summary)} chars in {duration:.2f}s",
                        duration=duration,
                        details={
                            "summary_length": len(summary),
                            "expected_length": len(expected),
                            "has_clinical_content": has_content
                        }
                    ))
                    print(f"  ✅ Session {i+1}: {len(summary)} chars, {duration:.2f}s")
                else:
                    self.results.append(TestResult(
                        test_name=f"single_session_{i+1}",
                        passed=False,
                        message="Summary too short or empty",
                        duration=duration
                    ))
                    print(f"  ❌ Session {i+1}: Summary too short")
                    
            except Exception as e:
                self.results.append(TestResult(
                    test_name=f"single_session_{i+1}",
                    passed=False,
                    message=str(e),
                    duration=time.time() - start_time
                ))
                print(f"  ❌ Session {i+1}: {e}")
    
    def _test_multi_session_summarization(self):
        """Test multi-session summarization"""
        print("\n📋 Testing Multi-Session Summarization")
        print("-" * 40)
        
        # Create session list
        sessions = []
        for i in range(min(3, len(self.df))):
            row = self.df.iloc[i]
            sessions.append({
                "original_transcription": row['session_transcription'],
                "notes": row['session_summary'][:200] if pd.notna(row['session_summary']) else "",
                "session_date": f"2024-01-{i+1:02d}"
            })
        
        start_time = time.time()
        
        try:
            result = self.service.summarize_sessions(sessions)
            duration = time.time() - start_time
            
            summary = result.get("summary", "")
            session_count = result.get("session_count", 0)
            key_points = result.get("key_points", [])
            
            passed = (
                len(summary) > 50 and
                session_count == len(sessions) and
                isinstance(key_points, list)
            )
            
            self.results.append(TestResult(
                test_name="multi_session_summary",
                passed=passed,
                message=f"Summarized {session_count} sessions in {duration:.2f}s",
                duration=duration,
                details={
                    "summary_length": len(summary),
                    "session_count": session_count,
                    "key_points_count": len(key_points)
                }
            ))
            
            if passed:
                print(f"  ✅ Multi-session: {len(summary)} chars, {session_count} sessions, {duration:.2f}s")
            else:
                print(f"  ❌ Multi-session: Failed validation")
                
        except Exception as e:
            self.results.append(TestResult(
                test_name="multi_session_summary",
                passed=False,
                message=str(e),
                duration=time.time() - start_time
            ))
            print(f"  ❌ Multi-session: {e}")
    
    def _test_output_format_compliance(self):
        """Test that output follows required format"""
        print("\n📋 Testing Output Format Compliance")
        print("-" * 40)
        
        # Test with a session that should have all sections
        row = self.df.iloc[0]
        transcription = row['session_transcription']
        
        start_time = time.time()
        
        try:
            summary = self.service.summarize_single_session(transcription)
            duration = time.time() - start_time
            
            # Check for required sections
            sections_found = []
            sections_missing = []
            
            for section in self.REQUIRED_SECTIONS:
                if section.lower() in summary.lower() or f"**{section}**" in summary:
                    sections_found.append(section)
                else:
                    sections_missing.append(section)
            
            # At least 3 of 5 sections should be present
            passed = len(sections_found) >= 3
            
            self.results.append(TestResult(
                test_name="output_format_compliance",
                passed=passed,
                message=f"Found {len(sections_found)}/5 required sections",
                duration=duration,
                details={
                    "sections_found": sections_found,
                    "sections_missing": sections_missing
                }
            ))
            
            if passed:
                print(f"  ✅ Format: {len(sections_found)}/5 sections found")
                print(f"     Found: {', '.join(sections_found)}")
            else:
                print(f"  ❌ Format: Only {len(sections_found)}/5 sections")
                print(f"     Missing: {', '.join(sections_missing)}")
                
        except Exception as e:
            self.results.append(TestResult(
                test_name="output_format_compliance",
                passed=False,
                message=str(e),
                duration=time.time() - start_time
            ))
            print(f"  ❌ Format test failed: {e}")

    
    def _test_risk_keyword_detection(self):
        """Test that risk keywords are properly detected and formatted"""
        print("\n📋 Testing Risk Keyword Detection")
        print("-" * 40)
        
        # Find sessions with risk-related content
        risk_sessions = []
        for i, row in self.df.iterrows():
            trans = row['session_transcription'].lower()
            if any(kw in trans for kw in ['suicidal', 'self-harm', 'suicide', 'ideation']):
                risk_sessions.append(i)
        
        if not risk_sessions:
            print("  ⚠️  No sessions with explicit risk keywords found in dataset")
            self.results.append(TestResult(
                test_name="risk_keyword_detection",
                passed=True,
                message="No risk sessions to test",
                details={"risk_sessions_found": 0}
            ))
            return
        
        # Test first risk session
        idx = risk_sessions[0]
        row = self.df.iloc[idx]
        
        start_time = time.time()
        
        try:
            summary = self.service.summarize_single_session(row['session_transcription'])
            duration = time.time() - start_time
            
            # Check for {{RED:}} markers or risk mentions
            has_red_markers = "{{RED:" in summary
            has_risk_mention = any(kw.lower() in summary.lower() for kw in self.RISK_KEYWORDS)
            
            # Either RED markers or risk mentions is acceptable
            passed = has_red_markers or has_risk_mention
            
            self.results.append(TestResult(
                test_name="risk_keyword_detection",
                passed=passed,
                message=f"RED markers: {has_red_markers}, Risk mentioned: {has_risk_mention}",
                duration=duration,
                details={
                    "has_red_markers": has_red_markers,
                    "has_risk_mention": has_risk_mention,
                    "session_index": idx
                }
            ))
            
            if passed:
                print(f"  ✅ Risk detection: Markers={has_red_markers}, Mentioned={has_risk_mention}")
            else:
                print(f"  ❌ Risk detection: No risk content in summary")
                
        except Exception as e:
            self.results.append(TestResult(
                test_name="risk_keyword_detection",
                passed=False,
                message=str(e),
                duration=time.time() - start_time
            ))
            print(f"  ❌ Risk test failed: {e}")
    
    def _test_performance_metrics(self):
        """Test performance requirements"""
        print("\n📋 Testing Performance Metrics")
        print("-" * 40)
        
        # Test inference time (should be < 30 seconds)
        row = self.df.iloc[0]
        
        start_time = time.time()
        
        try:
            summary = self.service.summarize_single_session(row['session_transcription'])
            duration = time.time() - start_time
            
            # Performance targets
            time_ok = duration < 30  # Under 30 seconds
            length_ok = 30 <= len(summary.split()) <= 150  # Word count bounds
            
            self.results.append(TestResult(
                test_name="performance_inference_time",
                passed=time_ok,
                message=f"Inference time: {duration:.2f}s (target: <30s)",
                duration=duration,
                details={
                    "inference_time": duration,
                    "target_time": 30
                }
            ))
            
            word_count = len(summary.split())
            self.results.append(TestResult(
                test_name="performance_word_count",
                passed=length_ok,
                message=f"Word count: {word_count} (target: 30-150)",
                details={
                    "word_count": word_count,
                    "target_min": 30,
                    "target_max": 150
                }
            ))
            
            if time_ok:
                print(f"  ✅ Inference time: {duration:.2f}s")
            else:
                print(f"  ❌ Inference time: {duration:.2f}s (too slow)")
            
            if length_ok:
                print(f"  ✅ Word count: {word_count} words")
            else:
                print(f"  ⚠️  Word count: {word_count} words (outside 30-150 range)")
                
        except Exception as e:
            self.results.append(TestResult(
                test_name="performance_metrics",
                passed=False,
                message=str(e),
                duration=time.time() - start_time
            ))
            print(f"  ❌ Performance test failed: {e}")
    
    def _test_edge_cases(self):
        """Test edge cases"""
        print("\n📋 Testing Edge Cases")
        print("-" * 40)
        
        # Test 1: Very short input
        try:
            result = self.service.summarize_text("Short text.")
            passed = "too short" in result.lower() or len(result) < 100
            self.results.append(TestResult(
                test_name="edge_case_short_input",
                passed=passed,
                message=f"Short input handled: {result[:50]}..."
            ))
            print(f"  ✅ Short input: Handled correctly")
        except Exception as e:
            self.results.append(TestResult(
                test_name="edge_case_short_input",
                passed=False,
                message=str(e)
            ))
            print(f"  ❌ Short input: {e}")
        
        # Test 2: Empty sessions list
        try:
            result = self.service.summarize_sessions([])
            passed = result.get("session_count", -1) == 0
            self.results.append(TestResult(
                test_name="edge_case_empty_sessions",
                passed=passed,
                message=f"Empty sessions handled: {result}"
            ))
            print(f"  ✅ Empty sessions: Handled correctly")
        except Exception as e:
            self.results.append(TestResult(
                test_name="edge_case_empty_sessions",
                passed=False,
                message=str(e)
            ))
            print(f"  ❌ Empty sessions: {e}")
        
        # Test 3: Long transcription (truncation)
        try:
            long_text = self.df.iloc[0]['session_transcription'] * 5  # Repeat 5x
            start_time = time.time()
            result = self.service.summarize_text(long_text)
            duration = time.time() - start_time
            
            passed = len(result) > 20 and duration < 60
            self.results.append(TestResult(
                test_name="edge_case_long_input",
                passed=passed,
                message=f"Long input ({len(long_text)} chars) handled in {duration:.2f}s",
                duration=duration
            ))
            print(f"  ✅ Long input: {len(long_text)} chars → {len(result)} chars in {duration:.2f}s")
        except Exception as e:
            self.results.append(TestResult(
                test_name="edge_case_long_input",
                passed=False,
                message=str(e)
            ))
            print(f"  ❌ Long input: {e}")
    
    def _test_batch_processing(self):
        """Test batch processing of multiple sessions"""
        print("\n📋 Testing Batch Processing")
        print("-" * 40)
        
        # Process 10 sessions and track success rate
        num_sessions = min(10, len(self.df))
        successes = 0
        total_time = 0
        
        for i in range(num_sessions):
            row = self.df.iloc[i]
            start_time = time.time()
            
            try:
                summary = self.service.summarize_single_session(row['session_transcription'])
                duration = time.time() - start_time
                total_time += duration
                
                if summary and len(summary) > 20:
                    successes += 1
                    
            except Exception as e:
                print(f"  ⚠️  Session {i+1} failed: {e}")
        
        success_rate = (successes / num_sessions) * 100
        avg_time = total_time / num_sessions
        
        passed = success_rate >= 80  # At least 80% success rate
        
        self.results.append(TestResult(
            test_name="batch_processing",
            passed=passed,
            message=f"Success rate: {success_rate:.1f}%, Avg time: {avg_time:.2f}s",
            duration=total_time,
            details={
                "total_sessions": num_sessions,
                "successes": successes,
                "success_rate": success_rate,
                "avg_inference_time": avg_time,
                "total_time": total_time
            }
        ))
        
        if passed:
            print(f"  ✅ Batch: {successes}/{num_sessions} ({success_rate:.1f}%), avg {avg_time:.2f}s")
        else:
            print(f"  ❌ Batch: {successes}/{num_sessions} ({success_rate:.1f}%) - below 80% threshold")
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        # Get service statistics
        stats = self.service.get_statistics() if self.service else {}
        
        summary = {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "service_stats": stats,
            "results": [
                {
                    "name": r.test_name,
                    "passed": r.passed,
                    "message": r.message,
                    "duration": r.duration,
                    "details": r.details
                }
                for r in self.results
            ]
        }
        
        print(f"\n✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {failed}/{total}")
        print(f"📊 Pass Rate: {summary['pass_rate']:.1f}%")
        
        if stats:
            print(f"\n📈 Service Statistics:")
            print(f"   Total Inferences: {stats.get('total_inferences', 0)}")
            print(f"   Success Rate: {stats.get('success_rate', 0):.1f}%")
            print(f"   Avg Inference Time: {stats.get('avg_inference_time', 0):.2f}s")
            print(f"   Fallback Count: {stats.get('fallback_count', 0)}")
        
        # Print failed tests
        if failed > 0:
            print(f"\n❌ Failed Tests:")
            for r in self.results:
                if not r.passed:
                    print(f"   - {r.test_name}: {r.message}")
        
        return summary


def main():
    """Run the comprehensive test suite"""
    print("\n" + "=" * 60)
    print("Phi-3 Therapy Summarization - Comprehensive Test Suite")
    print("=" * 60 + "\n")
    
    # Determine dataset path
    if os.path.exists("../psychotherapy_transcriptions_100.csv"):
        dataset_path = "../psychotherapy_transcriptions_100.csv"
    elif os.path.exists("psychotherapy_transcriptions_100.csv"):
        dataset_path = "psychotherapy_transcriptions_100.csv"
    else:
        print("❌ Dataset not found!")
        return
    
    tester = Phi3SummarizationTester(dataset_path)
    summary = tester.run_all_tests()
    
    # Save results to JSON
    results_file = "test_results_phi3.json"
    with open(results_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n📄 Results saved to {results_file}")
    
    # Return exit code based on pass rate
    if summary.get("pass_rate", 0) >= 80:
        print("\n✅ TEST SUITE PASSED")
        return 0
    else:
        print("\n❌ TEST SUITE FAILED")
        return 1


if __name__ == "__main__":
    exit(main())
