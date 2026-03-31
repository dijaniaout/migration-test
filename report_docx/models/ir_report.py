#-*- coding:utf-8 -*-

import requests
from odoo import _, api, fields, models
from odoo.exceptions import UserError
import os
try:
    from docxtpl import DocxTemplate, InlineImage, RichText
    from docx.opc.exceptions import PackageNotFoundError
    from jinja2.exceptions import UndefinedError
except ImportError:
    pass

import uuid
import logging
_logger = logging.getLogger(__name__)
class ReportAction(models.Model):
    _inherit = "ir.actions.report"

    report_type = fields.Selection(
        selection_add=[("docx", "DOCX")], ondelete={"docx": "set default"}
    )

    @api.model
    def _render_docx(self, docids, data):
        result = self.render_pdf_and_docx(docids, data)
        return result[data['template'].document_format_to_generate]

    @api.model
    def add_signature_to_report(self, template, signature_path):
        tmp_folder = "/tmp"
        file_uid = str(uuid.uuid4())
        full_docx_path = tmp_folder + '/' + file_uid + ".docx"
        converted_docx_path = tmp_folder + '/' + file_uid + "_converted.docx"
        pdf_path = tmp_folder + '/' + file_uid + "_converted.pdf"
        self._save_file(full_docx_path, template)
        doc = DocxTemplate(full_docx_path)
        try:
            signature = InlineImage(doc, image_descriptor=signature_path)
            next_signature = RichText('{{ signature }}', color="#FFFFFF", size=1)
            context = {'signature':signature , 'next_signature':next_signature}
            doc.render(context)
        except (PackageNotFoundError,KeyError):
            raise UserError("Impossible d'ouvrir le fichier modèle. Veuillez vérifier qu'il s'agit bien d'un document Word.")
        except UndefinedError as e:
            raise UserError(_("Le champ %s est inconnu. Veuillez vérifier le modèle %s.") % (str(e).split()[0],data['template'].name))
        doc.save(converted_docx_path)
        self._convert_docx_to_pdf(tmp_folder, converted_docx_path)
        f = open(pdf_path, "rb")
        pdf = f.read()
        f.close()
        d = open(converted_docx_path, "rb")
        docx = d.read()
        d.close()
        os.remove(full_docx_path)
        os.remove(converted_docx_path)
        os.remove(pdf_path)
        return {'pdf': (
                    pdf, "docx"
                ),
                'docx': (
                    docx, "docx"
                )}

    @api.model
    def render_pdf_and_docx(self, docids, data):
        report_model_name = "report.%s" % self.report_name
        report_model = self.env.get(report_model_name)
        if report_model is None:
            raise UserError(_("%s model was not found") % report_model_name)
        tmp_folder = "/tmp"
        file_uid = str(uuid.uuid4())
        full_docx_path = tmp_folder + '/' + file_uid + ".docx"
        converted_docx_path = tmp_folder + '/' + file_uid + "_converted.docx"
        pdf_path = tmp_folder + '/' + file_uid + "_converted.pdf"

        # FIXME: Handle printing multiple documents
        doc_id = docids[0]
        self._save_file(full_docx_path, report_model.sudo().get_template_file(doc_id.id, data))
        doc = DocxTemplate(full_docx_path)
        try:
            doc.render(report_model.sudo().get_template_data(doc_id, data))
        except PackageNotFoundError:
            raise UserError("Impossible d'ouvrir le fichier modèle. Veuillez vérifier qu'il s'agit bien d'un document Word.")
        except UndefinedError as e:
            raise UserError(_("Le champ %s est inconnu. Veuillez vérifier le modèle %s.") % (str(e).split()[0],data['template'].name))
        doc.save(converted_docx_path)
        # convert_using_gotenberg = self.env['ir.config_parameter'].sudo().get_param('ijayo.convert_using_gotenberg')
        # if convert_using_gotenberg == 'True':
        #     response = self._convert_docx_to_pdf_gotenberg(converted_docx_path)
        #     if response.status_code == 200:
        #         return (
        #             response.content, "docx"
        #         )
        #     else:     
        #         _logger.error(response)
        #         raise UserError(_("Unable to get pdf file. %r") % response)
        # else:
        self._convert_docx_to_pdf(tmp_folder, converted_docx_path)
        f = open(pdf_path, "rb")
        pdf = f.read()
        f.close()
        d = open(converted_docx_path, "rb")
        docx = d.read()
        d.close()
        os.remove(full_docx_path)
        os.remove(converted_docx_path)
        os.remove(pdf_path)
        return {'pdf': (
                    pdf, "docx"
                ),
                'docx': (
                    docx, "docx"
                )}
            
        
    def _convert_docx_to_pdf(self, tmp_folder_name, docx_path):
        output_path = tmp_folder_name

        cmd = "soffice --headless --convert-to pdf --outdir " + output_path \
            + " " + docx_path
        os.system(cmd)
        
    # def _convert_docx_to_pdf_gotenberg(self, docx_path=None):
    #     gotemberg_pdf_url = self.env['ir.config_parameter'].sudo().get_param('ijayo.gotenberg_pdf_url')
    #     if not gotemberg_pdf_url:
    #         raise UserError(_("Please fill in the url of the microservice related to gotenberg."))
    #     files = {'file': (docx_path, open(docx_path, 'rb'), 'multipart/form-data', {'Expires': '0'})}
    #     r = requests.post(gotemberg_pdf_url, files = files)
    #     return r

    @api.model
    def _get_report_from_name(self, report_name):
        res = super(ReportAction, self)._get_report_from_name(report_name)
        if res:
            return res
        report_obj = self.env["ir.actions.report"]
        qwebtypes = ["docx"]
        conditions = [
            ("report_type", "in", qwebtypes),
            ("report_name", "=", report_name),
        ]
        context = self.env["res.users"].context_get()
        return report_obj.with_context(**context).search(conditions, limit=1)

    def _save_file(self, folder_name, file):
        out_stream = open(folder_name, 'wb')
        try:
            out_stream.write(file)
        finally:
            out_stream.close()