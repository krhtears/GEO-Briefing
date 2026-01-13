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

def ask_gemini(question, persona_prompts=None):
    if not api_keys.GEMINI_API_KEY or "PASTE" in api_keys.GEMINI_API_KEY:
        return "⚠️ Gemini API Key not set. Please check api_keys.py."
    
    import time
    
    # Construct System Prompt from Personas
    system_instruction = ""
    if persona_prompts:
        # persona_prompts is a list of strings
        if isinstance(persona_prompts, list):
            system_instruction = "\n\n".join(persona_prompts)
        elif isinstance(persona_prompts, str):
            system_instruction = persona_prompts
            
    # Combine with user question for Gemini (or use system_instruction if supported by library version)
    # The simple google.generativeai setup often takes system config in model init, 
    # but for simplicity/compatibility we often prepend it to the message.
    # However, 'gemini-2.0-flash' and newer models support system instructions better.
    # Let's prepend for maximum safety across library versions unless we change model init.
    
    full_prompt = question
    if system_instruction:
        # Changed from "System Instruction" to "Context about the User"
        full_prompt = f"Context about the User (Persona):\n{system_instruction}\n\nPlease answer the following question considering the user's persona above:\n{question}"

    retries = 3
    base_delay = 2

    for attempt in range(retries):
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str and attempt < retries - 1:
                sleep_time = base_delay * (2 ** attempt)
                print(f"Gemini 429 error. Retrying in {sleep_time}s...")
                time.sleep(sleep_time)
                continue
            return f"❌ Error from Gemini: {error_str}"

def ask_gpt(question, persona_prompts=None):
    if not api_keys.OPENAI_API_KEY or "PASTE" in api_keys.OPENAI_API_KEY:
        return "⚠️ OpenAI API Key not set. Please check api_keys.py."
    
    if not openai_client:
        return "⚠️ OpenAI client not initialized."

    # Construct System Prompt
    base_system = "You are a helpful assistant providing detailed and comprehensive daily briefings. Always provide rich, in-depth explanations rather than short summaries."
    if persona_prompts:
        if isinstance(persona_prompts, list):
            additional_prompts = "\n\n".join(persona_prompts)
            # Change wording to reflect User Persona
            base_system += f"\n\nThe user asking the question matches the following persona/profile:\n{additional_prompts}\n\nPlease tailor your answer to be relevant and helpful to this user's context. Maintain a high level of detail."
        elif isinstance(persona_prompts, str):
             base_system += f"\n\nThe user asking the question matches the following persona/profile:\n{persona_prompts}\n\nPlease tailor your answer to be relevant and helpful to this user's context. Maintain a high level of detail."

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            max_tokens=3000,
            messages=[
                {"role": "system", "content": base_system},
                {"role": "user", "content": question}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error from OpenAI: {str(e)}"
