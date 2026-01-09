import google.generativeai as genai
from openai import OpenAI
import api_keys  # Import the keys from the file

# Configure Gemini
try:
    genai.configure(api_key=api_keys.GEMINI_API_KEY)
except Exception as e:
    print(f"Error configuring Gemini: {e}")

# Configure OpenAI
try:
    openai_client = OpenAI(api_key=api_keys.OPENAI_API_KEY)
except Exception as e:
    print(f"Error configuring OpenAI: {e}")
    openai_client = None

def ask_gemini(question):
    if not api_keys.GEMINI_API_KEY or "PASTE" in api_keys.GEMINI_API_KEY:
        return "⚠️ Gemini API Key not set. Please check api_keys.py."
    
    import time
    
    retries = 3
    base_delay = 2

    for attempt in range(retries):
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(question)
            return response.text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str and attempt < retries - 1:
                sleep_time = base_delay * (2 ** attempt)
                print(f"Gemini 429 error. Retrying in {sleep_time}s...")
                time.sleep(sleep_time)
                continue
            return f"❌ Error from Gemini: {error_str}"

def ask_gpt(question):
    if not api_keys.OPENAI_API_KEY or "PASTE" in api_keys.OPENAI_API_KEY:
        return "⚠️ OpenAI API Key not set. Please check api_keys.py."
    
    if not openai_client:
        return "⚠️ OpenAI client not initialized."

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o", # Or gpt-3.5-turbo depending on preference/cost
            messages=[
                {"role": "system", "content": "You are a helpful assistant providing daily briefings."},
                {"role": "user", "content": question}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error from OpenAI: {str(e)}"
