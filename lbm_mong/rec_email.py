from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def recommendation_email(document):
    fromaddr = 'locationbasedmessagingapp@gmail.com'
    toaddr = document.email
    username = 'locationbasedmessagingapp@gmail.com'
    password = 'imperial123'
    html_msg = """\
        <html>
            <head></head>
            <body>
                <p>Hello!</p>
                <p>%s %s has recommened you try the Location Based Messaging iOS App!<br>
                   Click on the link below to get started</p>
                <a href="www.google.com">Location Based Messaging</a>
                </p>
            </body>
        </html>
        """%(document.first_name, document.last_name)
    part2 = MIMEText(html_msg, 'html')
    msg1 = MIMEMultipart('alternative')
    msg1['Subject'] = "Join Location Based Messaging iOS App!"
    msg1['From'] = fromaddr
    msg1['To'] = toaddr
    msg1.attach(part2)
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    server.sendmail(fromaddr,toaddr,msg1.as_string())
    server.quit()
