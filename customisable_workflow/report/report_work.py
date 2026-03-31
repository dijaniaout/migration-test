#-*- coding:utf-8 -*-
import base64
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.misc import formatLang
try:
    from docxtpl import RichText
except ImportError:
    pass
from datetime import datetime
import time
import logging
_logger = logging.getLogger(__name__)
class ReportWork(models.AbstractModel):
    _name = 'report.work.docx'
    _description = "Report work"

    def get_template_file(self, docid, data):
            return base64.b64decode(data['template'].document)
    
    def get_template_data(self, doc, data):
        # Do data formatting needed here
        signature = RichText('{{ signature }}', color="#FFFFFF", size=1)
        next_signature = RichText('{{r next_signature }}', color="#FFFFFF", size=1)
        return {
                'document': doc,
                'signature': signature,
                'next_signature': next_signature
            }
