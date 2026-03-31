from odoo.tests.common import TransactionCase, tagged
from odoo import Command
from odoo.exceptions import UserError
# from odoo.exceptions import ValidationError
import logging
Logger = logging.getLogger(__name__)


@tagged('test_for_work')
class TestWork(TransactionCase):

    def setUp(self):
        super(TestWork, self).setUp()
        self.work_model = self.env['customisable_workflow.work_test']
        self.group_user = self.env.ref('base.group_user')
        self.step_model = self.env['customisable_workflow.step']
        self.workflow_model = self.env['customisable_workflow.workflow']
        self.group_manager = self.env.ref('base.group_system')
        self.user_model = self.env['res.users']
        self.decission_model = self.env['customisable_workflow.step_decision']
        self.transition_history_model = self.env['customisable_workflow.transition_history']

        #create test user
        self.user = self.user_model.create({
            'name': 'Test User',
            'login': 'test_user',
            'group_ids' : (self.group_user ).ids
        })

        # Create Workflow without step
        self.workflow = self.workflow_model.create({
            'name': 'Processus demo',
        })
        # Create Steps
        self.workflow_step1 = self.step_model.create({
            'name': 'Etape 1',
            'workflow_id': self.workflow.id,
            'allowed_group_ids': [(6, 0, [self.group_manager.id])],
        })
        self.workflow_step2 = self.step_model.create({
            'name': 'Etape 2',
            'workflow_id': self.workflow.id,
            'allowed_group_ids': [(6, 0, [self.group_manager.id])],
        })

        self.workflow_step3 = self.step_model.create({
            'name': 'Etape 3',
            'workflow_id': self.workflow.id,
            'allowed_group_ids': [(6, 0, [self.group_manager.id])],
        })
        # Set start_step_id for workflow
        self.workflow.write({
            'start_step_id': self.workflow_step1.id
        })
        # Create a work 
        self.work = self.work_model.create({
            'name': 'Test Work',
            'workflow_id': self.workflow.id,
        })
        #Create step decission
        self.decision_step_1_2 = self.decission_model.create({
            'name': 'Décision D',
            'step_id': self.workflow_step1.id,
            'target_step_id': self.workflow_step2.id,      
        })
       

    def test_compute_done_steps(self): 
        # create work test
        work_test = self.work_model.create({
            'name': 'Test Work',
            'workflow_id': self.workflow.id,
            'current_step_id': self.workflow_step1.id 
        })
        # Exécute  décision D for  A in  B
        work_test.with_context(decision_id=self.decision_step_1_2.id).make_a_decision()
        # Verify that current_step_id is updated in step B (step2)
        self.assertEqual(work_test.current_step_id.id, self.workflow_step2.id, "Le workflow doit aller à l'étape cible configurée sur la décision exécutée.")
        # Verifies that done_step_ids contains the correct steps(A puis B)
        work_test.invalidate_recordset()
        done_steps = work_test.done_step_ids.ids
        expected_steps = [self.workflow_step1.id, self.workflow_step2.id]
        self.assertEqual(done_steps, expected_steps, "Les étapes terminées ne sont pas correctement calculées.")

    def test_code_python_of_decision_executed(self):
        # Add pyhton code  for decision
        self.decision_step_1_2.write({'python_compute': 'record.write({"name": "Achat local"})'})
        # create work test
        work_test = self.work_model.create({
            'name': 'Test Work',
            'workflow_id': self.workflow.id,
            'current_step_id': self.workflow_step1.id ,    
        })
        # Exécute  décision D for  A in  B
        work_test.with_context(decision_id=self.decision_step_1_2.id).make_a_decision()
        # Vérify  the field of  'name' is modify
        self.assertEqual(work_test.name, "Achat local", "Le code python de la décision doit être exécuté ")
    
    def test_replace_workflow_static_with_dynamic_workflow(self):
        # Create a work test
        work_test = self.work_model.create({
            'name': 'Test Work',
            'workflow_id': self.workflow.id,
        })
        # Create  le workflow dynamique
        self.workflow_dynamic = self.workflow_model .create({
            'name': 'Workflow Dynamique Achat'
        })
        # Create step A (Draft) et B (Confirmed)
        self.step_a = self.step_model.create({
            'name': 'Étape A - Brouillon',
            'workflow_id': self.workflow_dynamic.id,
            'corresponding_state': "draft"     
        })  
        self.step_b = self.step_model.create({
            'name': 'Étape B - Confirmé',
            'workflow_id': self.workflow_dynamic.id,
            'corresponding_state': 'confirmed'
            
        })
        # Create a dynamic procedure that uses this workflow
        self.work_dynamic = self.work_model.create({
            'name': 'Procédure dynamique achat',
            'workflow_id': self.workflow_dynamic.id,
            'current_step_id': self.step_a.id  # Starts at   A (Draft)
        })
        # Create the decision to move from A (Draft) to B (Confirmed)
        self.decision_ab = self.decission_model.create({
            'name': 'Confirmer l\'achat',
            'step_id': self.step_a.id,  #  stepA - draft
            'python_compute': 'record.action_confirm()'  # Code Python to change step
        })
        # Execute Decision D (Confirm Purchase)
        self.work_dynamic.with_context(decision_id=self.decision_ab.id).make_a_decision()
        # Verify that the procedure is now at Step B (Confirmed)
        self.assertEqual(self.work_dynamic.current_step_id, self.step_b, "La procédure devrait être à l'étape B (Confirmé)")
            