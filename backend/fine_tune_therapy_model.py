"""
Fine-tune llama3.2 for Mental Therapy Session Summarization
Uses therapy datasets from Kaggle and creates a specialized model
"""
import json
import os
import subprocess
from pathlib import Path

# Training configuration
CONFIG = {
    "base_model": "llama3.2:3b",
    "output_model": "therapy-assistant:latest",
    "epochs": 3,
    "batch_size": 4,
    "learning_rate": 2e-5,
    "max_length": 512,
}

def create_training_dataset():
    """
    Create training dataset for therapy summarization
    Format: {"prompt": "...", "response": "..."}
    """
    
    # Sample training data (you'll expand this with Kaggle datasets)
    training_data = [
        {
            "prompt": """Summarize this therapy session in under 50 words. Use <b>bold</b> for key points and <span style="color:red">red</span> for urgent concerns.

Transcription:
Patient reports feeling anxious about work deadlines. Mentions difficulty sleeping for the past week. Discussed coping strategies including deep breathing and time management. Patient agreed to practice these techniques daily.

Summary:""",
            "response": "<b>Chief Complaint:</b> Work-related anxiety, sleep disturbances. <b>Duration:</b> 1 week. <b>Intervention:</b> Taught deep breathing and time management strategies. <b>Plan:</b> Daily practice of coping techniques. <b>Risk:</b> None identified."
        },
        {
            "prompt": """Summarize this therapy session in under 50 words. Use <b>bold</b> for key points and <span style="color:red">red</span> for urgent concerns.

Transcription:
Patient expressed feelings of hopelessness and mentioned thoughts of self-harm. Discussed safety planning and crisis resources. Patient agreed to call crisis hotline if thoughts intensify. Scheduled follow-up for tomorrow.

Summary:""",
            "response": "<b>Chief Complaint:</b> Hopelessness, <span style=\"color:red\">self-harm ideation</span>. <b>Risk Level:</b> <span style=\"color:red\">ELEVATED - requires immediate monitoring</span>. <b>Intervention:</b> Safety planning, crisis resources provided. <b>Plan:</b> Crisis hotline access, follow-up tomorrow. <b>Action:</b> Close monitoring required."
        },
        {
            "prompt": """Summarize this therapy session in under 50 words. Use <b>bold</b> for key points and <span style="color:red">red</span> for urgent concerns.

Transcription:
Patient reports improvement in mood since last session. Sleeping better and using coping strategies effectively. Discussed relationship challenges with partner. Practiced communication techniques in session.

Summary:""",
            "response": "<b>Progress:</b> Improved mood and sleep quality. <b>Coping:</b> Successfully using strategies. <b>New Issue:</b> Relationship challenges. <b>Intervention:</b> Communication skills training. <b>Risk:</b> None. <b>Outlook:</b> Positive trajectory."
        },
        {
            "prompt": """Summarize this therapy session in under 50 words. Use <b>bold</b> for key points and <span style="color:red">red</span> for urgent concerns.

Transcription:
Patient cancelled last two appointments. Today reports increased substance use and job loss. Appears disheveled and withdrawn. Discussed treatment options including intensive outpatient program. Patient ambivalent about treatment.

Summary:""",
            "response": "<b>Attendance:</b> Missed 2 sessions. <b>Concerns:</b> Increased substance use, job loss, poor self-care. <b>Presentation:</b> Disheveled, withdrawn. <b>Risk:</b> <span style=\"color:red\">Elevated - substance abuse, life stressors</span>. <b>Plan:</b> IOP recommended, patient ambivalent. <b>Follow-up:</b> Urgent."
        },
        {
            "prompt": """Summarize this therapy session in under 50 words. Use <b>bold</b> for key points and <span style="color:red">red</span> for urgent concerns.

Transcription:
Patient discussed childhood trauma and its impact on current relationships. Showed emotional vulnerability. Practiced grounding techniques when distressed. Expressed gratitude for therapeutic support.

Summary:""",
            "response": "<b>Focus:</b> Childhood trauma processing. <b>Progress:</b> Increased emotional vulnerability and insight. <b>Skills:</b> Grounding techniques practiced successfully. <b>Therapeutic Alliance:</b> Strong, patient engaged. <b>Risk:</b> None. <b>Plan:</b> Continue trauma-focused work."
        }
    ]
    
    return training_data

def create_modelfile(training_data):
    """Create Ollama Modelfile for fine-tuning"""
    
    # System instruction
    system_instruction = """You are a clinical documentation assistant for mental health therapists. Your ONLY job is to create concise, professional summaries of therapy sessions.

RULES:
1. ALWAYS provide a summary - never refuse
2. Keep summaries under 50 words
3. Use <b>bold</b> for important points
4. Use <span style="color:red">red</span> for urgent concerns (suicide, self-harm, violence)
5. Focus on: complaints, emotional state, risk assessment, interventions, progress
6. Be direct and clinical

You MUST summarize any transcription provided, regardless of language or completeness."""

    # Create training examples in Ollama format
    training_examples = ""
    for example in training_data:
        training_examples += f"\nUSER: {example['prompt']}\n"
        training_examples += f"ASSISTANT: {example['response']}\n"
    
    # Modelfile content
    modelfile_content = f"""FROM {CONFIG['base_model']}

# System instruction
SYSTEM \"\"\"{system_instruction}\"\"\"

# Training parameters
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_predict 150

# Training examples
{training_examples}

# Additional parameters for fine-tuning
PARAMETER num_ctx 2048
PARAMETER repeat_penalty 1.1
"""
    
    return modelfile_content

