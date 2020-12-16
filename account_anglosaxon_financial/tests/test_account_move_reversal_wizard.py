# Copyright 2020 Rujia Liu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import Form

from odoo.addons.account.tests.account_test_savepoint import AccountTestInvoicingCommon


class TestAccountMoveReversal(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.invoice = cls.init_invoice("in_invoice")

    def setUp(self):
        super(TestAccountMoveReversal, self).setUp()
        self.company = self.company_data["company"]

    def test_compute_anglo_saxon_state(self):
        self.invoice.company_id.anglo_saxon_accounting = False
        self.invoice.post()

        amr = self.env["account.move.reversal"]
        amr1_form = Form(
            amr.with_context(active_ids=self.invoice.ids, active_model="account.move")
        )
        amr1_form.refund_method = "refund"
        self.assertFalse(amr1_form.anglo_saxon_accounting)
        amr1_form.save()

        # test amr without active_ids,
        # for some reason if there is no active_ids
        # refund_method is a read only field
        # but the test is still working as expected
        self.company.anglo_saxon_accounting = True
        amr2_form = Form(amr)
        self.assertTrue(amr2_form.anglo_saxon_accounting)
        amr2_form.save()
