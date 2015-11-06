"""bluesky.exporters.email"""

__author__      = "Joel Dubowy"
__copyright__   = "Copyright 2015, AirFire, PNW, USFS"

import json
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bluesky.exceptions import BlueSkyConfigurationError
from . import ExporterBase

__all__ = [
    'EmailExporter'
]

__version__ = "0.1.0"

class EmailExporter(ExporterBase):

    # TODO: should there indeed be a default sender?
    DEFAULT_SENDER = "blueskyexporter@gmail.com"
    DEFAULT_SUBJECT = "bluesky run output"
    DEFAULT_SMTP_SERVER = "localhost"
    DEFAULT_SMTP_PORT = 1025

    def __init__(self, extra_exports, **config):
        super(EmailExporter, self).__init__(extra_exports, **config)
        self._recipients = self.config('recipients')
        if not self._recipients:
            raise BlueSkyConfigurationError("Specifu")
        # TODO: make sure each email address is valid
        self._sender = self.config('sender') or self.DEFAULT_SENDER
        self._subject = self.config('subject') or self.DEFAULT_SUBJECT
        self._server = self.config('smtp_server') or self.DEFAULT_SMTP_SERVER
        self._port = int(self.config('smtp_port') or self.DEFAULT_SMTP_PORT)
        self._smtp_starttls = self.config('smtp_starttls', default=False)
        self._username = self.config('username')
        self._password = self.config('password')

        # TODO: read the following from config
         # - smtp_username -- no default
         # - smtp_password -- no default


    def export(self, fires_manager):
        logging.info('Sending Email to %s', self._recipients)
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self._sender
            msg['To'] = ', '.join(self._recipients)
            msg['Subject'] = self._subject

            # TODO: attach json dump of fires_amanager instead of making it
            #   the email's content ?
            content = json.dumps(fires_manager.dump())

            # TODO: attach other output files according to what's in
            #   self._extra_exports

            msg.attach(MIMEText(content, 'plain'))
            msg.attach(MIMEText(content, 'html'))

            logging.debug('Connecting to SMTP server %s %s', self._server, self._port)
            s = smtplib.SMTP(self._server, self._port)

            if self._smtp_starttls:
                logging.debug('Using STARTTLS')
                s.ehlo()
                s.starttls()
                s.ehlo()

            if self._username and self._password:
                logging.debug('Logging into SMTP server with u/p')
                s.login(self._username, self._password)

            s.sendmail(msg['from'], self._recipients, msg.as_string())
            s.quit()

        except smtplib.SMTPException, e:
            # Note: e.message is blank
            raise StatusNotificationError(str(e))
