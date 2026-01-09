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

# Recipient Management
RECIPIENTS_FILE = "recipients.json"

def load_recipients():
    if not os.path.exists(RECIPIENTS_FILE):
        return []
    with open(RECIPIENTS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_recipients(recipients):
    with open(RECIPIENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(recipients, f, ensure_ascii=False, indent=4)

def add_recipient(email):
    recipients = load_recipients()
    if email not in recipients:
        recipients.append(email)
        save_recipients(recipients)
        return True
    return False

def delete_recipient(index):
    recipients = load_recipients()
    if 0 <= index < len(recipients):
        recipients.pop(index)
        save_recipients(recipients)
        return True
    return False
