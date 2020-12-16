# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveReversal(models.TransientModel):

    _inherit = "account.move.reversal"

    @api.onchange("refund_method")
    def compute_anglo_saxon_state(self):
        if self.env.context.get("active_ids"):
            inv = self.env["account.move"].browse(self.env.context["active_ids"])
            anglo_saxon = inv.company_id.anglo_saxon_accounting
        else:
            anglo_saxon = self.env.user.company_id.anglo_saxon_accounting
        for record in self:
            record.anglo_saxon_accounting = anglo_saxon

    anglo_saxon_refund_type = fields.Selection(
        [("financial", "Financial Only"), ("stock", "Stock Affected")],
        string="Impact of Refund",
        required=True,
        default="financial",
    )
    anglo_saxon_accounting = fields.Boolean()

    def reverse_moves(self):
        action = super().reverse_moves()
        if (
            self.refund_method == "refund"
            and self.anglo_saxon_refund_type == "financial"
            and isinstance(action, dict)
            and (action.get("res_id", "domain"))
        ):
            for inv in self.env["account.move"].browse(action.get("res_id", "domain")):
                if inv and not inv.anglo_saxon_financial:
                    inv.toggle_financial()
        return action
