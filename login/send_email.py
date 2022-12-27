import smtplib, logging
from email.message import EmailMessage
from flask import render_template, request
from app import app
import ssl
from exceptions import InternalServerError

logger = logging.getLogger(__name__)

def send_email(email, subject, content):

	ctx = ssl.create_default_context()
	login = app.config.get('MAIL_USERNAME')
	password = app.config.get('MAIL_PASSWORD')
	fromaddr = login
	toaddr = email

	email = EmailMessage()
	email['From'] = fromaddr
	email['To'] = toaddr

	if subject:
		email['Subject'] = subject
	if content:
		email.set_content(content(), subtype='html')

	# Send the message via local SMTP server.
	try:
		with smtplib.SMTP_SSL('smtp.gmail.com', port=465, context=ctx) as server:
			logger.info('login smtp')
			server.login(login, password)
			
			### catch exception and try to repeat sending message ###
			logger.info('try to send msg')
			server.send_message(email) 
			server.quit()
	except Exception as e:
		logger.error(f'{e}')
		raise InternalServerError