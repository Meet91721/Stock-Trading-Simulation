import smtplib, ssl
from backend.config.secrets import EMAIL_APP_CODE, EMAIL_ID
from email.mime.text import MIMEText

smtp_server = "smtp.gmail.com"
port = 465  

message = """\
<html>
<style>
body {{
  background-color: linen;
  margin: auto;
  width: 50%;
  border: 1px solid black;
  padding: 10px;
  text-align: center;
}}

.verify-button {{
    direction: ltr;
    font: small/1.5 Arial,Helvetica,sans-serif;
    font-family: Helvetica,sans-serif;
    text-align: center;
    background-color: #7030c4;
    font-size: 16px;
    text-decoration: none;
    color: white;
    padding: 12px 32px 12px 32px;
}}


</style>
  <body>
    <p>
       <h1>Welcome to StockTrading Simulator</h1>
       <hr>
       <br>
       <p> Your login id: <a href="mailto:{email}" target="_blank">{email}</a> 
       <br><br>
       To activate your StockTrading account, please verify your email address.
       <br><br><br>
       <a class="verify-button" href="{verification_link}">Verify Email</a>
       <hr>
    </p>
  </body>
</html>"""


def send_email(receiver_email, verification_link):
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(EMAIL_ID, EMAIL_APP_CODE)
            msg = MIMEText(message.format(email=receiver_email, verification_link= verification_link), 'html')
            msg['Subject'] = 'Verify Your Email Address'
            msg['From'] = EMAIL_ID
            msg['To'] = receiver_email
            server.sendmail(EMAIL_ID, receiver_email, msg.as_string())
            return 0
    except Exception as error:
        print(f"Error sending email: {error}")
        return 1
