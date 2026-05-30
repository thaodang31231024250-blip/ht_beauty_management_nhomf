# -*- coding: utf-8 -*-
from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            # Filter service lines only
            service_lines = order.order_line.filtered(
                lambda l: l.product_id and l.product_id.type == 'service' and not l.display_type
            )
            if not service_lines:
                continue

            # Create treatment plan
            plan = self.env['beauty.treatment.plan'].create({
                'partner_id': order.partner_id.id,
            })

            # Create plan lines from SO service lines
            for line in service_lines:
                self.env['beauty.treatment.plan.line'].create({
                    'plan_id': plan.id,
                    'product_id': line.product_id.id,
                    'name': line.name or line.product_id.name,
                    'quantity': line.product_uom_qty,
                    'price_unit': line.price_unit,
                })
        return res
