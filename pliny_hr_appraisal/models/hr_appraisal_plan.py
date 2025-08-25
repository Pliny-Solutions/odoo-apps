from odoo import models, fields, api
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class AppraisalPlan(models.Model):
    _name = "hr.appraisal.plan"
    _description = "List of the Appraisals the company plans to do"
    _order = "start_date desc"

    name = fields.Char('Name',required=True)
    start_date = fields.Date(
        string="Start Date",
        help="Start of period under evaluation, Can be left blank for general evaluations like Exit and end of probation evaluations")
    end_date = fields.Date(
        string="End Date",
        help="End of period under evaluation, Can be left blank for general evaluations like Exit and end of probation evaluations. Also acts as deadline of submissions")
    deadline = fields.Date(string="Submission Deadline")
    description = fields.Char(translate=False)
    score_id = fields.Many2one('hr.appraisal.score', string="Scoring System")
    allocation_ids = fields.One2many('hr.appraisal.plan.allocation', 'plan_id', string="Allocations")
    question_ids = fields.One2many('hr.appraisal.plan.question', 'plan_id', string="Questions")
    category_id = fields.Many2one('hr.appraisal.category', string="Appraisal Category")

    @api.constrains('deadline')
    def _check_deadline(self):
        for record in self:
            if record.deadline <= fields.Date.today():
                raise ValidationError("The deadline cannot be set in the past")


    @api.constrains('end_date')
    def _check_end_date(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date <= record.start_date:
                    raise ValidationError("The end date has to be after the start date")

    def open_add_employees_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.appraisal.add.employees.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_plan_id': self.id,
            }
        }

    def action_generate_appraisals(self):
        Appraisal = self.env['hr.appraisal']
        created = 0

        for plan in self:
            _logger.info(f"▶ Processing plan: {plan.name} (ID: {plan.id})")
            _logger.info(f"▶ Total allocations: {len(plan.allocation_ids)}")

            for alloc in plan.allocation_ids:
                if not alloc.employee_id:
                    _logger.warning(f"⚠ Skipping allocation with no employee set.")
                    continue

                employee = alloc.employee_id
                _logger.info(f"👤 Checking employee: {employee.name} (ID: {employee.id})")

                # Check for existing appraisal
                existing = Appraisal.search([
                    ('employee_id', '=', employee.id),
                    ('plan_id', '=', plan.id)
                ], limit=1)

                if existing:
                    _logger.warning(f"⛔ Appraisal already exists for {employee.name}")
                    continue

                _logger.info(f"✅ Creating appraisal for {employee.name}")

                appraisal = self.env['hr.appraisal'].create({
                    'employee_id': employee.id,
                    'plan_id': plan.id,
                    'start_date': plan.start_date,
                    'end_date': plan.end_date,
                    'deadline': plan.deadline,
                    'category_id': plan.category_id.id if plan.category_id else False,
                    'manager_id': employee.parent_id.id if employee.parent_id else False,
                    'job_id': employee.job_id.id if employee.job_id else False,
                    'department_id': employee.department_id.id if employee.job_id else False,
                    'state': 'draft',
                })
                created += 1

                # Mark allocation as allocated ✅
                alloc.state = 'allocated'

                # Move questions to appraisal question
                for question_template in plan.question_ids:
                    self.env['hr.appraisal.question'].create({
                        'appraisal_id': appraisal.id,
                        'name': question_template.name,
                        'description': question_template.description,
                        'maximum_value': question_template.maximum_value,
                    })

                # In-app Notification
                if employee.user_id and employee.user_id.partner_id:
                    self.env['bus.bus']._sendone(
                        employee.user_id.partner_id,
                        'notification',
                        {
                            'type': 'info',
                            'title': "New Appraisal Assigned",
                            'message': f"You have a new appraisal under the plan: {plan.name}",
                        }
                    )


                # Email Notification - Employer
                template = self.env.ref('hr_evaluation.mail_template_appraisal_allocated_employee', raise_if_not_found=False)
                if template and employee.work_email:
                    try:
                        template.send_mail(appraisal.id, force_send=True)
                        _logger.info(f"📧 Email sent to {employee.work_email} for appraisal {appraisal.id}")
                    except Exception as e:
                        _logger.error(f"❌ Failed to send email for {employee.name}: {str(e)}")

                # Email Notification - Manager
                template = self.env.ref('hr_evaluation.mail_template_appraisal_allocated_manager', raise_if_not_found=False)
                if template and employee.work_email:
                    try:
                        template.send_mail(appraisal.id, force_send=True)
                        _logger.info(f"📧 Email sent to {employee.work_email} for appraisal {appraisal.id}")
                    except Exception as e:
                        _logger.error(f"❌ Failed to send email for {employee.name}: {str(e)}")

        _logger.info(f"✅ Total appraisals created: {created}")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': "Appraisal Generation",
                'message': f"{created} appraisal(s) created.",
                'type': 'success' if created else 'warning',
            }
        }




class AppraisalPlanAllocation(models.Model):
    _name = "hr.appraisal.plan.allocation"
    _description = "List of employees who should fill out this appraisal Essential for email"


    plan_id = fields.Many2one('hr.appraisal.plan', string="Appraisal Plan")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    notes = fields.Char(string="Notes")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('allocated', 'Allocated'),
    ], string="Status", default='draft')

    #Prevent deletion of records that have been allocated
    def unlink(self):
            for record in self:
                if record.state == 'allocated':
                    raise UserError("You cannot delete an allocation that is already allocated.")
            return super(AppraisalPlanAllocation, self).unlink()


class AppraisalPlanQuestion(models.Model):
    _name = "hr.appraisal.plan.question"
    _description = "List of questions every employee under this plan must be asked"


    plan_id = fields.Many2one('hr.appraisal.plan', string="Appraisal Plan")
    name = fields.Char(string="Question", required=True)
    description = fields.Char(string="Description")
    score_id = fields.Many2one('hr.appraisal.score', related="plan_id.score_id", string="Scoring System", readonly=True)
    maximum_value = fields.Integer(string="Maximum Score", compute="_compute_maximum_value", store=True)


    @api.depends('plan_id.score_id.maximum_value')
    def _compute_maximum_value(self):
        for question in self:
            question.maximum_value = question.plan_id.score_id.maximum_value or 0



