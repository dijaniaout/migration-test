from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

@tagged('test_work')
class TestWorkflow(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestWorkflow, cls).setUpClass()
        cls.work_test = cls.env['customisable_workflow.work_test']
        cls.user_model = cls.env['res.users']
        cls.group_model = cls.env['res.groups']
        cls.workflow_model = cls.env['customisable_workflow.workflow']
        cls.step_decision_model = cls.env['customisable_workflow.step_decision']
        cls.step_model = cls.env['customisable_workflow.step']

         # Create Workflow
        cls.workflow = cls.workflow_model.create({
            'name': 'Processus demo',
        })   

        # Create the group
        cls.group_legal_unit = cls.group_model.create({
            'name': 'Cellule juridique',
        })           

        # Create Steps
        cls.workflow_step1 = cls.step_model.create({
            'name': 'Etape 1',
            'workflow_id': cls.workflow.id,
            'allowed_group_ids': [(4, cls.group_legal_unit.id)],
        })
        cls.workflow_step2 = cls.step_model.create({
            'name': 'Etape 2',
            'workflow_id': cls.workflow.id,
            'allowed_group_ids': [(4, cls.group_legal_unit.id)],
        })
        cls.workflow_step3 = cls.step_model.create({
            'name': 'Etape 3',
            'workflow_id': cls.workflow.id,
        })

        # Set initial step
        cls.workflow.write({'start_step_id': cls.workflow_step1.id})
        
        # Create Step Decisions
        cls.workflow_decision_step1_step2 = cls.step_decision_model.create({
            'name': 'Valider',
            'workflow_id': cls.workflow.id,
            'step_id': cls.workflow_step1.id,
            'target_step_id': cls.workflow_step2.id,
        })
        cls.workflow_decision_step2_step3 = cls.step_decision_model.create({
            'name': 'Valider',
            'workflow_id': cls.workflow.id,
            'step_id': cls.workflow_step2.id,
            'target_step_id': cls.workflow_step3.id,
        })

        cls.record = cls.work_test.create({
            'name': 'Achat pain',
            'workflow_id': cls.workflow.id,
        })
        cls.internal_user_group = cls.env.ref('base.group_user')  # Reference to the internal user group
        #create test user
        cls.user_test = cls.user_model.create({
            'name': 'Test User',
            'login': 'testuser',
            'email': 'testuser@example.com',
            'group_ids': [(6, 0, [cls.group_legal_unit.id, cls.internal_user_group.id])]
        })
        

    def test_authorized_user_can_change_steps(self):
        test_user_env = self.env(user=self.user_test)
        context_with_decision_id = dict(self.env.context, decision_id=self.workflow_decision_step1_step2.id)     
        logger.info("Context %r", context_with_decision_id)

        # Call make_a_decision with the modified context and user environment
        self.record.with_env(test_user_env).with_context(context_with_decision_id).make_a_decision()
        expected_step_id = self.workflow_step2.id

        # Check if history is created before to set the current_sep_id
        history = self.env['customisable_workflow.transition_history'].search([('user_id', '=', test_user_env.user.id),('step_from_id', '=', self.workflow_decision_step1_step2.step_id.id),
                                                                               ('step_to_id', '=', expected_step_id) ])    
        logger.info("History %r", history)
        self.assertEqual(len(history), 1, "L'historique n'a pas été créé avant de définir l'étape courante") 
        self.assertEqual(self.record.current_step_id.id, expected_step_id, 
                         "L'étape courante ne correspond pas à l'étape attendue après l'exécution de la décision.")

    
    def test_unauthorized_user_cannot_change_steps(self):
        #create test user not allowed
        another_test = self.user_model.create({
            'name': 'Another User',
            'login': 'anotheruser',
            'email': 'anotheruser@another.com',
        })
        test_user_env = self.env(user=another_test)
        context_with_decision_id = dict(self.env.context, decision_id=self.workflow_decision_step1_step2.id)     
        logger.info("Context_with_decision_id %r", context_with_decision_id)
        with self.assertRaises(ValidationError):
            # Call make_a_decision with the modified context and user environment
            self.record.with_env(test_user_env).with_context(context_with_decision_id).make_a_decision()

    def test_authorized_user_can_change_steps_with_justification(self):
        workflow_decision_test = self.step_decision_model.create({
            'name': 'Valider',
            'workflow_id': self.workflow.id,
            'step_id': self.workflow_step2.id,
            'target_step_id': self.workflow_step3.id,
            'need_a_justification': True,
        })
        test_user_env = self.env(user=self.user_test)
        context_with_decision_id = dict(self.env.context, decision_id=workflow_decision_test.id)     
        logger.info("Context %r", context_with_decision_id)
        # Calwith_decision_idl make_a_decision with the modified context and user environment
        action = self.record.with_env(test_user_env).with_context(context_with_decision_id).make_a_decision()   
        logger.info("Action %r", action) 
        #Check that the action is returned
        self.assertIsNotNone(action, "L'action retourné ne doit pas être nulle")
        self.assertEqual(action['name'], 'Justification', "Le nom de l'action retourné  doit être 'Justification'")
        self.assertEqual(action['res_model'], 'customisable_workflow.justification_wizard', 
                         "Le modèle de l'action retourné doit être 'customisable_workflow.justification_wizard'.")
        self.assertEqual(action['type'], 'ir.actions.act_window', "Le type de l'action retourné doit être 'ir.actions.act_window'.")


    @classmethod
    def tearDownClass(cls):
        # Reset the environment state
        cls.env.reset()
        super().tearDownClass()
