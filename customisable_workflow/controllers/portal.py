# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
import base64
import logging
import mimetypes
from odoo.addons.portal.controllers.portal import  CustomerPortal

_logger = logging.getLogger(__name__)
class CustomisableWorkflowPortal(CustomerPortal):

    @http.route('''/my/given_document/<model("customisable_workflow.work_given_document"):given_document>''', auth='user', type='http', website=True)
    def get_given_document(self, given_document, download=False, **kw):
        filecontent = given_document.attachment and base64.b64decode(given_document.attachment) or b''
        filename = given_document.name
        mimetype, _ = mimetypes.guess_type(filename)

        if not mimetype:
            mimetype = 'application/octet-stream' 

        if download:
            content_disposition = f'attachment; filename="{filename}"'
        else:
            content_disposition = f'inline; filename="{filename}"'

        headers = [
            ('Content-Type', mimetype),
            ('Content-Disposition', content_disposition)
        ]

        return request.make_response(filecontent, headers=headers)