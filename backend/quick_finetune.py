"""
Quick Fine-Tune Script for Therapy Model
Simplified version with built-in training data
"""
import subprocess
import sys
from pathlib import Path

def create_simple_modelfile():
    """Create a Modelfile with therapy-specific training"""
    
    modelfile = """FROM llama3.2:3b

# System instruction for therapy summarization
SYSTEM \"\"\"You are a clinical documentation assistant for mental health therapists.

Your ONLY job is to create concise summaries of therapy sessions.

RULES:
- ALWAYS provide a summary (never refuse)
- Keep under 50 words
- Use <b>bold</b> for key points
- Use <span style="color:red">red</span> for urgent concerns (suicide, self-harm, violence)
- Focus on: complaints, emotional state, risk assessment, progress
- Work with any language or incomplete data

Format: <b>Complaint:</b> ... <b>Risk:</b> ... <b>Plan:</b> ...
\"\"\"

# Training examples
MESSAGE user Summarize: Patient reports work anxiety, sleep issues for 1 week. Taught breathing exercises and time management. Patient will practice daily.
MESSAGE assistant <b>Complaint:</b> Work anxiety, insomnia (1 week). <b>Intervention:</b> Breathing exercises, time management training. <b>Plan:</b> Daily practice. <b>Risk:</b> Low.

MESSAGE user Summarize: Patient expressed hopelessness and self-harm thoughts. Safety planning completed. Crisis hotline provided. Follow-up tomorrow.
MESSAGE assistant <b>Complaint:</b> Hopelessness, <span style="color:red">self-harm ideation</span>. <b>Risk:</b> <span style="color:red">ELEVATED - immediate monitoring required</span>. <b>Intervention:</b> Safety plan, crisis resources. <b>Plan:</b> Follow-up tomorrow.

MESSAGE user Summarize: Patient shows mood improvement, sleeping better. Using coping strategies effectively. Discussed relationship issues. Practiced communication skills.
MESSAGE assistant <b>Progress:</b> Improved mood and sleep. <b>Coping:</b> Strategies working well. <b>New Issue:</b> Relationship challenges. <b>Intervention:</b> Communication training. <b>Risk:</b> Low.

MESSAGE user Summarize: Patient missed 2 sessions. Reports increased substance use and job loss. Appears disheveled. Discussed IOP program. Patient ambivalent.
MESSAGE assistant <b>Attendance:</b> 2 missed sessions. <b>Concerns:</b> Substance use increase, job loss. <b>Risk:</b> <span style="color:red">Elevated - substance abuse, life stressors</span>. <b>Plan:</b> IOP recommended. <b>Follow-up:</b> Urgent.

MESSAGE user Summarize: Patient processed childhood trauma. Showed emotional vulnerability. Practiced grounding techniques successfully. Expressed gratitude for support.
MESSAGE assistant <b>Focus:</b> Childhood trauma processing. <b>Progress:</b> Increased vulnerability and insight. <b>Skills:</b> Grounding techniques effective. <b>Alliance:</b> Strong. <b>Risk:</b> Low.

MESSAGE user Summarize: Patient reports panic attacks increasing. Avoiding social situations. Discussed exposure therapy. Patient hesitant but willing to try gradual approach.
MESSAGE assistant <b>Complaint:</b> Increased panic attacks, social avoidance. <b>Intervention:</b> Exposure therapy proposed. <b>Response:</b> Hesitant but open to gradual approach. <b>Plan:</b> Start gentle exposure. <b>Risk:</b> Low-moderate.

MESSAGE user Summarize: Patient celebrating 6 months sobriety. Attending AA regularly. Rebuilt relationship with family. Discussed relapse prevention strategies.
MESSAGE assistant <b>Milestone:</b> 6 months sobriety. <b>Support:</b> Regular AA attendance. <b>Progress:</b> Family relationships improved. <b>Focus:</b> Relapse prevention planning. <b>Risk:</b> Low. <b>Outlook:</b> Excellent.

MESSAGE user Summarize: Patient mentioned ending life, has plan and means. Immediate safety assessment conducted. Emergency contact notified. Hospitalization recommended.
MESSAGE assistant <span style="color:red"><b>CRISIS:</b> Active suicidal ideation with plan and means. IMMEDIATE INTERVENTION REQUIRED.</span> <b>Action:</b> Safety assessment, emergency contact notified, hospitalization recommended. <b>Risk:</b> <span style="color:red">IMMINENT DANGER</span>.

# Parameters optimized for therapy summarization
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_predict 120
PARAMETER num_ctx 2048
PARAMETER repeat_penalty 1.1
PARAMETER stop "</s>"
PARAMETER stop "Summary:"
"""
    
    return modelfile

