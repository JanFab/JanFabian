from email.mime.text import MIMEText
import smtplib

def send_email(email, height, average_height, count):
    from_email="srnka.les@gmail.com"
    from_password="fabianovci"
    to_email=email

    subject="Údaje o výške'"
    message="Dobrý deň, zasielame Vám údaje o vašej výške <strong>%s</strong>. Priemerná výška respondentov je <strong>%s</strong> čo je vypočítané z celkového počtu <strong>%s</strong>. Prajem pekný zvyšok dňa." % (height, average_height, count)

    msg=MIMEText(message, 'html')
    msg['Subject']=subject
    msg['To'] = to_email
    msg['From'] = from_email

    gmail=smtplib.SMTP('smtp.gmail.com', 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(from_email, from_password)
    gmail.send_message(msg)