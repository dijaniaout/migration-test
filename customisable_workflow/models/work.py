#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from lxml import etree
import json
import logging
import time
from datetime import datetime
import re
from odoo.tools.safe_eval import safe_eval
_logger = logging.getLogger(__name__)
IN_TREATMENT_LABEL = "En traitement"

class Work(models.AbstractModel):
    _name = 'customisable_workflow.work'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Work"

    name = fields.Char(string="Nom", required=True)
    workflow_id = fields.Many2one('customisable_workflow.workflow', string="Processus", required=True, index=True)
    current_step_id = fields.Many2one('customisable_workflow.step', string="Etape actuelle", index=True, tracking=True,
        copy=False, ondelete='restrict', domain="[('workflow_id', '=', workflow_id)]")
    current_step_description = fields.Text(related="current_step_id.description", string="Description de l'étape courante")
    has_documents_to_give = fields.Boolean(string="Has documents to give", related="workflow_id.has_documents_to_give")
    has_documents_to_generate = fields.Boolean(string="Has documents to generate", related="workflow_id.has_documents_to_generate")
    given_document_ids = fields.One2many('customisable_workflow.work_given_document', 'res_id', string="Documents fournis")
    generated_document_ids = fields.One2many('customisable_workflow.work_generated_document', 'res_id', string="Documents générés")
    current_user_can_act = fields.Boolean(string="L'utilisateur peut valider", compute="_compute_current_user_can_act")
    previous_step_id = fields.Many2one('customisable_workflow.step', string=u'Etape précédente', compute="_get_previous_step")
    transition_history_ids = fields.One2many('customisable_workflow.transition_history', 'res_id', string='Historique étapes effectuées')
    done_step_ids = fields.Many2many("customisable_workflow.step", compute='_compute_done_steps')
    has_a_justification = fields.Boolean(string="A une justification", compute='_compute_justification')
    justification = fields.Text(string="Justification", compute='_compute_justification')
    date_of_transition_to_the_current_stage = fields.Date("Date de transition", compute="_compute_date_of_transition_to_the_current_stage", store=True)
    visible_step = fields.Char(string=u'Étape visible', compute="_compute_visible_step")
    is_not_editable = fields.Boolean("N'est pas modifiable?", compute='_compute_not_editable_for_group')
    allowed_given_document_ids = fields.Many2many('customisable_workflow.work_given_document', string="Documents à fournir autorisés à l'utilisateur courant", compute="compute_allowed_given_document_ids")
    state = fields.Selection([], string="State")
    type = fields.Selection(
         selection=[
             ('process', 'Etape'),
             ('subprocess', 'Sous-processus')
         ],
         string="Débuter par",
         default='process'
     )
    subprocess_id = fields.Many2one('customisable_workflow.workflow', string='Sous-processus de début', domain=[('type', '=', 'subprocess')])
    dunning_ids = fields.One2many("customisable_workflow.dunning", related='workflow_id.dunning_ids', string=u"Relances", tracking=True)
    case_manager_id = fields.Many2one('res.users', string="Responsable du dossier")

    def _cron_dunning(self):
        record_ids = self.search([('workflow_id.dunning_ids', '!=', False)])
        sign_map = {
            'more_than': '>',
            'less_than': '<',
            'more_than_or_equal_to': '>=',
            'less_than_or_equal_to': '<=',
            'is_equal_to': '=='
        }
        for record in self:
            user_id = record.case_manager_id
            for dunning in record.dunning_ids:
                number_dunning_rule = len(dunning.dunning_rule_ids)
                if number_dunning_rule > 1 and dunning.cumulative:
                    cumulative = 0
                    for dunning_rule in dunning.dunning_rule_ids:
                        field_name = self.env['ir.model.fields'].sudo().search([('id', '=', dunning_rule.field_id.id)]).name
                        value = getattr(record, field_name)
                        sign = sign_map.get(dunning_rule.sign)
                        if dunning_rule.field_id.ttype in ['float', 'integer']:
                            condition = f"{value} {sign} {dunning_rule.number}"
                            if eval(condition):
                                cumulative += 1
                        if dunning_rule.field_id.ttype == 'boolean':
                            condition = f"{value} {sign} {dunning_rule.boolean_value}"
                            if eval(condition):
                                cumulative += 1
                    if cumulative == number_dunning_rule:
                        self.send_dunning(dunning, user_id)
                else:
                    for dunning_rule in dunning.dunning_rule_ids:
                        field_name = self.env['ir.model.fields'].sudo().search([('id', '=', dunning_rule.field_id.id)]).name
                        value = getattr(record, field_name)
                        sign = sign_map.get(dunning_rule.sign)
                        if dunning_rule.field_id.ttype in ['float', 'integer']:
                            condition = f"{value} {sign} {dunning_rule.number}"
                            if eval(condition):
                                self.send_dunning(dunning, user_id)
                                break
                        if dunning_rule.field_id.ttype == 'boolean':
                            condition = f"{value} {sign} {dunning_rule.boolean_value}"
                            if eval(condition):
                                self.send_dunning(dunning, user_id)
                                break

    def send_dunning(self, dunning, user_id):
        if user_id.login:
            email_to = user_id.login
            context = {'current_date': datetime.today().strftime('%d/%m/%Y')}
            for notification_type in dunning.notification_ids:
                template = notification_type.template_id
                
                body = template._render_field('body_html', self.ids, compute_lang=True)[self.id]
                subject = template._render_field('subject', self.ids, compute_lang=True)[self.id]
                
                # Log the message in chatter
                self.message_post(
                    body=body,
                    subject=subject,
                    message_type='notification',
                    subtype_id=self.env.ref('mail.mt_note').id,
                    author_id=user_id.partner_id.id,
                    partner_ids=[user_id.partner_id.id]
                )
                
                # Send the actual email
                email_values = {
                    'email_to': email_to,
                }
                template.with_context(context).send_mail(self.id, email_values=email_values, force_send=False)

    def compute_allowed_given_document_ids(self):
        for record in self:
            user_groups = self.env.user.group_ids.ids
            record.allowed_given_document_ids = record.given_document_ids.filtered(lambda given_document: any(group.id in user_groups for group in given_document.document_id.allowed_group_ids))      

    def write(self, vals):
        res = super(Work,self).write(vals)
        if 'transitioning' not in self.env.context or not self.env.context['transitioning']:
            self.with_context(transitioning=True)._execute_automatic_transition()
        self._cron_dunning()
        return res

    def _compute_done_steps(self):
        for record in self:
            steps = []
            for transition_history in record.transition_history_ids:
                if transition_history.step_to_id:
                    steps.append(transition_history.step_to_id.id)
            record.done_step_ids = steps

    def _compute_not_editable_for_group(self):
        for record in self:
            is_not_editable = False
            if record.current_step_id.readonly_group_ids:
                users = self.env['res.users']
                for group in record.current_step_id.readonly_group_ids:
                    users |= group.user_ids
                for user in users:
                    if self.env.user.id == user.id:
                        is_not_editable = True
                        break
            record.is_not_editable = is_not_editable
    
    def _execute_automatic_transition(self):
        for work in self:
            _logger.info("Handling transiton for work %s", work.name)
            if work.current_step_id:
                previous_step = work.current_step_id
            try:
                for step_decision in work.current_step_id.step_decision_ids:
                    if step_decision.transition_rule_id:
                        _logger.info("Found trasition rule %s", step_decision.transition_rule_id.name)
                        if step_decision.transition_rule_id.delay_before_automatic_transition > 0:
                            date = fields.Date.today() - work.date_of_transition_to_the_current_stage
                            days = date.days
                            if days >= step_decision.transition_rule_id.delay_before_automatic_transition:
                                if not step_decision.transition_rule_id.condition_ids:
                                    work._execute_decision(step_decision,justification=None)
                                else:
                                    work._execute_decision_with_conditions(step_decision)
                        else:
                            if step_decision.transition_rule_id.condition_ids:
                                work._execute_decision_with_conditions(step_decision)
            except Exception as error:
                if 'cron' in self.env.context and self.env.context['cron']:
                    _logger.error("Erreur lors de la transition automatique sur le dossier %s détails : %r", work.name, error)
                    try:
                        if previous_step:
                            self.env['customisable_workflow.transition_history'].sudo().create({'model': work._name,
                                                                            'res_id': work.id,
                                                                            'user_id': self.env.user.id,
                                                                            'step_from_id':  work.current_step_id.id,
                                                                            'step_to_id': previous_step.id,
                                                                            'justification': _("Erreur lors de la transition automatique à l'étape %s.\nDétails : %s", work.current_step_id.name, error)})
                            work.current_step_id = previous_step.id
                    except Exception as error:
                        _logger.error("Erreur lors de l'annulation de la transition automatique sur le dossier %s détails : %r", work.name, error)
                else:
                    raise

    @api.model
    def _cron_automatic_transitions_between_steps(self):
        works = self.search([])
        works.with_context(transitioning=True, cron=True)._execute_automatic_transition()

    @api.model
    def create_cron(self, model_name):
        """Create a cron job for the given model if it doesn't already exist."""
        cron_name = f'Cron for {model_name} automatic transitions'
        cron = self.env['ir.cron'].search([('name', '=', cron_name)], limit=1)
        if not cron:
            self.env['ir.cron'].create({
                'name': cron_name,
                'model_id': self.env['ir.model']._get(model_name).id,
                'state': 'code',
                'code': f'model._cron_automatic_transitions_between_steps()',
                'user_id': self.env.ref('base.user_root').id,
                'interval_number': 5,
                'interval_type': 'minutes'
            })

    @api.model
    def _register_hook(self):
        # Overriding _register_hook to automatically create cron jobs for models
        # This is done to ensure that automatic transitions between steps are handled
        # for all applicable models other than 'customisable_workflow.work'
        res = super(Work, self)._register_hook()
        models = self.env['ir.model'].search([('model', '!=', 'customisable_workflow.work')])
        for model in models:
            try:
                model_class = self.env[model.model]
                if isinstance(model_class, Work):
                    self.create_cron(model.model)
            except Exception as e:
                _logger.error('Cannoot create cron for %s. Details: %r', model.model, e.message)
        return res

    def _execute_decision_with_conditions(self, step_decision):
        conditions_are_checked = self._check_transition_conditions(step_decision)
        if conditions_are_checked:
            _logger.info("Transitionning for work %s with decision %s", self.name, step_decision.name)
            self._execute_decision(step_decision,justification=None)
        
    def _check_transition_conditions(self, step_decision):
        conditions_are_checked = False
        for condition in step_decision.transition_rule_id.condition_ids:
            conditions_are_checked = condition.check_condition(self, conditions_are_checked)
            if step_decision.transition_rule_id.cumulative_mode == True and conditions_are_checked == False:
                break
            if step_decision.transition_rule_id.cumulative_mode == False and conditions_are_checked == True:
                break
        return conditions_are_checked     

    @api.model
    def _cron_transition_time(self):
        works = self.search(['|','|',('workflow_id.processing_start_step_id', '!=', False),('workflow_id.processing_end_step_id', '!=', False),('workflow_id.processing_expiraton_step_id', '!=', False)])
        for work in works:
            if work:
                transition_history_ids = work.transition_history_ids.filtered(lambda x: x.step_to_id.id == work.workflow_id.processing_end_step_id.id)
                if transition_history_ids:
                    pass
                else:
                    transition_history = work.env['customisable_workflow.transition_history'].search([('step_to_id', '=', work.workflow_id.processing_start_step_id.id),('res_id', '=', work.id)],limit=1)
                    if transition_history.date:
                        date = fields.Date.today() - transition_history.date.date()
                        days = date.days
                        if days >= work.workflow_id.maximum_processing_time:
                            self.env['customisable_workflow.transition_history'].sudo().create({'model': work._name,
                                                                        'res_id': work.id,
                                                                        'user_id': self.env.user.id,
                                                                        'step_from_id':  work.current_step_id.id,
                                                                        'step_to_id':  work.workflow_id.processing_expiraton_step_id.id}) 
                            work.current_step_id = work.workflow_id.processing_expiraton_step_id
                        else:
                            pass

    @api.depends("current_step_id")
    def _compute_date_of_transition_to_the_current_stage(self):
        for work in self:
            if work.current_step_id:
                work.date_of_transition_to_the_current_stage = fields.Date.today()

    def get_view(self, view_id=None, view_type='form',**options):
        result = super(Work, self).get_view(view_id=view_id, view_type=view_type, **options)
        if view_type == 'form':
            doc = etree.XML(result['arch'])
            header = doc.xpath("//header")
            steps = self.env['customisable_workflow.step'].search([])
            sheet = []
            for sheet_node in doc.xpath("//sheet"):
                span_element = etree.Element("span")
                sheet_node.insert(0, span_element)
                sheet = doc.xpath("//sheet/span")
            if steps:
                for step in steps:
                    invisible_button = "current_step_id != %s or  current_user_can_act == False" %step.id
                    invisible_ribbon = "current_step_id != %s or visible_step == '%s'" %(step.id,IN_TREATMENT_LABEL)
                    bg_color = None
                    if step.criticity == "info":
                        bg_color = "bg-info"
                    if step.criticity == "success":
                        bg_color = "bg-success"
                    if step.criticity == "warning":
                        bg_color = "bg-warning"
                    if step.criticity == "danger":
                        bg_color = "bg-danger"
                    if sheet:
                        etree.SubElement(sheet[0],'widget', {'name': "web_ribbon", 
                                                             'title': step.name, 'bg_color': bg_color, 
                                                             'invisible': invisible_ribbon, 'tooltip': step.description or ""})
                    if header:
                        for decision in step.step_decision_ids:
                            if decision.is_manual_decision:
                                highlight_button = decision.highlight_button
                                invisible_criteria = False
                                decision_id =" {'decision_id': %d}" %decision.id
                                button_visibility_criterion = decision.button_visibility_criterion
                                if button_visibility_criterion:
                                    pattern = r'(\w+)\s*(==|!=|>|<|>=|<=|in)\s*(.+)'
                                    match = re.search(pattern, button_visibility_criterion)
                                    if match:
                                        variable_name = match.group(1)
                                        if variable_name in self._fields:
                                            invisible_criteria = " or ".join([invisible_button, button_visibility_criterion])
                                etree.SubElement(header[0],'button', {'string': decision.name, 'name': "make_a_decision", 'type': "object", 'class': "oe_highlight" if highlight_button else "", 'invisible': invisible_criteria if invisible_criteria else invisible_button, 'context': decision_id})

            if sheet:
                invisible_ribbon = "visible_step != '%s' " %IN_TREATMENT_LABEL
                etree.SubElement(sheet[0],'widget', {'name': "web_ribbon", 'title': IN_TREATMENT_LABEL, 'bg_color': "bg-info", 'invisible': invisible_ribbon})
            for key,vals in result['models'].items():
                if key == result["model"]:
                    for field in vals:
                        for node in doc.xpath("//field[@name='%s']" % field):
                            secondary = False
                            for parent in node.iterancestors():
                                if parent.tag == 'field':
                                    secondary = True
                                    break
                            if not secondary and not node.attrib.get('readonly'):
                                node.set('readonly',"is_not_editable == True")
            workflow_ids = self.env['customisable_workflow.workflow'].search([('res_model_id.model', '=', self._name)])
            # first group by field because 2 workflows may have different requirements on the same field
            rules_by_field = {}
            for workflow_id in workflow_ids:
                if workflow_id.field_step_visibility_ids:
                    for field_step_visibility in workflow_id.field_step_visibility_ids:
                        if field_step_visibility.field_id.name not in rules_by_field:
                            rules_by_field[field_step_visibility.field_id.name] = {}
                        rules_by_field[field_step_visibility.field_id.name][workflow_id.id] = field_step_visibility
            # theb set rules on fields nodes
            for field_name in rules_by_field:
                for node in doc.xpath("//field[@name='%s']" % field_name):
                    required_conditions = []
                    readonly_conditions = []
                    invisible_conditions = []
                    for workflow_id in rules_by_field[field_name]:
                        field_step_visibility = rules_by_field[field_name][workflow_id]
                        if field_step_visibility.visible_step_id:
                            invisible_conditions.append("workflow_id==%d and %d not in done_step_ids" % (workflow_id, field_step_visibility.visible_step_id.id))
                        if field_step_visibility.required_step_id:
                            required_conditions.append("workflow_id==%d and %d in done_step_ids" % (workflow_id, field_step_visibility.required_step_id.id))
                        if field_step_visibility.readonly_step_id:
                            readonly_conditions.append("workflow_id==%d and %d in done_step_ids" % (workflow_id, field_step_visibility.readonly_step_id.id))
                    if invisible_conditions:
                        if node.get('invisible'):
                            invisible_conditions.insert(0,"(%s)" % node.get('invisible'))
                        node.set('invisible'," or ".join(invisible_conditions))
                    if required_conditions:
                        if node.get('required'):
                            required_conditions.insert(0,"(%s)" % node.get('required'))
                        node.set('required', " or ".join(required_conditions))
                    if readonly_conditions:
                        if node.get('readonly'):
                            readonly_conditions.insert(0,"(%s)" % node.get('readonly'))
                        node.set('readonly', " or ".join(readonly_conditions))
            result['arch'] = etree.tostring(doc, encoding='unicode')
        return result

    @api.constrains('workflow_id')
    def _set_first_step_if_not_set(self):
        for work in self:
            if work.workflow_id and not work.current_step_id:
                if not work.workflow_id.start_step_id:
                    raise ValidationError(_("Pour commencer, la premère étape du processus doit être définie."))
                work.current_step_id = work.workflow_id.start_step_id.id
                
    @api.constrains('workflow_id')
    def _set_first_transition_history(self):
        for work in self:
            transition_history = self.env['customisable_workflow.transition_history'].sudo().search([('model', '=', self._name),
                                                                        ('res_id', '=', work.id),
                                                                        ('step_to_id', '=', work.current_step_id.id)])
            if not transition_history:
                self.env['customisable_workflow.transition_history'].sudo().create({'model': self._name,
                                                                        'res_id': work.id,
                                                                        'user_id': self.env.user.id,
                                                                        'step_to_id':  work.current_step_id.id})

    @api.onchange('workflow_id')
    def _on_workflow_change_set_first_step(self):
        if self.workflow_id and self.workflow_id.step_ids:
            self.current_step_id = self.workflow_id.start_step_id.id
    
    @api.constrains('current_step_id')
    def _check_current_user_can_act(self):
        if not self._current_user_can_act_previous_step():
            raise ValidationError(_("Vous n'êtes pas autorisé à valider cette étape."))

    @api.constrains('current_step_id')
    def _move_to_next_if_automatic(self):
        if self.current_step_id.is_automatic_step:
            self.sudo().go_to_next_stage()
    
    @api.constrains('current_step_id')
    def _check_previous_step_required_docs(self):
        for work in self:
            if work.previous_step_id:
                doc_not_attachement = []
                for document in work.previous_step_id.provided_document_ids:
                    if document.is_required:
                        for existing_doc in work.given_document_ids:
                            if document.id == existing_doc.document_id.id and existing_doc.step_id.id == work.previous_step_id.id:
                                if not existing_doc.attachment:
                                    doc_not_attachement.append(existing_doc.name)
                if doc_not_attachement:
                    if len(doc_not_attachement) == 1:
                        raise ValidationError(_("Le documents %s est obligatoire avant d'aller à l'étape suivante") % ', '.join(doc_not_attachement))
                    else:
                        raise ValidationError(_("Les documents suivants doivent être fournis avant de passer à l'étape suivante :\n• %s") % '\n• '.join(doc_not_attachement))
    
    @api.constrains('current_step_id')
    def _send_notifications(self):
        for work in self:
            if work.current_step_id:
                for notification_type in work.current_step_id.notification_type_ids.filtered(lambda notification: notification.when_to_send=="beginning" or not notification.when_to_send):
                    notification_type.send_for_work(work)
            if work.previous_step_id:
                for notification_type in work.previous_step_id.notification_type_ids.filtered(lambda notification: notification.when_to_send=="end"):
                    notification_type.send_for_work(work)
    
    def _compute_current_user_can_act(self):
        for record in self:
            if record.current_step_id.allowed_user_ids or record.current_step_id.allowed_group_ids:
                can_validate = False
                for user in record.current_step_id.all_allowed_user_ids:
                    if self.env.user.id == user.id:
                        can_validate = True
                        break
            else:
                can_validate = True
            record.current_user_can_act = can_validate
    
    def _current_user_can_act_previous_step(self):
        for record in self:
            odoobot = self.env.ref('base.user_root')
            if odoobot.id == self.env.user.id:
                can_validate = True
            else:
                if record.previous_step_id.allowed_user_ids or record.previous_step_id.allowed_group_ids:
                    can_validate = False
                    for user in record.previous_step_id.all_allowed_user_ids:
                        if self.env.user.id == user.id:
                            can_validate = True
                            break
                else:
                    can_validate = True
            return can_validate

    def format_date(self,date):
        return time.strftime("%d/%m/%Y",time.strptime(str(date),"%Y-%m-%d")) or ''
    
    def get_today_date(self):
        return time.strftime("%d/%m/%Y",time.strptime(str(fields.Date.today()),"%Y-%m-%d")) or ''

    def make_a_decision(self):
        for record in self:
            decision_id = self.env.context.get('decision_id')
            decision = self.env['customisable_workflow.step_decision'].search([('id', '=', decision_id)])
            if decision.need_a_justification:
                action = {
                    'name': _('Justification'),
                    'view_mode': 'form',
                    'res_model': 'customisable_workflow.justification_wizard',
                    'view_id': self.env.ref('customisable_workflow.justification_form_view').id,
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    'context': {'default_decision_id': decision_id,'default_model':self._name,'default_res_id':self.id}
                    }
                return action
            else:
                return record._execute_decision(decision,justification=None)

    def go_to_next_stage(self):
        if self.current_step_id.step_decision_ids:
            decision = self.current_step_id.step_decision_ids[0]
            self._execute_decision(decision,justification=None)
    
    def _execute_decision(self, decision, justification):
        transition_history = {'model': self._name,
                                'res_id': self.id,
                                'user_id': self.env.user.id,
                                'step_from_id':  self.current_step_id.id,
                                'justification': justification}
        if decision.target_step_id:
            transition_history['step_to_id'] = decision.target_step_id.id
        #Have to create the history before to set the current_sep_id
        self.env['customisable_workflow.transition_history'].sudo().create(transition_history)
        if decision.target_step_id:
            self.current_step_id = decision.target_step_id.id
        try:
            if decision.python_compute and decision.python_compute.strip():
                localdict = {'env': self.env, 'record': self}
                return safe_eval(decision.python_compute.strip(),localdict, mode="eval", nocopy=True)
        except Exception as e:
            raise UserError(f"Error executing Python code: {e}")
    
    def _get_previous_step(self):
        for work in self:
            previous_step = self.env['customisable_workflow.transition_history'].search(domain=[('res_id', '=', work.id),('model', '=', self._name)], limit=1, order="id desc")
            work.previous_step_id = previous_step.step_from_id.id
    
    def _compute_justification(self):
        for work in self:
            last_justification = self.env['customisable_workflow.transition_history'].search(domain=[('res_id', '=', work.id),('model', '=', self._name)], offset=0, limit=1, order="id desc").justification
            if last_justification:
                work.has_a_justification = True
                work.justification = last_justification
            else:
                work.has_a_justification = False
                work.justification = ''
    
    def _compute_visible_step(self):
        for work in self:
            work.visible_step = work.current_step_id.name
            is_authorized = False
            if work.current_step_id.visible_to_group_ids:
                users = self.env['res.users']
                for group in work.current_step_id.visible_to_group_ids:
                    users |= group.user_ids
                for user in users:
                    if self.env.user.id == user.id:
                        is_authorized = True
                        break
                if is_authorized == False:
                    work.visible_step = IN_TREATMENT_LABEL

    @api.constrains('state')
    def _set_current_step_on_state_change(self):
        for record in self:
            '''
                Listen for state changes to make correspondance between state and current step
                as requested by step configuration.
            '''
            if record.state:
                step = self.env['customisable_workflow.step'].search([('workflow_id', '=', record.workflow_id.id),('corresponding_state','=',record.state)])
                if step:
                    record._set_history(step)
                    record.sudo().write({'current_step_id': step.id})
                    
    def _set_history(self,step):
        '''
            Complete the iniated pending transition history.
            This method updates the transition history records associated with the current record.
            It completes any pending transition histories initiated.
            If no pending transition history is found, it creates a new one.
        '''
        transition_history = None
        # In case the transition was done clicking on the decision button, decision_id is in the context.
        # In that case we expect an uncomplte trasition history that we need to complete.
        # If decision_id is not in the context, it means the state change was done by another process in Odooo
        if 'decision_id' in self.env.context:
            decision = self.env['customisable_workflow.step_decision'].browse(self.env.context['decision_id'])
            if self.workflow_id.id == decision.workflow_id.id:
                transition_history = self.env['customisable_workflow.transition_history'].with_context(show_all=True).search([('res_id', '=', self.id), ('user_id','=',self.env.user.id),
                                                    ('step_from_id', '=', decision.step_id.id), ('step_to_id','=', False)], limit=1,  order='id desc')
          # If a transition history is found with decision_id in the context, update step_to_id with the new step
        if transition_history:
            transition_history.write({'step_to_id': step.id})
        else:
            #Check if the transition history is not yet there befor creating
            #Create it if its step_to_id does not match our step
            transition_history = self.env['customisable_workflow.transition_history'].with_context(show_all=True).search([('res_id', '=', self.id)], limit=1,  order='id desc')
            if transition_history and not transition_history.step_to_id.id == step.id:
                self.env['customisable_workflow.transition_history'].create({
                    'step_from_id':transition_history.step_to_id.id,
                    'step_to_id': step.id,
                    'model': self._name,
                    'res_id': self.id,
                    'user_id': self.env.user.id,
                })