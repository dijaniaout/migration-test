# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

@tagged('test_step')
class TestSpet(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestSpet, cls).setUpClass()
        cls.workflow_model = cls.env['customisable_workflow.workflow']
        cls.step_model = cls.env['customisable_workflow.step']
        cls.workflow = cls.workflow_model.create({
            'name': 'Worflow '
        })

    # Test that ValidationError is raised when an automatic step has more than one decision.
    def test_automatic_step_cannot_have_more_decision(self):
        with self.assertRaises(ValidationError, msg = "On ne peut pas avoir une étape automatique avec plusieurs décisions."):
            self.step_model.create({
            'name': "Step1 ",
            'workflow_id':self.workflow.id,
            'is_automatic_step': True,
            'step_decision_ids': [(0, 0, {'name': 'Decision1'}), (0, 0, {'name': 'Decision 2'})]
        })

    # Test that no ValidationError is raised when a valid step is created.
    def test_automatic_step_have_one_decision(self):
        step = self.step_model.create({
            'name': "Step 2 ",
            'workflow_id':self.workflow.id,
            'is_automatic_step': True,
            'step_decision_ids': [(0, 0, {'name': 'Decision1'})]
        })
        logging.info('Step %r', step)
        decision_len = len(step.step_decision_ids)
        self.assertEqual(decision_len, 1, "L'étape automatique doit avoir exactement une décision")