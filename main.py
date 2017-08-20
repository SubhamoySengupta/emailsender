import email_module

SMTP_SERVER_ADDR, PORT = 'smtp.gmail.com', 587
SENDER_FILE = 'sender.txt'
RECIPENTS_FILE = 'recipients.txt'
MESSAGE_FILE = 'message.txt'
ATTACHMENTS_PATH = 'attachments'

sender, app_password = email_module.get_sender(SENDER_FILE)

recipients = email_module.get_resipients(RECIPENTS_FILE)

message_parts = email_module.read_message_file(MESSAGE_FILE)

message_parts['Recipients'] = recipients

message_parts['Sender'] = sender

message_parts['Attachments'] = ATTACHMENTS_PATH

server = email_module.mail_server(SMTP_SERVER_ADDR, PORT)

print sender
print app_password
server.login(sender, app_password)

server.set_message_format(message_parts)

server.sendmail(recipients, sender)

print 'All Done!'

server.server.quit()
