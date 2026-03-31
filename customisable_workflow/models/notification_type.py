# -*- coding:utf-8 -*-
from odoo import api, fields, models, exceptions,_

class NotificationType(models.Model):
    _name = "banking_customisable_workflow.notification_type"
    _description = 'Types de notification'
   
    name = fields.Char("Titre", required=True)
    user_ids = fields.Many2many('res.users', string='Individus')
    group_ids = fields.Many2many('res.groups', string="Groupes")
    template_id = fields.Many2one('mail.template', "Template d'email", required=True)
    when_to_send = fields.Selection([('end', 'Fin'), ('beginning', 'Début')], default='beginning', string="Quand envoyer la notification")
    attachement_ids = fields.Many2many('customisable_workflow.document', 'customisable_workflow_notification_type_document_rel', string=u"Attachements")

    @api.constrains('user_ids','group_ids')
    def _check_groups_and_users(self):
        for record in self:
            if not (record.user_ids or record.group_ids):
                raise exceptions.ValidationError(_('Veuillez choisir au moins un individu ou un groupe.'))
            
    def get_template(self,work):
        template = self.template_id
        attachements = []
        for attachement_id in self.attachement_ids:
            work_doc_event = self.env['customisable_workflow_report.work_doc_event'].sudo().search([
                                            ('model', '=', work._name),
                                            ('res_id', '=', work.id),
                                            ('document_id', '=', attachement_id.id)], 
                                            order='date DESC', limit=1)
            attachement = work_doc_event.result_attachment_pdf or work_doc_event.result_attachment
            if attachement:
                attachement_copy = attachement.copy()
                attachement_copy.name = attachement_id.name
                attachements.append(attachement_copy.id)
        template.sudo().write({'attachment_ids': [(6, 0, attachements)]})
        return template

    def send_for_work(self, work):
        """
        Sends the  notification for the given work
        """
        template = self.get_template(work)
        if self.user_ids:
            for user in self.user_ids:
                email_values = {
                    'email_to': user.email,
                }
                template.send_mail(work.id, raise_exception=True, email_values=email_values)
        if self.group_ids:
            user_ids = self.env['res.users'].search([('group_ids', 'in', self.group_ids.mapped('id'))])
            email_values = {}
            email_list = []
            for user in user_ids:
                email_list.append(user.email)
            # Join the list into a single string of comma-separated emails
            email_to = ', '.join(email_list)
            email_values['email_to'] = email_to
            template.send_mail(work.id, raise_exception=True, email_values=email_values, force_send=False)
        template.sudo().attachment_ids.unlink()

    def send_for_work_to_creator(self, work):
        """
        For the given work, sends the notification to the creator
        """
        email_values = {
            'email_to': work.create_uid.login,
        }
        self.template_id.send_mail(work.id, raise_exception=True, email_values=email_values, force_send=False)