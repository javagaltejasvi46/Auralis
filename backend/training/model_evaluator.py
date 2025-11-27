"""
Model Evaluator for Phi-3-Mini
Computes quality metrics on test set
"""
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import re
from typing import List, Dict
import json


class ModelEvaluator:
    """Evaluate model quality on test set"""
    
    def __init__(self):
        self.rouge_scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
        self.smoothing = SmoothingFunction()
        
    def compute_rouge_scores(self, predictions: List[str], references: List[str]) -> Dict[str, float]:
        """Compute ROUGE-L scores"""
        if len(predictions) != len(references):
            raise ValueError("Predictions and references must have same length")
        
        scores = []
        for pred, ref in zip(predictions, references):
            score = self.rouge_scorer.score(ref, pred)
            scores.append(score['rougeL'].fmeasure)
        
        avg_score = sum(scores) / len(scores)
        print(f"📊 ROUGE-L: {avg_score:.4f}")
        
        return {
            'rouge_l_mean': avg_score,
            'rouge_l_scores': scores
        }
    
    def compute_bleu_scores(self, predictions: List[str], references: List[str]) -> float:
        """Compute BLEU scores"""
        scores = []
        for pred, ref in zip(predictions, references):
            # Tokenize
            pred_tokens = pred.split()
            ref_tokens = [ref.split()]
            
            # Compute BLEU
            score = sentence_bleu(ref_tokens, pred_tokens, smoothing_function=self.smoothing.method1)
            scores.append(score)
        
        avg_score = sum(scores) / len(scores)
        print(f"📊 BLEU: {avg_score:.4f}")
        
        return avg_score
    
    def check_required_sections(self, summary: str) -> Dict[str, bool]:
        """Check if summary contains required sections"""
        required_sections = [
            'Chief Complaint',
            'Emotional State',
            'Risk',
            'Intervention',
            'Plan'
        ]
        
        sections_present = {}
        for section in required_sections:
            # Case-insensitive check
            sections_present[section] = section.lower() in summary.lower()
        
        return sections_present
    
    def check_risk_formatting(self, summary: str) -> Dict[str, any]:
        """Validate {{RED:text}} formatting for risk keywords"""
        risk_keywords = ['suicide', 'self-harm', 'kill', 'hurt myself', 'violence', 'abuse', 'overdose']
        
        # Find all {{RED:...}} markers
        red_markers = re.findall(r'\{\{RED:(.*?)\}\}', summary, re.IGNORECASE)
        
        # Check if risk keywords are properly formatted
        unformatted_keywords = []
        for keyword in risk_keywords:
            if keyword.lower() in summary.lower():
                # Check if it's in a RED marker
                found_in_marker = any(keyword.lower() in marker.lower() for marker in red_markers)
                if not found_in_marker:
                    unformatted_keywords.append(keyword)
        
        return {
            'red_markers_count': len(red_markers),
            'red_markers': red_markers,
            'unformatted_keywords': unformatted_keywords,
            'properly_formatted': len(unformatted_keywords) == 0
        }
    
    def check_word_count(self, summary: str) -> Dict[str, any]:
        """Check if summary meets word count requirements"""
        words = summary.split()
        word_count = len(words)
        
        in_range = 30 <= word_count <= 70
        extended_range = word_count <= 150
        
        return {
            'word_count': word_count,
            'in_target_range': in_range,
            'in_extended_range': extended_range
        }
    
    def evaluate_clinical_accuracy(self, predictions: List[str], references: List[str]) -> Dict[str, float]:
        """Evaluate clinical accuracy metrics"""
        section_completeness = []
        risk_formatting_accuracy = []
        word_count_compliance = []
        
        for pred in predictions:
            # Check sections
            sections = self.check_required_sections(pred)
            completeness = sum(sections.values()) / len(sections)
            section_completeness.append(completeness)
            
            # Check risk formatting
            risk_check = self.check_risk_formatting(pred)
            risk_formatting_accuracy.append(1.0 if risk_check['properly_formatted'] else 0.0)
            
            # Check word count
            wc_check = self.check_word_count(pred)
            word_count_compliance.append(1.0 if wc_check['in_target_range'] else 0.0)
        
        return {
            'section_completeness': sum(section_completeness) / len(section_completeness),
            'risk_formatting_accuracy': sum(risk_formatting_accuracy) / len(risk_formatting_accuracy),
            'word_count_compliance': sum(word_count_compliance) / len(word_count_compliance)
        }
    
    def generate_evaluation_report(self, predictions: List[str], references: List[str], output_file: str = "evaluation_report.json"):
        """Generate comprehensive evaluation report"""
        print("📊 Generating evaluation report...")
        
        # Compute all metrics
        rouge_scores = self.compute_rouge_scores(predictions, references)
        bleu_score = self.compute_bleu_scores(predictions, references)
        clinical_metrics = self.evaluate_clinical_accuracy(predictions, references)
        
        report = {
            'total_samples': len(predictions),
            'rouge_l_mean': rouge_scores['rouge_l_mean'],
            'bleu_score': bleu_score,
            'section_completeness': clinical_metrics['section_completeness'],
            'risk_formatting_accuracy': clinical_metrics['risk_formatting_accuracy'],
            'word_count_compliance': clinical_metrics['word_count_compliance'],
            'meets_target': rouge_scores['rouge_l_mean'] >= 0.40
        }
        
        # Save report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Report saved to {output_file}")
        print(f"\n📈 Summary:")
        print(f"  ROUGE-L: {report['rouge_l_mean']:.4f} {'✅' if report['meets_target'] else '❌'}")
        print(f"  BLEU: {report['bleu_score']:.4f}")
        print(f"  Section Completeness: {report['section_completeness']:.2%}")
        print(f"  Risk Formatting: {report['risk_formatting_accuracy']:.2%}")
        print(f"  Word Count Compliance: {report['word_count_compliance']:.2%}")
        
        return report


if __name__ == "__main__":
    # Test evaluator
    evaluator = ModelEvaluator()
    
    # Sample data
    predictions = [
        "**Chief Complaint:** Depression **Emotional State:** Sad **Risk:** {{RED:suicide}} ideation **Intervention:** CBT **Plan:** Weekly sessions"
    ]
    references = [
        "**Chief Complaint:** Major depression **Emotional State:** Depressed mood **Risk:** {{RED:suicide}} thoughts **Intervention:** Cognitive therapy **Plan:** Continue weekly"
    ]
    
    report = evaluator.generate_evaluation_report(predictions, references)
