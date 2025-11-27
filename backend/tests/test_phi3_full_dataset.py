"""
Full Dataset Test for Phi-3 Therapy Summarization
Tests all 100 sessions and generates a quality report
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import time
import json
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class SessionResult:
    """Result for a single session"""
    session_idx: int
    success: bool
    inference_time: float
    summary_length: int
    word_count: int
    has_chief_complaint: bool
    has_emotional_state: bool
    has_risk: bool
    has_intervention: bool
    has_plan: bool
    has_red_markers: bool
    error: str = ""


def analyze_summary(summary: str) -> Dict[str, bool]:
    """Analyze summary for required sections"""
    summary_lower = summary.lower()
    return {
        "has_chief_complaint": "chief complaint" in summary_lower or "**chief" in summary_lower,
        "has_emotional_state": "emotional" in summary_lower,
        "has_risk": "risk" in summary_lower,
        "has_intervention": "intervention" in summary_lower,
        "has_plan": "plan" in summary_lower,
        "has_red_markers": "{{RED:" in summary
    }


def run_full_dataset_test(num_sessions: int = 20):
    """Run test on specified number of sessions"""
    
    print("=" * 70)
    print(f"Phi-3 Full Dataset Test ({num_sessions} sessions)")
    print("=" * 70)
    
    # Load dataset
    dataset_path = "../psychotherapy_transcriptions_100.csv"
    if not os.path.exists(dataset_path):
        dataset_path = "psychotherapy_transcriptions_100.csv"
    
    df = pd.read_csv(dataset_path)
    print(f"\n📊 Loaded {len(df)} sessions from dataset")
    print(f"📊 Testing {num_sessions} sessions\n")
    
    # Initialize service
    from summarization_service_phi3 import SummarizationService
    service = SummarizationService()
    
    results: List[SessionResult] = []
    total_start = time.time()
    
    for i in range(min(num_sessions, len(df))):
        row = df.iloc[i]
        transcription = row['session_transcription']
        
        print(f"Processing session {i+1}/{num_sessions}...", end=" ")
        
        start_time = time.time()
        
        try:
            summary = service.summarize_single_session(transcription)
            duration = time.time() - start_time
            
            analysis = analyze_summary(summary)
            
            result = SessionResult(
                session_idx=i,
                success=True,
                inference_time=duration,
                summary_length=len(summary),
                word_count=len(summary.split()),
                **analysis
            )
            
            print(f"✅ {duration:.2f}s, {len(summary)} chars")
            
        except Exception as e:
            duration = time.time() - start_time
            result = SessionResult(
                session_idx=i,
                success=False,
                inference_time=duration,
                summary_length=0,
                word_count=0,
                has_chief_complaint=False,
                has_emotional_state=False,
                has_risk=False,
                has_intervention=False,
                has_plan=False,
                has_red_markers=False,
                error=str(e)
            )
            print(f"❌ {e}")
        
        results.append(result)
    
    total_time = time.time() - total_start
    
    # Generate report
    print("\n" + "=" * 70)
    print("Test Report")
    print("=" * 70)
    
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    print(f"\n📊 Overall Results:")
    print(f"   Total Sessions: {len(results)}")
    print(f"   Successful: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"   Failed: {len(failed)} ({len(failed)/len(results)*100:.1f}%)")
    print(f"   Total Time: {total_time:.2f}s")
    
    if successful:
        avg_time = sum(r.inference_time for r in successful) / len(successful)
        avg_length = sum(r.summary_length for r in successful) / len(successful)
        avg_words = sum(r.word_count for r in successful) / len(successful)
        
        print(f"\n⏱️  Performance:")
        print(f"   Avg Inference Time: {avg_time:.2f}s")
        print(f"   Avg Summary Length: {avg_length:.0f} chars")
        print(f"   Avg Word Count: {avg_words:.0f} words")
        
        # Section coverage
        chief_count = sum(1 for r in successful if r.has_chief_complaint)
        emotional_count = sum(1 for r in successful if r.has_emotional_state)
        risk_count = sum(1 for r in successful if r.has_risk)
        intervention_count = sum(1 for r in successful if r.has_intervention)
        plan_count = sum(1 for r in successful if r.has_plan)
        red_count = sum(1 for r in successful if r.has_red_markers)
        
        print(f"\n📋 Section Coverage:")
        print(f"   Chief Complaint: {chief_count}/{len(successful)} ({chief_count/len(successful)*100:.1f}%)")
        print(f"   Emotional State: {emotional_count}/{len(successful)} ({emotional_count/len(successful)*100:.1f}%)")
        print(f"   Risk Assessment: {risk_count}/{len(successful)} ({risk_count/len(successful)*100:.1f}%)")
        print(f"   Intervention: {intervention_count}/{len(successful)} ({intervention_count/len(successful)*100:.1f}%)")
        print(f"   Plan: {plan_count}/{len(successful)} ({plan_count/len(successful)*100:.1f}%)")
        print(f"   RED Markers: {red_count}/{len(successful)} ({red_count/len(successful)*100:.1f}%)")
    
    if failed:
        print(f"\n❌ Failed Sessions:")
        for r in failed:
            print(f"   Session {r.session_idx}: {r.error}")
    
    # Save results
    report = {
        "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_sessions": len(results),
        "successful": len(successful),
        "failed": len(failed),
        "success_rate": len(successful) / len(results) * 100,
        "total_time": total_time,
        "avg_inference_time": sum(r.inference_time for r in successful) / len(successful) if successful else 0,
        "section_coverage": {
            "chief_complaint": chief_count / len(successful) * 100 if successful else 0,
            "emotional_state": emotional_count / len(successful) * 100 if successful else 0,
            "risk": risk_count / len(successful) * 100 if successful else 0,
            "intervention": intervention_count / len(successful) * 100 if successful else 0,
            "plan": plan_count / len(successful) * 100 if successful else 0,
            "red_markers": red_count / len(successful) * 100 if successful else 0
        },
        "results": [asdict(r) for r in results]
    }
    
    with open("test_results_full_dataset.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Results saved to test_results_full_dataset.json")
    
    # Final verdict
    print("\n" + "=" * 70)
    if len(successful) / len(results) >= 0.95:
        print("✅ TEST PASSED - 95%+ success rate achieved")
    else:
        print("❌ TEST FAILED - Below 95% success rate")
    print("=" * 70)
    
    return report


if __name__ == "__main__":
    # Test 20 sessions by default (can be changed)
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--sessions", type=int, default=20, help="Number of sessions to test")
    args = parser.parse_args()
    
    run_full_dataset_test(args.sessions)