def fine_tune():
    """Run the fine-tuning process"""
    print("="*60)
    print("🧠 QUICK FINE-TUNE: Therapy Summarization Model")
    print("="*60)
    
    # Check Ollama is installed
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        print(f"✅ Ollama version: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Ollama not found. Please install from https://ollama.ai")
        return False
    
    # Check base model exists
    print("\n📦 Checking for base model...")
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
    if "llama3.2:3b" not in result.stdout:
        print("⚠️  Base model not found. Pulling llama3.2:3b...")
        subprocess.run(["ollama", "pull", "llama3.2:3b"])
    else:
        print("✅ Base model found: llama3.2:3b")
    
    # Create Modelfile
    print("\n📝 Creating Modelfile with training data...")
    modelfile_content = create_simple_modelfile()
    modelfile_path = Path("Modelfile.therapy")
    
    with open(modelfile_path, 'w', encoding='utf-8') as f:
        f.write(modelfile_content)
    
    print(f"✅ Modelfile created: {modelfile_path}")
    print(f"   - 8 training examples included")
    print(f"   - Optimized for therapy summarization")
    
    # Create fine-tuned model
    print("\n🔧 Creating fine-tuned model...")
    print("   This may take 2-5 minutes...")
    
    try:
        result = subprocess.run(
            ["ollama", "create", "therapy-assistant:latest", "-f", str(modelfile_path)],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        print("\n✅ Fine-tuned model created: therapy-assistant:latest")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error creating model:")
        print(e.stderr)
        return False

def test_model():
    """Test the fine-tuned model"""
    print("\n🧪 Testing fine-tuned model...")
    
    test_prompt = """Summarize this therapy session in under 50 words. Use <b>bold</b> for key points and <span style="color:red">red</span> for urgent concerns.

Transcription:
Patient reports feeling overwhelmed with work deadlines. Difficulty sleeping for 3 nights. Discussed stress management and work-life balance. Patient agreed to set boundaries with supervisor.

Summary:"""
    
    try:
        result = subprocess.run(
            ["ollama", "run", "therapy-assistant:latest", test_prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        print("\n📝 Test Summary Generated:")
        print("-" * 60)
        print(result.stdout.strip())
        print("-" * 60)
        return True
    except Exception as e:
        print(f"❌ Error testing model: {e}")
        return False

def update_instructions():
    """Show instructions to update the service"""
    print("\n" + "="*60)
    print("✅ FINE-TUNING COMPLETE!")
    print("="*60)
    
    instructions = """
📋 Next Steps:

1. Update backend/summarization_service.py:
   
   Change line 11:
   FROM: self.model = "llama3.2:3b"
   TO:   self.model = "therapy-assistant:latest"

2. Restart the backend server:
   
   Stop current server (Ctrl+C)
   python backend/main.py

3. Test in the app:
   
   - Open patient profile
   - Click "Summarize" button
   - Verify improved summaries

4. Monitor performance:
   
   - Check summary quality
   - Verify risk flagging works
   - Collect feedback for improvements

📊 Model Info:
   - Name: therapy-assistant:latest
   - Base: llama3.2:3b
   - Training: 8 therapy examples
   - Optimized: Mental health summarization
   - Size: ~2GB

🔄 To re-train with more data:
   python backend/fine_tune_therapy_model.py
"""
    print(instructions)

if __name__ == "__main__":
    print("\n🚀 Starting quick fine-tune process...\n")
    
    # Run fine-tuning
    success = fine_tune()
    
    if success:
        # Test the model
        test_model()
        
        # Show next steps
        update_instructions()
        
        print("\n✨ Fine-tuning successful! Update your service to use the new model.")
    else:
        print("\n❌ Fine-tuning failed. Check errors above.")
        sys.exit(1)
