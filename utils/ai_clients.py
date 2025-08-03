import os
import google.generativeai as genai

def get_gemini_client():
    """
    Initialize and return a Gemini model client.
    
    Returns:
        google.generativeai.GenerativeModel: Configured Gemini model
        
    Raises:
        KeyError: If GEMINI_API_KEY environment variable is not set
        Exception: If API key configuration fails
    """
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise KeyError("GEMINI_API_KEY environment variable is required")
    
    try:
        genai.configure(api_key=api_key)
        model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        return genai.GenerativeModel(model_name)
    except Exception as e:
        raise Exception(f"Failed to configure Gemini client: {e}")