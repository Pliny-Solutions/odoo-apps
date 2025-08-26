from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TrainingTrainee(models.Model):
    _name = "hr.training.trainee"
    _description = "List of trainees who attended a training"

    training_id = fields.Many2one('hr.training', string="Training")
    partner_id = fields.Many2one(
        'res.partner',
        string="Trainee",
        required=True,
        domain=[('is_company', '=', False)]
    )
    reimbursement = fields.Monetary(
        string="Reimbursement",
        currency_field='currency_id',
        default=0,
        help="Amount allocated to trainee as payment or reimbursement"
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        readonly=True,
        default=lambda self: self.env.company.currency_id
    )
    notes = fields.Char(string="Notes")

class TrainingExpense(models.Model):
    _name = "hr.training.expense"
    _description = "Expenses incurred during training"

    training_id = fields.Many2one('hr.training', string="Training")
    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        required=True,
        help="Employee responsible for the expense"
    )
    name = fields.Char(string="Name", required=True)
    notes = fields.Char(string="Notes")
    expense = fields.Monetary(
        string="Expense",
        currency_field='currency_id',
        default=0,
        help="Cost of the expense item"
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        readonly=True,
        default=lambda self: self.env.company.currency_id
    )


