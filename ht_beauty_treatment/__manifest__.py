{
    'name': 'HT Beauty Treatment',
    'version': '1.0',
    'category': 'HT Beauty',
    'author': 'Nhóm F',
    'summary': 'Phần mềm quản lý phác đồ và nhật ký điều trị cho HT Beauty',
    'description': """
        Module quản lý vòng đời điều trị cho HT Beauty:
        - Phác đồ điều trị
        - Phân loại Tag & Dịch vụ
        - Nhật ký từng buổi
    """,
    'depends': ['ht_beauty_core', 'sale_management', 'ht_beauty_appointment'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/bulk_appointment_wizard_views.xml',
        'views/treatment_plan_views.xml',
        'views/treatment_session_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'license': 'LGPL-3',
}