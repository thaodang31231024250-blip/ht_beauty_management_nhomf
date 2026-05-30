from odoo import models, fields, api
from datetime import timedelta

class BeautyTreatmentSession(models.Model):
    _inherit = 'beauty.treatment.session'

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            # 11.5: Khách hàng làm xong dịch vụ -> Sinh task CSKH
            if 'state' in vals and vals['state'] == 'done':
                rec._create_post_treatment_care_task()
        return res

    def _create_post_treatment_care_task(self):
        """Tự động tạo To-do Gọi điện cho bộ phận CSKH vào ngày hôm sau"""
        cskh_group = self.env.ref('ht_beauty_core.beauty_group_cskh', raise_if_not_found=False)
        
       
        cskh_users = self.env['res.users'].search([('groups_id', 'in', cskh_group.ids)]) if cskh_group else []
        
        if cskh_users:
            assigned_user = cskh_users[0]
            deadline_date = fields.Date.context_today(self) + timedelta(days=1)
            
            self.activity_schedule(
                'mail.mail_activity_data_call',
                summary='Gọi hỏi thăm sau điều trị',
                note=f"""
                    <b>Chăm sóc khách sau điều trị:</b><br/>
                    - Khách hàng: {self.partner_id.name}<br/>
                    - Buổi thực hiện: {self.name}<br/>
                    <i>Yêu cầu: Gọi điện hỏi thăm tình trạng da của khách, có kích ứng gì sau khi làm dịch vụ không, và nhắc khách dùng dưỡng da đúng cách.</i>
                """,
                user_id=assigned_user.id,
                date_deadline=deadline_date
            )