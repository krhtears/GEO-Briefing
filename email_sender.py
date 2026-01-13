import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import api_keys
from datetime import datetime
import stats_manager # Import for highlighting logic

def send_briefing_email(recipients, results_data, stats=None):
    """
    Sends an HTML email with the briefing results.
    results_data: List of tuples/dicts [(question, gemini_answer, gpt_answer), ...]
    stats: Dict {Brand: count}
    """
    if not recipients:
        return "No recipients specified."
    
    sender_email = api_keys.EMAIL_SENDER
    sender_password = api_keys.EMAIL_PASSWORD.strip()
    
    # Extract email addresses from recipient objects (dicts)
    # Handle legacy (list of strings) just in case
    target_emails = []
    for r in recipients:
        if isinstance(r, dict):
             target_emails.append(r['email'])
        else:
             target_emails.append(str(r))
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['Subject'] = f"유초중사업본부 GEO Briefing - {datetime.now().strftime('%Y-%m-%d')}"
    msg['To'] = ", ".join(target_emails)
    
    # Stats HTML
    stats_html = ""
    if stats:
        header_html = "".join([f"<th style='background-color: #E2EFDA; border: 1px solid black; padding: 5px; text-align: center;'>{brand}</th>" for brand in stats.keys()])
        # Total Counts
        count_html = "".join([f"<td style='border: 1px solid black; padding: 5px; text-align: center;'>{data['count']}</td>" for data in stats.values()])
        
        # Detail Breakdown
        detail_html = ""
        for data in stats.values():
            details = data['details']
            active_kws = [f"{k}: {v}" for k, v in details.items() if v > 0]
            if active_kws:
                cell_content = "<br>".join(active_kws)
            else:
                cell_content = "-"
            detail_html += f"<td style='border: 1px solid black; padding: 5px; text-align: center; font-size: 0.8em; color: #555;'>{cell_content}</td>"

        stats_html = f"""
        <div style="margin-bottom: 30px;">
            <h3>📊 키워드 언급 횟수</h3>
            <table style='width: 100%; border-collapse: collapse; border: 1px solid black;'>
                <tr>
                    <th style='background-color: #E2EFDA; border: 1px solid black; padding: 5px; text-align: center; width: 100px;'>구분</th>
                    {header_html}
                </tr>
                <tr>
                    <td style='border: 1px solid black; padding: 5px; text-align: center; font-weight: bold;'>언급횟수</td>
                    {count_html}
                </tr>
                <tr>
                    <td style='border: 1px solid black; padding: 5px; text-align: center; font-weight: bold;'>키워드 상세</td>
                    {detail_html}
                </tr>
            </table>
        </div>
        """

    # Build HTML Content
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ margin-bottom: 30px; border-bottom: 1px solid #ddd; padding-bottom: 20px; }}
            .question-box {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin-bottom: 15px; }}
            .question-text {{ font-size: 1.1em; font-weight: bold; color: #333; margin: 0; }}
            .model-section {{ margin-top: 15px; margin-bottom: 15px; }}
            .gemini-title {{ color: #885df1; font-weight: bold; font-size: 1.05em; margin-bottom: 5px; }}
            .gpt-title {{ color: #10a37f; font-weight: bold; font-size: 1.05em; margin-bottom: 5px; }}
            .content-box {{ background-color: #f9f9f9; padding: 10px; border-radius: 4px; border-left: 3px solid transparent; }}
            .gemini-content {{ border-left-color: #885df1; }}
            .gpt-content {{ border-left-color: #10a37f; }}
        </style>
    </head>
    <body>
        <h2>Daily AI Briefing Reports</h2>
        {stats_html}
    """
    
    import re
    
    def format_text(text):
        # 1. Replace '**text**' with '<b>text</b>'
        # Regular expression looks for **...** lazily
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        
        # 2. Remove single '*'
        text = text.replace('*', '')
        
        # 3. Handle newlines
        text = text.replace('\n', '<br>')
        
        text = text.replace('\n', '<br>')
        
        return text
    
    # Highlighting Logic
    all_competitors = stats_manager.load_competitors()
    
    def highlight_text(text, competitors):
        for comp in competitors:
            for kw in comp['keywords']:
                if kw in text:
                    # Inline style for email compatibility
                    text = text.replace(kw, f"<span style='background-color: #FFF2CC; padding: 0 2px;'>{kw}</span>")
        return text
    
    for item in results_data:
        q = item['question']
        
        # Apply formatting
        gemini = format_text(item['gemini'])
        gpt = format_text(item['gpt'])
        
        # Apply Highlighting (after formatting to preserve HTML tags if safe, actually before might be better?)
        # Let's do after, but ensuring we don't break the HTML we just added. 
        # Actually our highlight adds span tags, format_text adds b/br tags. They shouldn't conflict unless keywords overlap with tags which is unlikely.
        gemini = highlight_text(gemini, all_competitors)
        gpt = highlight_text(gpt, all_competitors)
        
        html_content += f"""
        <div class="container">
            <div class="question-box">
                <p class="question-text">❓ {q}</p>
            </div>
            
            <div class="model-section">
                <div class="gemini-title">✨ Gemini 2.0</div>
                <div class="content-box gemini-content">
                    {gemini}
                </div>
            </div>

            <div class="model-section">
                <div class="gpt-title">🤖 GPT-4o</div>
                <div class="content-box gpt-content">
                    {gpt}
                </div>
            </div>
        </div>
        """
        
    html_content += """
        <p style="font-size: 0.8em; color: #888; margin-top: 20px;">김록훈님이 보냈습니다.</p>
    </body>
    </html>
    """

    
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        # Gmail SMTP Server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, target_emails, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return f"failed to send email: {str(e)}"
