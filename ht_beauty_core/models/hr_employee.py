from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    role_type = fields.Selection([
        ('doctor', 'Bác sĩ'),
        ('ktv', 'Kỹ thuật viên'),
        ('receptionist', 'Lễ tân'),
        ('cskh', 'CSKH')
    ], string='Vị trí công việc', required=True)
    
    specialization = fields.Selection([
        ('dieu_tri_da', 'Điều trị da'),
        ('dieu_tri_mun', 'Điều trị mụn'),
        ('nang_co_tre_hoa', 'Nâng cơ - Trẻ hóa da'),
        ('triet_long', 'Triệt lông vĩnh viễn'),
        ('cham_soc_da', 'Chăm sóc - Phục hồi da'),
], string='Chuyên môn')