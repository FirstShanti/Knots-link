import smtplib, logging
from email.message import EmailMessage
from flask import render_template, request, flash
from app import app
import traceback
import ssl

logger = logging.getLogger(__name__)

def send_email(user, msg=None):
	
	ctx = ssl.create_default_context()
	login = app.config.get('MAIL_USERNAME')
	password = app.config.get('MAIL_PASSWORD')
	fromaddr = login
	toaddr = user.email

	email = EmailMessage()
	email['From'] = fromaddr
	email['To'] = toaddr

	if not msg:
		email['Subject'] = "authentication"
		url = f'{request.url_root}auth/?user={user.slug}&key={user.auth_key}'
		email.set_content(render_template('confirmed.html', url=url), subtype='html')
	else:
		email['Subject'] = "Good job!"
		email.set_content(render_template('post_to_email.html', post=msg), subtype='html')
	# Send the message via local SMTP server.
	with smtplib.SMTP_SSL('smtp.gmail.com', port=465, context=ctx) as server:
		try:
			logger.info('login smtp')
			server.login(login, password)
			
			### catch exception and try to repeat sending message ###
			logger.info('try to send msg')
			server.send_message(email) 
			server.quit()
		except Exception as e:
			logger.error(e)