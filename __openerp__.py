# -*- coding: utf-8 -*-

{
    "name": "Boletos",
    "version": "0.1",
    "author": "Alexandre Defendi",
    "category": "Account",
    "website": "http://evoluirinformatica.com.br",
    "description": """
    Module to create brazilian boletos.
    Company Boleto conf in menu Administration->Company->boletos
    Partner Boleto conf in Partner form.
    Wizard to generate boletos in Invoice form.
    """,
    'depends': ['account','l10n_br_base','account_payment',],
    'js': [],
    'init_xml': [],
    'update_xml': [
        'boleto_view.xml',
        'partner_view.xml',
        'res_partner_view.xml',
        'wizard/boleto_create_view.xml',
        'wizard/boleto_gerador_view.xml',
        ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
