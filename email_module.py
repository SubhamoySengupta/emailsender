import smtplib
import re
import mimetypes
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from os import walk
from sys import exit


def get_sender(filename):
	f = open(filename, 'r')
	email, app_password = '', ''
	for line in f.readlines():
		if line[0] is '#':
			continue
		if 'email =' in line:
			email = line.split('=')[1].strip()
		if 'app_specific_password =' in line:
			app_password = line.split('=')[1].strip()
	return email, app_password


def get_resipients(filename):
	f = open(filename, 'r')
	recipients = []
	for line in f.readlines():
		if line[0] is '#':
			continue
		if re.match('[^@]+@[^@]+\.[^@]+', line):
			recipients.append(line.strip())
	return recipients


def read_message_file(filename):
	f = open(filename, 'r')
	msg = dict(Subject='', PlainText='', HTML='')
	for line in f.readlines():
		if '<Subject>' in line:
			current = 'Subject'
		elif '<PlainText>' in line:
			current = 'PlainText'
		elif '<HTML>' in line:
			current = 'HTML'
		else:
			msg[current] += line
	return msg


class mail_server():
	def __init__(self, SMTP_SERVER_ADDR, PORT):
		self.server = smtplib.SMTP(SMTP_SERVER_ADDR, PORT)
		self.server.starttls()
		self.server.ehlo()

	def login(self, sender, app_password):
		#try:
			code, resp = self.server.login(sender, app_password)
		#except:
		#	print 'An error occured, could not login'
		#	exit(1)

	def set_message_format(self, message_parts):
		try:
			self.msg = MIMEMultipart()
			self.msg['Subject'] = message_parts['Subject']
			self.msg['From'] = message_parts['Sender']
			self.msg['To'] = ','.join(message_parts['Recipients'])
			for (root, dirs, filenames) in walk(message_parts['Attachments']):
				if filenames:
					for files in filenames:
						ctype, encoding = mimetypes.guess_type(files)
						print 'Attachment->', files, 'Type->', ctype, 'Encoding->', encoding
						if ctype is None and encoding is None:
							ctype = 'application/octet-stream'
						maintype, subtype = ctype.split('/', 1)
						if maintype is 'text':
							fb = open(root + '/' + files, 'rb')
							attachment = MIMEText(fb.read(), _subtype=subtype)
						elif maintype is 'image':
							fb = open(root + '/' + files, 'rb')
							attachment = MIMEImage(fb.read(), _subtype=subtype)
							fb.close()
						elif maintype is 'audio':
							fb = open(root + '/' + files, 'rb')
							attachment = MIMEAudio(fb.read(), _subtype=subtype)
							fb.close()
						else:
							fb = open(root + '/' + files, 'rb')
							attachment = MIMEBase(maintype, subtype)
							attachment.set_payload(fb.read())
							encoders.encode_base64(attachment)
							fb.close()
						attachment.add_header('Content-Disposition', 'attachment', filename=files)
						self.msg.attach(attachment)
			if message_parts['PlainText'] != '':
				self.msg.attach(MIMEText(message_parts['PlainText'], 'plain'))
			if message_parts['HTML'] != '':
				self.msg.attach(MIMEText(message_parts['HTML'], 'html'))
			self.formatted_msg = self.msg.as_string()
		except:
			print 'An error occured,could not format message'
			exit(1)

	def sendmail(self, recipients, sender):
		self.server.sendmail(sender, ','.join(recipients), self.formatted_msg)
