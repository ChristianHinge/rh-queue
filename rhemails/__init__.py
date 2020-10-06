import os
import smtplib
from email.message import EmailMessage
from string import Template
import pkg_resources


class EmailSender(object):
  def __init__(self, **kwargs):
    super().__init__()
    self.email_to = os.environ["SLURM_SCRIPT_EMAIL"]
    self.template_args = {
        "script": os.environ["SLURM_SCRIPT"],
        "args": os.environ["SLURM_SCRIPT_ARGS"],
        "node": os.environ["SLURM_JOB_NODELIST"],
        "script_name": os.environ["SLURM_JOB_NAME"],
        "job_id": os.environ["SLURM_JOBID"],
        "output_file": os.environ["SLURM_OUTPUT_FILE"]
    }
    self.email_from = "rhqueue@regionh.dk"
    self.get_template(kwargs.get("action"), self.template_args["script_name"])

  def send_email(self):
    email_content = Template(self.email_template.decode("utf-8"))
    email = EmailMessage()
    email.set_content(
        email_content.safe_substitute(self.template_args))
    email["Subject"] = self.email_subject
    email["To"] = self.email_to
    email["From"] = self.email_from
    try:
      with smtplib.SMTP("10.140.209.2", 25) as server:
        server.ehlo()
        server.sendmail(self.email_from, self.email_to, email.as_string())
    except Exception as e:
      print(e)

  def get_template(self, action, script_name):
    self.email_template = pkg_resources.resource_string(
        __name__, f'templates/email.{action}.tmp')
    self.email_subject = f"Script {script_name} {action}"
