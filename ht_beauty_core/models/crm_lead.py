from odoo import models, fields

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    zalo_link = fields.Char(string='Link Zalo', related='partner_id.zalo_link', readonly=False, store=True)
    consultation_note = fields.Html(string='Ghi chú tư vấn')