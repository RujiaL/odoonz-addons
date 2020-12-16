# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.move"

    anglo_saxon_financial = fields.Boolean("Financial Only")
    anglo_saxon_accounting = fields.Boolean(related="company_id.anglo_saxon_accounting")

    @api.onchange("purchase_id")
    def change_vendor_bill_purchase_id_anglo_saxon(self):
        """
        When we add a purchase order to a manually created invoice
        we know we want anglosaxon, unless we are recharging on
        behalf of another company
        """
        if not self.purchase_id:
            return {}
        if self.purchase_id.company_id == self.company_id:
            self.anglo_saxon_financial = False

    def toggle_financial(self):
        for record in self.filtered(lambda s: s.state == "draft"):
            record.anglo_saxon_financial = not record.anglo_saxon_financial
            if record.is_purchase_document(include_receipts=True):
                for line in record.invoice_line_ids:
                    if line.product_id:
                        line.account_id = (
                            line._get_computed_account() or line.account_id
                        )
            if record.is_sale_document(include_receipts=True):
                journal_entries = record.line_ids.filtered(
                    lambda line: line.exclude_from_invoice_tab
                )
                receivable_line = record.line_ids.filtered(
                    lambda line: line.account_id.user_type_id.type == "receivable"
                )
                tax_line = record.line_ids.filtered(lambda line: line.tax_line_id)
                (journal_entries - receivable_line - tax_line).unlink()

    def _stock_account_prepare_anglo_saxon_in_lines_vals(self):
        filtered_self = self.filtered(lambda s: not s.anglo_saxon_financial)
        return super(
            AccountInvoice, filtered_self
        )._stock_account_prepare_anglo_saxon_in_lines_vals()

    def _stock_account_prepare_anglo_saxon_out_lines_vals(self):
        filtered_self = self.filtered(lambda s: not s.anglo_saxon_financial)
        return super(
            AccountInvoice, filtered_self
        )._stock_account_prepare_anglo_saxon_out_lines_vals()

    def _stock_account_anglo_saxon_reconcile_valuation(self, product=False):
        new_self = self.filtered(lambda s: not s.anglo_saxon_financial)
        if new_self:
            super(
                AccountInvoice, new_self
            )._stock_account_anglo_saxon_reconcile_valuation(product=product)


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    def _get_computed_account(self):
        """
        We override stock_account function to return the expense account
        for inwards invoices and refunds.
        Note: Context is checked as this method could arguably be called from
        an empty recordset (although it never is in core)
        :param type:
        :param product:
        :param fpos:
        :param company:
        :return: an account
        """
        try:
            if (
                self.move_id.journal_id.company_id.anglo_saxon_accounting
                and (
                    self.move_id.anglo_saxon_financial
                    or self.env.context.get("anglo_saxon_financial")
                )
                and self.move_id.is_purchase_document(include_receipts=True)
                and self.product_id
                and self.product_id.type == "product"
            ):
                return self.product_id.product_tmpl_id.get_product_accounts(
                    fiscal_pos=self.move_id.fiscal_position_id
                )["expense"]
        except AttributeError:
            pass
        return super()._get_computed_account()
