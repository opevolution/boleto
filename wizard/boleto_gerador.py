# -*- coding: utf-8 -*-
import logging
from openerp.osv import fields, osv
from datetime import date

_logger = logging.getLogger(__name__)

class boleto_gerador(osv.osv_memory):

    _name = "boleto.boleto_gerador"
    _description = "Gera Boletos a Partir das Faturas"
    
    _columns = {
        'bol_cp_config_ids': fields.many2one('boleto.company_config', 'Configuração', required=True),
        'state': fields.selection([('init', 'init'),
                               ('done', 'done')], 'state', readonly=True),
        }

    _defaults = {
        'state': 'init',
        }

    def gera_boleto(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        _logger.info("Inciando a Geração dos Boletos")
        data = self.read(cr, uid, ids, ['bol_cp_config_ids'], context=context)[0]
        bol_conf_id = data['bol_cp_config_ids'][0]
        _logger.info("bol_conf_id: "+str(bol_conf_id))
        inv_obj = self.pool.get('account.invoice')
        boleto_obj = self.pool.get('boleto.boleto')
        active_ids = context.get('active_ids',[])
        boleto_ids = []
        
        for invoice in inv_obj.browse(cr, uid, active_ids, context=context):
            company = self.pool.get('res.company').browse(cr, uid, [invoice.company_id.id])[0]
            #bank_lines = [y for y in company.bank_ids]
            bank_id = False
            for bank in company.bank_ids:
                if bank.company_id.id == company.id and bank.default_bank:
                    bank_id = bank.id
                    break
            _logger.info("bank_id: "+str(bank_id))
            if bank_id != False:
                partner = self.pool.get('res.partner').browse(cr, uid, [invoice.partner_id.id])[0]
                bol_conf = self.pool.get('boleto.company_config').browse(cr, uid, [bol_conf_id])[0]
                _logger.info("bol_conf: "+str(bol_conf['name']))
                
                if invoice.state in ['proforma2', 'open']:
                    _logger.info("Abrindo fatura "+invoice.number)
                    data_lines = [x for x in invoice.move_id.line_id if x.account_id.id == invoice.account_id.id and x.account_id.type in ('receivable', 'payable')]
                    for line in data_lines:
                        _logger.info("Criando Boleto para a Linha "+line.name)
            #        rec_ids = invoice._get_receivable_lines(active_ids, False, context)
            #        for move_line in self.pool.get('account.move.line').browse(cr, uid, rec_ids[got multiple values for keywordinvoice.id]):
                        boleto = {
                                  'name': invoice.number + '-' + str(line.id),
                                  'carteira': partner.boleto_partner_config.carteira,
                                  'cedente': company.id,
                                  'sacado': partner.id,
                                  'juros': partner.boleto_partner_config.juros,
                                  'multa': partner.boleto_partner_config.multa,
                                  'instrucoes': partner.boleto_partner_config.instrucoes,
                                  'banco': bol_conf.banco,
                                  'agencia_cedente': bol_conf.agencia_cedente,
                                  'conta_cedente': bol_conf.conta_cedente,
                                  'convenio': bol_conf.convenio,
                                  'nosso_numero': (int(invoice.number) * 100) + line.id,
                                  'move_line_id': line.id,
                                  'data_vencimento': line.date_maturity or date.today(),
                                  'data_documento': line.date_created,
                                  'valor': line.debit,
                                  'numero_documento': line.id,
                                  'endereco': partner.street,
                                  'state': 'novo'
                                }
                        _logger.info("boleto: "+str(boleto['name']))
                        _logger.info("banco: "+str(boleto['banco']))
                        _logger.info("agencia_cedente: "+str(boleto['agencia_cedente']))
                        _logger.info("conta_cedente: "+str(boleto['conta_cedente']))
                        _logger.info("carteira: "+str(boleto['carteira']))
                        #s_logger.info("sacado: "+str(boleto['sacado']))
                        _logger.info("nosso_numero: "+str(boleto['nosso_numero']))
                        _logger.info("endereco: "+str(boleto['endereco']))
                        #boleto_id = boleto_obj.create(cr, uid, boleto, context)
                        #boleto_ids.append(boleto_id)

        _logger.info("Finalizando a Geração dos Boletos")
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        
        return False

boleto_gerador()            