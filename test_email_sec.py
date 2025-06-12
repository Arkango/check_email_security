import smtplib
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_authenticated_email(smtp_server, port, sender_email, recipient_email, subject, body, username, password):
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(username, password)
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        return "Authenticated email sent successfully"
    except Exception as e:
        return f"Failed to send authenticated email: {e}"

def send_unauthenticated_email(smtp_server, port, sender_email, recipient_email, subject, body):
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        return "Unauthenticated email sent successfully"
    except Exception as e:
        return f"Failed to send unauthenticated email: {e}"
    
def send_spoofed_email_auth(smtp_server, port, recipient_email, subject, body,username, password):
    try:
        spoofed_sender = f"spoofed@{recipient_email.split('@')[1]}"
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(username, password)
        msg = MIMEMultipart()
        msg['From'] = spoofed_sender
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        server.sendmail(spoofed_sender, recipient_email, msg.as_string())
        server.quit()
        return "Spoofed email sent successfully"
    except Exception as e:
        return f"Failed to send spoofed email: {e}"

def send_spoofed_email(smtp_server, port, recipient_email, subject, body):
    try:
        spoofed_sender = f"spoofed@{recipient_email.split('@')[1]}"
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        msg = MIMEMultipart()
        msg['From'] = spoofed_sender
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        server.sendmail(spoofed_sender, recipient_email, msg.as_string())
        server.quit()
        return "Spoofed email sent successfully"
    except Exception as e:
        return f"Failed to send spoofed email: {e}"

def send_invalid_credentials_email(smtp_server, port, sender_email, recipient_email, subject, body):
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login("invalid_user", "invalid_password")
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        return "Email sent with invalid credentials (unexpected)"
    except Exception as e:
        return f"Failed to send email with invalid credentials: {e}"
    
def send_invalid_credentials_email_only_pass(smtp_server, port, sender_email, recipient_email, subject, body,username):
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(username, "invalid_password")
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        return "Email sent with invalid credentials (unexpected)"
    except Exception as e:
        return f"Failed to send email with invalid credentials: {e}"

def send_open_relay_email(smtp_server, port, sender_email, recipient_email, subject, body):
    try:
        server = smtplib.SMTP(smtp_server, port)
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        return "Email sent through open relay (unexpected)"
    except Exception as e:
        return f"Failed to send email through open relay: {e}"

def run_tests():
    with open('real_smtp_configurations.csv', mode='r') as file:
        reader = csv.DictReader(file)
        with open('smtp_results.csv', mode='w', newline='') as results_file:
            fieldnames = ['Test Title', 'Result', 'Log File']
            writer = csv.DictWriter(results_file, fieldnames=fieldnames)
            writer.writeheader()
            for i,row in enumerate(reader):
                smtp_server = row['Server']
                port = row['Port']
                sender_email = row['Sender']
                recipient_email = row['Recipient']
                subject = row['Subject']
                body = row['Body']
                username = row['Username']
                password = row['Password']



                tests = [
                    ("Authenticated Email", send_authenticated_email, [smtp_server, port, sender_email, recipient_email, subject, body, username, password]),
                    ("Unauthenticated Email", send_unauthenticated_email, [smtp_server, port, sender_email, recipient_email, subject, body]),
                    ("Spoofed Email", send_spoofed_email, [smtp_server, port, recipient_email, subject, body]),
                    ("Spoofed Email Auth", send_spoofed_email_auth, [smtp_server, port, recipient_email, subject, body,username,password]),
                    ("Invalid Credentials Email", send_invalid_credentials_email, [smtp_server, port, sender_email, recipient_email, subject, body]),
                    ("Invalid Credentials Email Only Pass", send_invalid_credentials_email_only_pass, [smtp_server, port, sender_email, recipient_email, subject, body,username]),
                    ("Open Relay Email", send_open_relay_email, [smtp_server, port, sender_email, recipient_email, subject, body])
                ]

                for test_name, test_func, test_args in tests:
                    result = test_func(*test_args)
                    log_file_name = f"{i}_{smtp_server}_{port}_{test_name.replace(' ', '_')}.txt"
                    with open(log_file_name, mode='w') as log_file:
                        log_file.write(result)
                    writer.writerow({'Test Title': f"{i} {smtp_server} {port} - {test_name}", 'Result': result, 'Log File': log_file_name})

if __name__ == "__main__":
    run_tests()

