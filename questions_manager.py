import json
import os

QUESTIONS_FILE = "questions.json"

def load_questions():
    if not os.path.exists(QUESTIONS_FILE):
        return []
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_questions(questions):
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=4)

def add_question(question_text):
    questions = load_questions()
    if question_text not in questions:
        questions.append(question_text)
        save_questions(questions)
        return True
    return False

def delete_question(index):
    questions = load_questions()
    if 0 <= index < len(questions):
        questions.pop(index)
        save_questions(questions)
        return True
    return False

def set_questions(new_questions_list):
    """
    Overwrites the current list of questions with a new list.
    Useful for restoring history.
    """
    save_questions(new_questions_list)
    return True

# Recipient Management
RECIPIENTS_FILE = "recipients.json"

def load_recipients():
    if not os.path.exists(RECIPIENTS_FILE):
        return [{"name": "김록훈", "email": "rhkim@megastudy.net"}]
    with open(RECIPIENTS_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            # Migration check: if list is strings, convert to dicts
            cleaned_data = []
            for item in data:
                if isinstance(item, str):
                    cleaned_data.append({"name": "No Name", "email": item})
                elif isinstance(item, dict):
                    cleaned_data.append(item)
            return cleaned_data
        except json.JSONDecodeError:
            return []

def save_recipients(recipients):
    with open(RECIPIENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(recipients, f, ensure_ascii=False, indent=4)

def add_recipient(name, email):
    recipients = load_recipients()
    # Check for duplicate email
    for r in recipients:
        if r['email'] == email:
            return False
            
    recipients.append({"name": name, "email": email})
    save_recipients(recipients)
    return True

def delete_recipient(index):
    recipients = load_recipients()
    if 0 <= index < len(recipients):
        recipients.pop(index)
        save_recipients(recipients)
        return True
    return False
