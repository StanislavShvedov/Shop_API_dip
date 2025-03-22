import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

smtp_user = "Ваша почта@yandex.ru"
smtp_password = "пароль"

def send_varif_mail(host_email: str, password: str, user_email: str, subj_tex: str, mail_text: str) -> None:
    """
        Отправляет письмо на указанный email.

        Аргументы:
            - host_email (str): Email адрес отправителя.
            - password (str): Пароль для SMTP-сервера отправителя.
            - user_email (str): Email адрес получателя.
            - subj_tex (str): Тема письма.
            - mail_text (str): Текст письма.

        Возвращает:
            - None

        Исключения:
            - Exception: Если возникает ошибка при отправке письма.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = host_email
        msg['To'] = user_email
        msg['Subject'] = "Наш интернет магазин" + subj_tex
        msg.attach(MIMEText(mail_text, 'plain'))

        server = smtplib.SMTP('smtp.yandex.ru', 587)
        server.starttls()
        server.login(host_email, password)
        server.sendmail(host_email, user_email, msg.as_string())
        server.quit()

        print(f"Письмо успешно отправлено на адрес {user_email}!")
    except Exception as e:
        print(f"Ошибка при отправке письма: {str(e)}")
