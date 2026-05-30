{
    'name': 'HT Beauty Core',
    'version': '1.0',
    'category': 'HT Beauty',
    'author': 'Nhóm F',
    'license': 'LGPL-3',
    'summary': 'Phần mềm Quản lý Viện thẩm mỹ HT Beauty',
    'description': """
        Module chứa các dữ liệu nền tảng và phân quyền cho HT Beauty.
        Mở rộng các tính năng Khách hàng, Nhân sự và Quản lý Phòng điều trị.
    """,
    'depends': [
        'base',
        'crm',
        'hr',
        'sale_management',
        'website_crm',
        'mail',
        'loyalty'
    ],
    'data': [
        'security/beauty_security.xml',
        'security/ir.model.access.csv',
        'data/crm_stage_data.xml',
        'data/beauty_service_data.xml',
        'data/beauty_room_data.xml',
        'views/beauty_room_views.xml',
        'views/hr_employee_views.xml',
        'views/res_partner_views.xml',
        'views/beauty_menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}