# real_encode_test.py
import os
from steganography_utils import encode_data

def test_real_encoding():
    """Test with actual audio file"""
    
    # Put a real WAV file in your project directory
    audio_path = "test_audio.wav"  # Replace with your actual audio file
    
    if not os.path.exists(audio_path):
        print(f"❌ Please add a real audio file named '{audio_path}' to test encoding")
        return False
    
    try:
        print("🔍 Testing real encoding...")
        
        key = encode_data(
            audio_path=audio_path,
            data="Hello World",
            output_path="real_test_output.wav",
            data_type="message",
            user_id=1,
            receiver_email="test@example.com"
        )
        
        print(f"✅ Encoding successful!")
        print(f"🔑 Key: {key.decode()}")
        print(f"📁 Output exists: {os.path.exists('real_test_output.wav')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Real encoding failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_real_encoding()
