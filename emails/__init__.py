import smtplib, ssl
from email.message import EmailMessage
from string import Template
import pkg_resources


class EmailSender(object):
  def __init__(self, **kwargs):
    super().__init__()
    self.email_to = kwargs.get("email", "")
    self.template_args = {
        "script": kwargs.get("script", ""),
        "args": ' '.join(kwargs.get("args", []))
    }
    self.email_from = "rhqueue@regionh.dk"
    self.get_template(kwargs.get("action"))

  def send_email(self):
    self.email_content = Template(self.email_template.decode("utf-8"))
    self.email = EmailMessage()
    self.email.set_content(
        self.email_content.safe_substitute(self.template_args))
    self.email["Subject"] = self.email_subject
    self.email["To"] = self.email_to
    self.email["From"] = self.email_from
    try:
      with smtplib.SMTP("10.140.209.2", 25) as server:
        server.ehlo()
        server.sendmail(self.email_from, self.email_to, self.email.as_string())
    except Exception as e:
      print(e)

  def get_template(self, action):
    self.email_template = pkg_resources.resource_string(
        __name__, f'templates/email.{action}.tmp')
    self.email_subject = f"Script {action}"
