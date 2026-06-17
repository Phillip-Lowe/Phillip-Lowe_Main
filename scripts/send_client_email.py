#!/usr/bin/env python3
"""
SAOS Client Delivery Email
Generates and sends welcome email with credentials and setup instructions.

Usage:
    python3 send_client_email.py --client-id 123 --email "client@example.com" --agent-name "Percy"
"""

import os
import sys
import json
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


# SyStack brand colors (from TOOLS.md)
BRAND = {
    "navy": "#001a2d",
    "cyan": "#00a1db",
    "gray_light": "#f8fafc",
    "gray": "#e2e8f0",
    "text": "#1e293b"
}


def generate_welcome_email(client_data: dict) -> str:
    """Generate HTML welcome email for SAOS client."""
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to SAOS</title>
    <style>
        body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: {BRAND['gray_light']}; color: {BRAND['text']}; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; }}
        .header {{ background: linear-gradient(135deg, {BRAND['navy']} 0%, #003d66 100%); padding: 40px 30px; text-align: center; }}
        .header h1 {{ color: white; margin: 0; font-size: 28px; font-weight: 700; }}
        .header p {{ color: {BRAND['cyan']}; margin: 10px 0 0; font-size: 16px; }}
        .content {{ padding: 40px 30px; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: {BRAND['navy']}; font-size: 20px; margin: 0 0 15px; }}
        .info-box {{ background: {BRAND['gray']}; border-radius: 8px; padding: 20px; margin: 15px 0; }}
        .info-box code {{ background: white; padding: 3px 8px; border-radius: 4px; font-family: 'SF Mono', monospace; font-size: 14px; }}
        .button {{ display: inline-block; background: {BRAND['cyan']}; color: white; padding: 14px 32px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 15px 0; }}
        .steps {{ counter-reset: step; list-style: none; padding: 0; }}
        .steps li {{ counter-increment: step; margin-bottom: 20px; padding-left: 50px; position: relative; }}
        .steps li::before {{ content: counter(step); position: absolute; left: 0; top: 0; width: 32px; height: 32px; background: {BRAND['navy']}; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; }}
        .footer {{ background: {BRAND['navy']}; padding: 30px; text-align: center; color: #94a3b8; font-size: 14px; }}
        .footer a {{ color: {BRAND['cyan']}; text-decoration: none; }}
        .emoji {{ font-size: 24px; margin-right: 8px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛰️ Your SAOS Fleet is Live!</h1>
            <p>Welcome aboard, {client_data['client_name']}</p>
        </div>
        
        <div class="content">
            <div class="section">
                <h2><span class="emoji">👋</span>Hello {client_data['contact_name']}</h2>
                <p>Your SAOS Business Fleet has been deployed and is ready to work. Here's everything you need to get started.</p>
            </div>
            
            <div class="section">
                <h2><span class="emoji">🔗</span>Your Access Links</h2>
                <div class="info-box">
                    <p><strong>Tailscale URL:</strong><br>
                    <code>{client_data.get('tailscale_url', 'Coming soon')}</code></p>
                    
                    <p style="margin-top: 15px;"><strong>n8n Dashboard:</strong><br>
                    <code>http://{client_data.get('vps_ip', 'PENDING')}:5678</code></p>
                    
                    <p style="margin-top: 15px;"><strong>Agent Dashboard:</strong><br>
                    <code>http://{client_data.get('vps_ip', 'PENDING')}:8080</code></p>
                </div>
            </div>
            
            <div class="section">
                <h2><span class="emoji">🚀</span>Getting Started</h2>
                <ol class="steps">
                    <li><strong>Install Tailscale</strong> on your devices
                        <br><a href="https://tailscale.com/download">Download Tailscale</a></li>
                    
                    <li><strong>Accept the invite</strong> we'll send to your email</li>
                    
                    <li><strong>Access your agent</strong> at the Tailscale URL above</li>
                    
                    <li><strong>Start automating</strong> — your agent is ready to help!</li>
                </ol>
            </div>
            
            <div class="section">
                <h2><span class="emoji">🤖</span>Meet Your Agent: {client_data['agent_name']}</h2>
                <p>Your agent is powered by local AI — your data never leaves your infrastructure. It's already configured with your business context and ready to:</p>
                <ul>
                    <li>Handle booking and scheduling</li>
                    <li>Process invoices automatically</li>
                    <li>Monitor systems 24/7</li>
                    <li>Learn your preferences over time</li>
                </ul>
            </div>
            
            <div class="section" style="text-align: center; margin-top: 40px;">
                <a href="{client_data.get('tailscale_url', '#')}" class="button">Access Your Dashboard</a>
            </div>
            
            <div class="section">
                <h2><span class="emoji">📞</span>Need Help?</h2>
                <p>Reply to this email or call/text <strong>(501) 274-6231</strong> anytime.</p>
                <p style="margin-top: 10px; font-size: 14px; color: #64748b;">
                    Support hours: Monday–Friday, 9 AM – 6 PM CST<br>
                    Emergency: Available 24/7 for critical issues
                </p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>SyStack</strong> — Automation for Small Business</p>
            <p style="margin-top: 10px;">
                <a href="https://systack.net">systack.net</a> • 
                <a href="mailto:support@systack.net">support@systack.net</a>
            </p>
            <p style="margin-top: 20px; font-size: 12px;">
                Deployed: {client_data.get('deployed_at', datetime.now().strftime('%B %d, %Y'))}<br>
                Tier: {client_data.get('tier', 'Business').title()} Fleet
            </p>
        </div>
    </div>
</body>
</html>"""


def send_email_smtp(to_email: str, subject: str, html_body: str, 
                   from_email: str = "support@systack.net",
                   smtp_host: str = None, smtp_user: str = None, smtp_pass: str = None) -> bool:
    """Send email via SMTP."""
    
    smtp_host = smtp_host or os.environ.get("SMTP_HOST", "smtp.sendgrid.net")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = smtp_user or os.environ.get("SMTP_USER")
    smtp_pass = smtp_pass or os.environ.get("SMTP_PASS")
    
    if not smtp_user or not smtp_pass:
        print("⚠️  SMTP credentials not configured")
        print("   Set SMTP_USER and SMTP_PASS environment variables")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"SyStack Support <{from_email}>"
        msg['To'] = to_email
        
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def save_email_to_file(client_data: dict, output_dir: str = "/tmp/saos-emails"):
    """Save email HTML to file for review."""
    os.makedirs(output_dir, exist_ok=True)
    
    html = generate_welcome_email(client_data)
    filename = f"{output_dir}/welcome-{client_data['client_id']}.html"
    
    with open(filename, 'w') as f:
        f.write(html)
    
    print(f"💾 Email saved to: {filename}")
    return filename


def main():
    parser = argparse.ArgumentParser(description="Send SAOS client welcome email")
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--client-name", default="Your Business")
    parser.add_argument("--contact-name", default="There")
    parser.add_argument("--agent-name", default="Your Agent")
    parser.add_argument("--tier", default="business")
    parser.add_argument("--tailscale-url", default="")
    parser.add_argument("--vps-ip", default="PENDING")
    parser.add_argument("--test-mode", action="store_true", help="Save to file instead of sending")
    parser.add_argument("--send", action="store_true", help="Actually send email via SMTP")
    
    args = parser.parse_args()
    
    client_data = {
        "client_id": args.client_id,
        "client_name": args.client_name,
        "contact_name": args.contact_name,
        "agent_name": args.agent_name,
        "tier": args.tier,
        "tailscale_url": args.tailscale_url,
        "vps_ip": args.vps_ip,
        "deployed_at": datetime.now().strftime("%B %d, %Y")
    }
    
    # Generate email
    html = generate_welcome_email(client_data)
    
    if args.test_mode:
        # Save to file for review
        filename = save_email_to_file(client_data)
        print(f"🧪 TEST MODE: Email saved to {filename}")
        print(f"   Client: {args.client_name} ({args.email})")
        print(f"   Agent: {args.agent_name}")
        return
    
    if args.send:
        # Send via SMTP
        subject = f"🛰️ Your SAOS Fleet is Live — Welcome {args.contact_name}!"
        success = send_email_smtp(args.email, subject, html)
        
        if success:
            print(f"✅ Welcome email sent to {args.email}")
        else:
            print(f"❌ Failed to send email to {args.email}")
            # Save to file as fallback
            save_email_to_file(client_data)
    else:
        print("📧 Email generated. Use --send to send via SMTP or --test-mode to save to file.")
        print(f"   To: {args.email}")
        print(f"   Subject: 🛰️ Your SAOS Fleet is Live — Welcome {args.contact_name}!")


if __name__ == "__main__":
    main()
