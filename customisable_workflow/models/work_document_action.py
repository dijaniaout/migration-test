#-*- coding:utf-8 -*-
from odoo import models, fields, api,  _
import logging

_logger = logging.getLogger(__name__)

class WorkDocumentAction(models.AbstractModel):
    """
    Base model for handling actions on documents.
    """
    _name = 'customisable_workflow.work_document_action'
    _order = "res_id, id desc"
    _description = "Work document action"

    model = fields.Char('Related Document Model', index=True, required=True)
    res_id = fields.Many2oneReference('Related Document ID', index=True, model_field='model', required=True)
    step_id = fields.Many2one('customisable_workflow.step', string="Etape", required=True, ondelete='cascade')
    parent_model = fields.Char('Source model', index=True, required=True)
    parent_id = fields.Many2oneReference('Source document ID', index=True, model_field='parent_model', required=True)
    source_document = fields.Binary('Document à traiter')
    source_document_pdf = fields.Binary('Document à traiter (PDF)')
    result_document = fields.Binary('Document traité')
    result_document_pdf = fields.Binary('Document traité (PDF)')
    actor_user_id = fields.Many2one('res.users', string='Acteur')
    action_date = fields.Datetime(string="Date du traitement")
    current_user_can_act = fields.Boolean(string="L'utilisateur peut traiter", compute="_compute_current_user_can_act")
   
    def _compute_current_user_can_act(self):
        for record in self:
            if record.origin_id.allowed_group_ids:
                can_act = False
                for group in record.origin_id.allowed_group_ids:
                    for user in group.user_ids:
                        responsibility_transfer_id = user.responsibility_transfer_ids.filtered(lambda responsibility_transfer: responsibility_transfer.delegate_responsibility_id.id == self.env.user.id and fields.Date.today() >= responsibility_transfer.start_date and fields.Date.today() <= responsibility_transfer.end_date)
                        if self.env.user.id == user.id or responsibility_transfer_id:
                            can_act = True
                            break
            else:
                can_act = True
            record.current_user_can_act = can_act
    
    def reject(self):
        """
        Reject action
        """
        self.write({'actor_user_id':self.env.user.id,
                    'state': 'rejected',
                    'action_date': fields.Datetime.now()
                  })
