import logging
from odoo import http
from odoo.http import request
_logger = logging.getLogger(__name__)
class HTBeautyWebsite(http.Controller):
    # ------------------------------------------------------------------ #
    #  TRANG LIÊN HỆ                                                       #
    # ------------------------------------------------------------------ #
    @http.route('/lien-he', type='http', auth='public', website=True)
    def contact_us_page(self, **kwargs):
        services = request.env['product.product'].sudo().search([
            ('type', '=', 'service'),
            ('sale_ok', '=', True),
        ])
        selected_service_id = kwargs.get('service_id')
        values = {
            'services': services,
            'selected_service_id': (
                int(selected_service_id)
                if selected_service_id and str(selected_service_id).isdigit()
                else False
            ),
        }
        return request.render('ht_beauty_website.contact_us_template', values)
    @http.route(
        '/lien-he/submit',
        type='http',
        auth='public',
        website=True,
        methods=['POST'],
        csrf=True,
    )
    def contact_us_submit(self, **post):
        if not post:
            return request.redirect('/lien-he')
        try:
            lead_vals = {
                'name': f"Website Lead: {post.get('contact_name', '').strip() or 'Khách hàng'}",
                'contact_name': post.get('contact_name', '').strip(),
                'phone': post.get('phone', '').strip(),
                'description': post.get('description', '').strip(),
                'type': 'lead',
                'source_id': request.env.ref(
                    'utm.utm_source_website', raise_if_not_found=False
                ) and request.env.ref('utm.utm_source_website').id or False,
            }
            # Gắn tên dịch vụ vào description nếu có chọn
            service_id = post.get('service_id')
            if service_id and str(service_id).isdigit():
                service = request.env['product.product'].sudo().browse(int(service_id))
                if service.exists():
                    existing_desc = lead_vals.get('description', '')
                    lead_vals['description'] = (
                        f"Dịch vụ quan tâm: {service.name}\n\n{existing_desc}".strip()
                    )
            request.env['crm.lead'].sudo().create(lead_vals)
            return request.render('ht_beauty_website.contact_success_template', {})
        except Exception as e:
            _logger.error("HTBeauty - Lỗi tạo CRM Lead: %s", str(e), exc_info=True)
            return request.render('ht_beauty_website.contact_us_template', {
                'services': request.env['product.product'].sudo().search([
                    ('type', '=', 'service'),
                    ('sale_ok', '=', True),
                ]),
                'selected_service_id': False,
                'error_message': 'Đã có lỗi xảy ra, vui lòng thử lại hoặc liên hệ trực tiếp với chúng tôi.',
            })
    # ------------------------------------------------------------------ #
    #  TRANG DỊCH VỤ                                                       #
    # ------------------------------------------------------------------ #
    @http.route('/dich-vu', type='http', auth='public', website=True)
    def services_page(self, **kwargs):
        services = request.env['product.product'].sudo().search([
            ('type', '=', 'service'),
            ('sale_ok', '=', True),
        ])
        categories = request.env['product.category'].sudo().search([])
        active_categories = categories.filtered(
            lambda c: any(s.categ_id.id == c.id for s in services)
        )
        values = {
            'categories': active_categories,
            'services': services,
        }
        return request.render('ht_beauty_website.services_template', values)