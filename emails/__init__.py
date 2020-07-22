import smtplib, ssl
from email.message import EmailMessage
from string import Template
from configparser import ConfigParser
import os
import pkg_resources
class EmailSender(object):
  def __init__(self, to, action, script=None):
    super().__init__()
    self.email_to = to
    self.template_args = {"script": script}
    self.email_from = "peter.nicolas.castenschiold.mcdaniel@regionh.dk"
    if action == "start":
      self.email_function = self._send_start_email
    elif action == "completed":
      self.email_function = self._send_done_email
    elif action == "failed":
      self.email_function = self._send_failed_email
    self.config = ConfigParser()
    self.config.read(pkg_resources.resource_filename(__package__, "config.ini"))
    self.password = self.config["Email"]["Password"]

  def send_email(self):
    self.email_function()
    self.email_content = Template(self.email_template)
    self.email = EmailMessage()
    self.email.set_content(self.email_content.safe_substitute(self.template_args))
    self.email["Subject"] = self.email_subject
    self.email["To"] = self.email_to
    self.email["From"] = self.email_from
    context = ssl.create_default_context()
    try:
      with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(self.email_from, self.password)
        server.sendmail(self.email_from, self.email_to, self.email.as_string())
    except Exception as e:
      print(e)

  def _send_start_email(self):
    self.email_template = "The script: $script has begun"
    self.email_subject = "Script Start"
    
  def _send_done_email(self):
    self.email_template = "The script $script has completed without errors"
    self.email_subject = "Script Completed"

  def _send_failed_email(self):
    self.email_template = "The script: $script has failed with errors"
    self.email_subject = "Script Failed"