from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import os
import uuid
import base64

class UploadSignedDocWizard(models.TransientModel):
    _name = 'customisable_workflow_signature.upload_signed_doc_wizard'
    _description = 'wizard: upload signed document'

    def default_signed_document(self):
        return self.env['customisable_workflow_signature.work_signed_document'].browse(self._context.get('active_id'))

    result_document = fields.Binary(string='Document signé', required=True)
    document_filename = fields.Char("Nom du document signé")
    signed_document_id = fields.Many2one('customisable_workflow_signature.work_signed_document', string="Document", required=True, default=default_signed_document)
        
    def save(self):
        for record in self:
            self.env['ir.attachment'].sudo().create([{'name': record.document_filename,
                            'datas': record.result_document,
                            'res_model': record._name,
                            'res_id': record.id,
                            'public': True}])
            attachment = self.env['ir.attachment'].search([('res_model', '=', record._name),
                        ('res_id', '=', record.id)])
            if attachment.mimetype in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/pdf']:
                if attachment.mimetype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                    docx_path = attachment._full_path(attachment.store_fname)
                    file_name = os.path.basename(docx_path)
                    cmd = "soffice --headless --convert-to pdf --outdir /tmp " + docx_path
                    os.system(cmd)
                    f = open('/tmp/' + file_name + '.pdf', "rb")
                    pdf = f.read()
                    f.close()
                    record.signed_document_id.write({
                        'result_document_pdf': base64.b64encode(pdf),
                        'actor_user_id': self.env.user.id,
                        'action_date': fields.Datetime.now(),
                        'state': 'signed',
                        'signature_type': 'manual',
                    })
                else:
                    record.signed_document_id.write({
                        'result_document_pdf': record.result_document,
                        'actor_user_id': self.env.user.id,
                        'action_date': fields.Datetime.now(),
                        'state': 'signed',
                        'signature_type': 'manual',
                    })
            else:
                raise ValidationError(_("Le format du document n'est pas supporté!"))