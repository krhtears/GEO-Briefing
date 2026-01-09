import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import api_keys
from datetime import datetime

def send_briefing_email(recipients, results_data):
    """
    Sends an HTML email with the briefing results.
    results_data: List of tuples/dicts [(question, gemini_answer, gpt_answer), ...]
    """
    if not recipients:
        return "No recipients specified."
    
    sender_email = api_keys.EMAIL_SENDER
    sender_password = api_keys.EMAIL_PASSWORD.strip()
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['Subject'] = f"🌤️ Daily AI Briefing - {datetime.now().strftime('%Y-%m-%d')}"
    msg['To'] = ", ".join(recipients)
    
    # Build HTML Content
    html_content = """
    <html>
    <head>
        <style>
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; vertical-align: top; }
            th { background-color: #f2f2f2; }
            .question { font-weight: bold; background-color: #e8f4f8; }
            .gemini { color: #885df1; font-weight: bold; }
            .gpt { color: #10a37f; font-weight: bold; }
        </style>
    </head>
    <body>
        <h2>Daily AI Briefing Reports</h2>
        <table>
            <tr>
                <th width="20%">Question</th>
                <th width="40%">✨ Gemini 2.0</th>
                <th width="40%">🤖 GPT-4</th>
            </tr>
    """
    
    for item in results_data:
        # Markdown to HTML conversion is basic here; for complex markdown, a library like 'markdown' is needed.
        # But for plain text/basic usage, replacing newlines helps.
        q = item['question']
        gemini = item['gemini'].replace('\n', '<br>').replace('**', '')
        gpt = item['gpt'].replace('\n', '<br>').replace('**', '')
        
        html_content += f"""
            <tr>
                <td class="question">{q}</td>
                <td>{gemini}</td>
                <td>{gpt}</td>
            </tr>
        """
        
    html_content += """
        </table>
        <p style="font-size: 0.8em; color: #888;">김록훈님이 보냈습니다.</p>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        # Gmail SMTP Server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipients, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return f"failed to send email: {str(e)}"
