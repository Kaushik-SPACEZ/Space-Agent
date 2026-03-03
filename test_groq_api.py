"""
Test script to verify Groq API key is working
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def test_groq_api():
    """Test if Groq API key is valid and working"""
    
    print("=" * 60)
    print("Testing Groq API Key")
    print("=" * 60)
    
    # Get API key from .env
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "llama-3.3-70b-versatile")
    
    print(f"\n📋 Configuration:")
    print(f"   API Key: {api_key[:20]}...{api_key[-10:]}")
    print(f"   Model: {model}")
    print(f"   Endpoint: https://api.groq.com/openai/v1")
    
    try:
        # Initialize Groq client
        print("\n🔄 Initializing Groq client...")
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        print("✅ Client initialized successfully")
        
        # Test simple completion
        print(f"\n🧪 Testing API call with model: {model}")
        print("   Sending test message: 'Hello, how are you?'")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "Hello, how are you? Reply in one sentence."}
            ],
            temperature=0.1,
            max_tokens=50
        )
        
        # Get response
        reply = response.choices[0].message.content
        
        print("\n✅ API CALL SUCCESSFUL!")
        print(f"   Response: {reply}")
        print(f"   Model used: {response.model}")
        print(f"   Tokens used: {response.usage.total_tokens}")
        
        # Test JSON mode (required for our application)
        print("\n🧪 Testing JSON mode (required for Earth Agent)...")
        json_response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You extract data. Return JSON with keys: name, age"},
                {"role": "user", "content": "John is 25 years old"}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        json_reply = json_response.choices[0].message.content
        print("✅ JSON MODE WORKING!")
        print(f"   JSON Response: {json_reply}")
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\n✅ Your Groq API key is VALID and WORKING!")
        print("✅ The model supports JSON mode (required)")
        print("✅ Your Earth Observation Agent should work now!")
        print("\n💡 Next step: Restart your server with: python main.py")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED!")
        print("=" * 60)
        print(f"\n❌ Error: {str(e)}")
        print("\n🔍 Possible issues:")
        print("   1. Invalid API key")
        print("   2. API key expired")
        print("   3. Network connection issue")
        print("   4. Model name incorrect")
        print("\n💡 Solution:")
        print("   1. Go to https://console.groq.com")
        print("   2. Create a new API key")
        print("   3. Update the .env file")
        
        return False

if __name__ == "__main__":
    test_groq_api()