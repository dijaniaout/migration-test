
# -*- coding: utf-8 -*-
import base64
import unicodedata
import logging
import json

from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)

def clean(name): return name.replace('\x3c', '')

class Home(http.Controller):

    @http.route('/web/binary/upload_given_document_attachment', type='http', auth="user")
    def upload_attachment(self, model, id, ufile, callback=None):
        files = request.httprequest.files.getlist('ufile')
        Model = request.env['ir.attachment']
        out = """<script language="javascript" type="text/javascript">
                    var win = window.top.window;
                    win.jQuery(win).trigger(%s, %s);
                </script>"""
        args = []
        for ufile in files:

            filename = ufile.filename
            if request.httprequest.user_agent.browser == 'safari':
                # Safari sends NFD UTF-8 (where é is composed by 'e' and [accent])
                # we need to send it the same stuff, otherwise it'll fail
                filename = unicodedata.normalize('NFD', ufile.filename)

            try:
                attachment = Model.search([('res_model', '=', model), ('res_id', '=', int(id)), ('res_field', '=', 'attachment')])
                if attachment:
                    attachment.datas = base64.encodebytes(ufile.read())
                else: 
                    attachment = Model.create({
                        'name': filename,
                        'datas': base64.encodebytes(ufile.read()),
                        'res_model': model,
                        'res_id': int(id),
                        'res_field': 'attachment',
                        'public': True
                    })
                if attachment.mimetype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                    document = request.env[model].browse(int(id))
                    document.create_pdf_from_docx()

            except AccessError:
                args.append({'error': "Vous n'avez pas le droit de transmettre des fichiers ici."})
            except Exception:
                args.append({'error': "Une erreur technique est arrivée"})
                _logger.exception("Fail to upload attachment %s" % ufile.filename)
            else:
                args.append({
                    'filename': clean(filename),
                    'mimetype': ufile.content_type,
                    'id': attachment.id,
                    'size': attachment.file_size
                })
        return out % (json.dumps(clean(callback)), json.dumps(args)) if callback else json.dumps(args)