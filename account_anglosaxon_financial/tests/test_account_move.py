# Copyright 2020 Rujia Liu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import Form

# from odoo.addons.account.tests.account_test_savepoint
# import AccountTestInvoicingCommon
from odoo.addons.sale_stock.tests.test_anglo_saxon_valuation import (
    TestAngloSaxonValuation,
)


class TestAccountMove(TestAngloSaxonValuation):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        # cls.in_invoice = cls.init_invoice('in_invoice')
        # cls.out_invoice = cls.init_invoice('out_invoice')
        cls.product_a = cls.product.copy()
        cls.product_a.categ_id = cls.env.ref("product.product_category_1").id
        cls.product_a.standard_price = 10.0
        cls.product_a.lst_price = 10.0

        cls.product_b = cls.product = cls.env["product.product"].create(
            {
                "name": "product_b",
                "type": "consu",
                "standard_price": 5.0,
                "lst_price": 5.0,
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )

    def setUp(self):
        super(TestAccountMove, self).setUp()

    def test_in_lines_prepare_anglo_saxon(self):
        # Init in_invoice: financial only
        in_invoice_form = Form(
            self.env["account.move"].with_context(default_type="in_invoice")
        )
        in_invoice_form.partner_id = self.env.ref("base.res_partner_2")
        in_invoice_form.anglo_saxon_financial = True
        with in_invoice_form.new() as line:
            line.product_id = self.product_a
        in_invoice = in_invoice_form.save()
        in_invoice.post()

        amls = in_invoice.line_ids
        self.assertEqual(len(amls), 2)
        # stock_out_aml = amls.filtered(
        #     lambda aml: aml.account_id == self.stock_output_account
        # )
        pass
