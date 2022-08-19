import smtplib

# # Import the email modules we'll need
# from email.message import EmailMessage

# msg = EmailMessage()
# msg.set_content('hola hola hola')

# # me == the sender's email address
# # you == the recipient's email address
# msg['Subject'] = f'The contents of asdasd'
# msg['From'] = 'jaimeusc@protonmail.com'
# msg['To'] = 'jaimeusc@protonmail.com'

# # Send the message via our own SMTP server.
# s = smtplib.SMTP('localhost')
# s.send_message(msg)
# s.quit()

sendfrom = 'NachoJaimez007@gmail.com'
sendto = 'jaimeusc@protonmail.com'
server = smtplib.SMTP('smtp.gmail.com', 587)
psw = 'xxxx' #TODO: implement Github secrets here

server.starttls()

server.login(sendfrom,)

# server.sendemail(sendto, sendto, 'the rsms is too high')

print('mail sent')
