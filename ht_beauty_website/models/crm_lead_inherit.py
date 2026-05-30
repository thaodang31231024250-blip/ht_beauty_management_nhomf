from odoo import fields, models


class CrmLeadInherit(models.Model):
    _inherit = 'crm.lead'

    # Trường mở rộng nếu cần sau này (ví dụ: zalo, nguồn website,...)
    ht_source_page = fields.Char(
        string='Trang nguồn',
        help='Trang website mà khách hàng đã gửi form',
        default='website_contact',
    )
