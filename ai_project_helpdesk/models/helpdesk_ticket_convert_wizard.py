from odoo import _, models, fields
from odoo.exceptions import UserError
from odoo.tools import html2plaintext
import json
from odoo.addons.ai.utils.llm_api_service import LLMApiService


class HelpdeskTicketConvertWizard(models.TransientModel):
    _inherit = 'helpdesk.ticket.convert.wizard'

    stage_id = fields.Many2one('project.task.type', string='Stage', domain="[('project_ids', 'in', project_id)]",
                               compute='_compute_default_stage', readonly=False, store=True, required=False)

    def action_auto_assign_project(self):
        # Get the ticket being converted
        tickets = self._get_tickets_to_convert()
        if not tickets:
            raise UserError(_("No ticket found to convert."))
        ticket = tickets[0]  # We process one ticket at a time

        # Get available projects
        projects = self.env['project.project'].search([
            ('is_template', '=', False),
            ('active', '=', True),
        ])
        if not projects:
            raise UserError(_("No active projects found."))

        # Build pipe-separated project list (avoid repeating JSON keys)
        project_table = "ID|Name|Description\n"
        for project in projects:
            # Clean and truncate description
            desc = ""
            if project.description:
                desc = html2plaintext(
                    project.description).strip().replace('\n', ' ')
            if not desc:
                desc = "No description available"
            # Escape pipe characters if any
            name = project.name.replace('|', '/')
            desc = desc.replace('|', '/')
            project_table += f"{project.id}|{name}|{desc}\n"

        # Prepare ticket information
        ticket_subject = ticket.name or "No subject"
        ticket_description = ""
        if ticket.description:
            ticket_description = html2plaintext(ticket.description).strip()
        ticket_tags = ", ".join(ticket.tag_ids.mapped(
            'name')) if ticket.tag_ids else "No tags"

        # Prepare system and user prompts
        system_prompt = (
            "You are an AI assistant helping to categorize support tickets "
            "into appropriate projects. Analyze the ticket content and match it "
            "with the most suitable project based on the description and context. "
            "Consider the subject matter, technical domain, and any mentioned "
            "keywords or tags."
        )

        user_prompt = f"""
        Based on this helpdesk ticket, select the most appropriate project:

        TICKET INFORMATION:
        - Subject: {ticket_subject}
        - Description: {ticket_description}
        - Tags: {ticket_tags}

        AVAILABLE PROJECTS (pipe-separated table):
        {project_table}

        Analyze the ticket content and select the project ID that best matches 
        the ticket's topic and requirements.
        Return the project ID of the best match, with your reasoning and confidence level.
        """

        # Define response schema for structured output
        response_schema = {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "The ID of the selected project"
                },
                "reasoning": {
                    "type": "string",
                    "description": "Brief explanation of why this project was selected"
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Confidence level of the match (0–1)"
                },
            },
            "required": ["project_id", "reasoning", "confidence"],
            "additionalProperties": False,
        }

        # Initialize LLM service
        llm_service = LLMApiService(self.env, 'google')

        # Make the LLM request
        response = llm_service.request_llm(
            llm_model="gemini-1.5-flash",
            system_prompts=[system_prompt],
            user_prompts=[user_prompt],
            schema=response_schema,
        )

        # Parse the response
        if response and response[0]:
            result = json.loads(response[0])

            # Validate the project ID exists
            selected_project = projects.filtered(
                lambda p: p.id == result['project_id'])
            if not selected_project:
                raise UserError(_(
                    "AI suggested project ID %s which doesn't exist." % result['project_id']
                ))

            # Update the wizard with the selected project
            self.project_id = selected_project.id
            
            created_task = self.env['project.task'].with_context(mail_create_nolog=True).create(
                [self._get_task_values(ticket)]
            )
            
            return {
                'view_mode': 'form',
                'res_model': 'project.task',
                'res_id': created_task.id,
                'views': 'project.view_task_form2',
                'type': 'ir.actions.act_window',
            }

            # # Show notification and refresh the wizard form
            # notification = {
            #     'type': 'ir.actions.client',
            #     'tag': 'display_notification',
            #     'params': {
            #         'type': 'success',
            #         'title': _('Project Auto-Assigned'),
            #         'message': _("Selected: %s (%d%% confidence)") % (
            #             selected_project.name, int(
            #                 result.get('confidence', 0) * 100)
            #         ),
            #         'sticky': False,
            #     }
            # }
            
            # return notification
