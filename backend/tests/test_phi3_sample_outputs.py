"""
Sample Output Test for Phi-3 Therapy Summarization
Shows actual generated summaries for review
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from summarization_service_phi3 import SummarizationService


def show_sample_outputs():
    """Generate and display sample summaries for review"""
    
    print("=" * 70)
    print("Phi-3 Therapy Summarization - Sample Outputs")
    print("=" * 70)
    
    # Load dataset
    dataset_path = "../psychotherapy_transcriptions_100.csv"
    if not os.path.exists(dataset_path):
        dataset_path = "psychotherapy_transcriptions_100.csv"
    
    df = pd.read_csv(dataset_path)
    print(f"\n📊 Loaded {len(df)} sessions\n")
    
    # Initialize service
    service = SummarizationService()
    
    # Test 3 different sessions
    test_indices = [0, 5, 10]
    
    for idx in test_indices:
        if idx >= len(df):
            continue
            
        row = df.iloc[idx]
        transcription = row['session_transcription']
        expected = row['session_summary']
        
        print("=" * 70)
        print(f"SESSION {idx + 1}")
        print("=" * 70)
        
        print("\n📝 TRANSCRIPTION (first 500 chars):")
        print("-" * 40)
        print(transcription[:500] + "..." if len(transcription) > 500 else transcription)
        
        print("\n📋 EXPECTED SUMMARY:")
        print("-" * 40)
        print(expected)
        
        print("\n🤖 PHI-3 GENERATED SUMMARY:")
        print("-" * 40)
        
        summary = service.summarize_single_session(transcription)
        print(summary)
        
        print("\n📊 COMPARISON:")
        print(f"   Expected length: {len(expected)} chars, {len(expected.split())} words")
        print(f"   Generated length: {len(summary)} chars, {len(summary.split())} words")
        
        # Check for key elements
        has_chief = "chief complaint" in summary.lower()
        has_emotional = "emotional" in summary.lower()
        has_risk = "risk" in summary.lower()
        has_intervention = "intervention" in summary.lower()
        has_plan = "plan" in summary.lower()
        has_red_markers = "{{RED:" in summary
        
        print(f"\n   ✓ Chief Complaint: {'Yes' if has_chief else 'No'}")
        print(f"   ✓ Emotional State: {'Yes' if has_emotional else 'No'}")
        print(f"   ✓ Risk Assessment: {'Yes' if has_risk else 'No'}")
        print(f"   ✓ Intervention: {'Yes' if has_intervention else 'No'}")
        print(f"   ✓ Plan: {'Yes' if has_plan else 'No'}")
        print(f"   ✓ RED Markers: {'Yes' if has_red_markers else 'No'}")
        
        print("\n")
    
    # Test multi-session summary
    print("=" * 70)
    print("MULTI-SESSION SUMMARY (3 sessions)")
    print("=" * 70)
    
    sessions = []
    for i in range(3):
        row = df.iloc[i]
        sessions.append({
            "original_transcription": row['session_transcription'],
            "notes": row['session_summary'][:200],
            "session_date": f"2024-01-{i+1:02d}"
        })
    
    result = service.summarize_sessions(sessions)
    
    print("\n🤖 GENERATED MULTI-SESSION SUMMARY:")
    print("-" * 40)
    print(result.get("summary", "No summary"))
    
    print(f"\n📊 Session Count: {result.get('session_count', 0)}")
    print(f"📊 Key Points: {len(result.get('key_points', []))}")
    
    if result.get('key_points'):
        print("\n📌 Key Points:")
        for i, point in enumerate(result['key_points'], 1):
            print(f"   {i}. {point}")
    
    # Print service statistics
    stats = service.get_statistics()
    print("\n" + "=" * 70)
    print("SERVICE STATISTICS")
    print("=" * 70)
    print(f"   Total Inferences: {stats.get('total_inferences', 0)}")
    print(f"   Success Rate: {stats.get('success_rate', 0):.1f}%")
    print(f"   Avg Inference Time: {stats.get('avg_inference_time', 0):.2f}s")
    print(f"   Fallback Count: {stats.get('fallback_count', 0)}")
    
    print("\n✅ Sample output generation complete!")


if __name__ == "__main__":
    show_sample_outputs()