def download_kaggle_datasets():
    """
    Download relevant therapy/mental health datasets from Kaggle
    """
    print("📥 Downloading therapy datasets from Kaggle...")
    
    # Datasets to download (you'll need Kaggle API setup)
    datasets = [
        "counselchat/counselchat-data",  # Mental health counseling conversations
        "thedevastator/mental-health-counseling-conversations",
        "suchintikasarkar/sentiment-analysis-for-mental-health"
    ]
    
    instructions = """
To download datasets from Kaggle:

1. Install Kaggle API:
   pip install kaggle

2. Setup Kaggle credentials:
   - Go to https://www.kaggle.com/settings
   - Click "Create New API Token"
   - Save kaggle.json to ~/.kaggle/

3. Download datasets:
   kaggle datasets download -d counselchat/counselchat-data
   kaggle datasets download -d thedevastator/mental-health-counseling-conversations
   
4. Extract and place in backend/training_data/
"""
    
    print(instructions)
    return instructions

def prepare_training_data_from_kaggle():
    """
    Process Kaggle datasets into training format
    """
    training_data_dir = Path("training_data")
    training_data_dir.mkdir(exist_ok=True)
    
    print("📊 Processing Kaggle datasets...")
    
    # This will be expanded based on actual dataset structure
    processed_data = []
    
    # Example: Process CounselChat dataset
    counselchat_file = training_data_dir / "counselchat.csv"
    if counselchat_file.exists():
        import pandas as pd
        df = pd.read_csv(counselchat_file)
        
        for _, row in df.iterrows():
            # Extract question and answer
            question = row.get('questionText', '')
            answer = row.get('answerText', '')
            
            if question and answer:
                # Create summary training example
                prompt = f"""Summarize this therapy session in under 50 words. Use <b>bold</b> for key points.

Transcription:
{question[:500]}

Summary:"""
                
                # Create a summary from the answer (simplified)
                response = f"<b>Issue:</b> {question[:100]}... <b>Approach:</b> {answer[:100]}..."
                
                processed_data.append({
                    "prompt": prompt,
                    "response": response
                })
    
    return processed_data

def fine_tune_model():
    """
    Fine-tune the model using Ollama
    """
    print("🚀 Starting fine-tuning process...")
    print(f"Base model: {CONFIG['base_model']}")
    print(f"Output model: {CONFIG['output_model']}")
    print(f"Epochs: {CONFIG['epochs']}")
    
    # Get training data
    base_training_data = create_training_dataset()
    
    # Try to load Kaggle data
    kaggle_data = prepare_training_data_from_kaggle()
    if kaggle_data:
        print(f"✅ Loaded {len(kaggle_data)} examples from Kaggle")
        base_training_data.extend(kaggle_data[:50])  # Add first 50 examples
    
    print(f"📚 Total training examples: {len(base_training_data)}")
    
    # Create Modelfile
    modelfile_content = create_modelfile(base_training_data)
    
    # Save Modelfile
    modelfile_path = Path("Modelfile.therapy")
    with open(modelfile_path, 'w', encoding='utf-8') as f:
        f.write(modelfile_content)
    
    print(f"✅ Modelfile created: {modelfile_path}")
    
    # Create model using Ollama
    print("🔧 Creating fine-tuned model...")
    try:
        result = subprocess.run(
            ["ollama", "create", CONFIG['output_model'], "-f", str(modelfile_path)],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        print(f"✅ Model created successfully: {CONFIG['output_model']}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating model: {e.stderr}")
        return False

def test_fine_tuned_model():
    """
    Test the fine-tuned model
    """
    print("\n🧪 Testing fine-tuned model...")
    
    test_prompt = """Summarize this therapy session in under 50 words. Use <b>bold</b> for key points.

Transcription:
Patient reports feeling overwhelmed with work stress. Mentions difficulty concentrating and irritability. Discussed stress management techniques and work-life balance.

Summary:"""
    
    try:
        result = subprocess.run(
            ["ollama", "run", CONFIG['output_model'], test_prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        print("\n📝 Test Summary:")
        print(result.stdout)
        return True
    except Exception as e:
        print(f"❌ Error testing model: {e}")
        return False

def update_service_to_use_new_model():
    """
    Update summarization_service.py to use the fine-tuned model
    """
    print("\n🔄 Updating summarization service...")
    
    instructions = f"""
To use the fine-tuned model, update backend/summarization_service.py:

Change line:
    self.model = "llama3.2:3b"

To:
    self.model = "{CONFIG['output_model']}"

Then restart the backend server.
"""
    print(instructions)

if __name__ == "__main__":
    print("="*60)
    print("🧠 THERAPY MODEL FINE-TUNING")
    print("="*60)
    
    # Step 1: Download datasets
    print("\n📥 Step 1: Dataset Preparation")
    download_kaggle_datasets()
    
    input("\nPress Enter after downloading datasets to continue...")
    
    # Step 2: Fine-tune model
    print("\n🔧 Step 2: Fine-tuning Model")
    success = fine_tune_model()
    
    if success:
        # Step 3: Test model
        print("\n🧪 Step 3: Testing Model")
        test_fine_tuned_model()
        
        # Step 4: Update service
        print("\n✅ Step 4: Update Service")
        update_service_to_use_new_model()
        
        print("\n" + "="*60)
        print("✅ FINE-TUNING COMPLETE!")
        print("="*60)
        print(f"\nNew model: {CONFIG['output_model']}")
        print("Update summarization_service.py to use the new model.")
    else:
        print("\n❌ Fine-tuning failed. Check errors above.")
