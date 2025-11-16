#!/usr/bin/env python3
"""
Test NVIDIA Nemotron API connection

Usage:
    ./venv/bin/python scripts/test_nemotron.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from project root (override shell env)
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path, override=True)

def test_nemotron_connection():
    """Test basic connection to NVIDIA Nemotron API"""

    api_key = os.getenv('NVIDIA_API_KEY')
    base_url = os.getenv('NVIDIA_NIM_URL', 'https://integrate.api.nvidia.com/v1')

    if not api_key or api_key == 'your_api_key_here':
        print("❌ ERROR: NVIDIA_API_KEY not set in .env file")
        print("\nSteps to fix:")
        print("1. Go to https://build.nvidia.com/")
        print("2. Sign up/login and get your API key")
        print("3. Edit .env and set: NVIDIA_API_KEY=your_actual_key")
        return False

    print("🔧 Testing NVIDIA Nemotron connection...")
    print(f"   API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"   Base URL: {base_url}\n")

    try:
        # Initialize client
        client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )

        # Test with recommended models
        test_models = [
            "nvidia/nvidia-nemotron-nano-9b-v2",  # Fast
            "deepseek-ai/deepseek-v3.1",          # Smart
            "qwen/qwen3-next-80b-a3b-instruct",   # Multilingual
        ]

        print("📋 Available models to test:")
        for i, model in enumerate(test_models, 1):
            print(f"   {i}. {model}")

        # Try first available model
        print(f"\n📤 Testing with: {test_models[0]}...")

        response = client.chat.completions.create(
            model=test_models[0],
            messages=[{
                "role": "user",
                "content": "What is credit risk in finance? Answer in one sentence."
            }],
            temperature=0.2,
            max_tokens=100
        )

        answer = response.choices[0].message.content

        print("✅ SUCCESS! Nemotron is working!\n")
        print("Response:")
        print(f"   {answer}\n")

        # Show usage stats
        usage = response.usage
        print("Usage Stats:")
        print(f"   Prompt tokens: {usage.prompt_tokens}")
        print(f"   Completion tokens: {usage.completion_tokens}")
        print(f"   Total tokens: {usage.total_tokens}")

        return True

    except Exception as e:
        print(f"❌ ERROR: {str(e)}\n")
        print("Common issues:")
        print("- Invalid API key (check .env file)")
        print("- Rate limit exceeded (free tier has limits)")
        print("- Network connection problem")
        print("- Model name changed (check NVIDIA docs)")
        return False


def list_available_models():
    """List all available NVIDIA models"""

    api_key = os.getenv('NVIDIA_API_KEY')
    base_url = os.getenv('NVIDIA_NIM_URL')

    if not api_key or api_key == 'your_api_key_here':
        return

    try:
        client = OpenAI(base_url=base_url, api_key=api_key)

        print("\n" + "="*70)
        print("Available NVIDIA Models:")
        print("="*70)

        models = client.models.list()

        for model in models.data[:10]:  # Show first 10
            print(f"  • {model.id}")

        print(f"\n  (Showing 10 of {len(models.data)} available models)")
        print("="*70)

    except Exception as e:
        print(f"\nCouldn't list models: {e}")


if __name__ == "__main__":
    print("="*70)
    print("NVIDIA NEMOTRON API TEST")
    print("="*70 + "\n")

    success = test_nemotron_connection()

    if success:
        list_available_models()

        print("\n" + "="*70)
        print("✅ Ready to integrate Nemotron into FE-EKG!")
        print("="*70)
        print("\nNext steps:")
        print("1. Run: ./venv/bin/python scripts/integrate_nemotron.py")
        print("2. Or use NemotronScorer in your evolution methods")
    else:
        print("\n" + "="*70)
        print("❌ Fix the errors above and try again")
        print("="*70)
