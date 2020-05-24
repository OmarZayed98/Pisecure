# Author: Omar Zayed and Vanessa Lama

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
import os
import sys

# THIRD PARTY IMPORTS
import cv2

# gmail must be set to allow less secure apps, so you can send emails.
# fill the email credentials information needed (starting line 38 till 41)


def send_mail(frame):

    #getting the log file where the last date and time is saved.
    log_file = 'logs/email.log'
	
	#  read the log file and Check if the last sound played was within 10 seconds.
    if os.path.isfile(log_file): # First check if file exists.
        with open(log_file, 'r') as f:
            date = f.read()
            date_to_datetime = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")

            if datetime.now() < date_to_datetime + timedelta(minutes=1):
                return

    # Update the email log.
    with open(log_file, 'w') as f:
        f.write(str(datetime.now()))

    # Create the jpg out of the frame sent from the other python file.
    cv2.imwrite("intrude.jpg", frame)

    #enter the information below in order to allow it to send an email
    gmail_email = ''
    gmail_password = ''
    recipient_email = ''
    email_body = ''

    msg = MIMEMultipart()
    msg['From'] = gmail_email
    msg['To'] = recipient_email
    msg['Subject'] = "Someone is at Home!"
    msg.attach(MIMEText(email_body))

	#getting the picture and attaching it 
	
    file = 'intrude.jpg'
    filename = 'intrude.jpg'
    attachment = open(file, "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(part)

	#sending the email
    mail_server = smtplib.SMTP('smtp.gmail.com', 587)
    mail_server.ehlo()
    mail_server.starttls()
    mail_server.ehlo()
    mail_server.login(gmail_email, gmail_password)
    mail_server.sendmail(gmail_email, recipient_email, msg.as_string())
    mail_server.close()