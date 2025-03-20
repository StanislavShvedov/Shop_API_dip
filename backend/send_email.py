import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

smtp_user = "79158732788@yandex.ru"
smtp_password = "tlvfnrzphdjyhifx"

def send_varif_mail(host_email, password, user_email, subj_tex, mail_text):
    try:
        msg = MIMEMultipart()
        msg['From'] = host_email
        msg['To'] = user_email
        msg['Subject'] = "Наш интернет магазин" + subj_tex
        msg.attach(MIMEText(mail_text, 'plain'))

        server = smtplib.SMTP('smtp.yandex.ru', 587)
        server.starttls()
        server.login(host_email, password)
        server.sendmail(host_email, "svedovstanislav699@gmail.com", msg.as_string())
        server.quit()

        print("Письмо успешно отправлено!")
    except Exception as e:
        print(f"Ошибка при отправке письма: {str(e)}")
