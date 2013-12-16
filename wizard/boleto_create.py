# -*- coding: utf-8 -*-
import logging
#import tempfile
import base64
import time
from osv import osv, fields
from pyboleto.bank.real import BoletoReal
from pyboleto.bank.bradesco import BoletoBradesco
from pyboleto.bank.caixa import BoletoCaixa
from pyboleto.bank.bancodobrasil import BoletoBB
from pyboleto.pdf import BoletoPDF
from datetime import datetime, date
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

_logger = logging.getLogger(__name__)

class boleto_create(osv.osv_memory):
    """ Generate Brazilian Boletos """

    _name = 'boleto.boleto_create'
    #_inherit = "ir.wizard.screen"

    _columns = {
        'file': fields.binary('Arquivo', readonly=True),
        'file_name': fields.char('Nome do Arquivo', 40, readonly=True),
        'state': fields.selection([('init', 'init'),
                                   ('get','get'),
                                   ('done','done')], 'state', readonly=True),
        }

    _defaults = {
        'state': 'init',
        }

    def anexarFicheiro(self,cr,uid,ids,conteudo,context={}):
        _logger.info("Anexando Boleto")
        nome='Boleto_'+time.strftime('%Y%m%d_%H%M%S')+'.pdf'
        attach_id=self.pool.get('ir.attachment').create(cr, uid, {
                                                'name': nome,
                                                'datas': base64.encodestring(conteudo),
                                                'datas_fname': nome,
                                                'res_model': 'boleto.boleto',
                                                'res_id': ids,
                                                }, context=context)
        return True

    def create_boleto(self, cr, uid, ids, context=None):
        _logger.info("Inciando a Geracao do(s) PDF(s)")    
        if context is None:
            context = {}
        #arquivo = tempfile.NamedTemporaryFile(prefix='boleto',suffix='.pdf', delete=False)

        boleto_obj = self.pool.get('boleto.boleto')
        active_ids = context.get('active_ids', [])
        
        for bol in boleto_obj.browse(cr, uid, active_ids, context=context):
            
            boleto_id = bol.id
            _logger.info("Gerando PDF do boleto %s" % boleto_id)
            
            fbuffer = StringIO()
            boleto_pdf = BoletoPDF(fbuffer)

            company = self.pool.get('res.company').browse(cr, uid, [bol.cedente.id])[0]
            partner = self.pool.get('res.partner').browse(cr, uid, [bol.sacado.id])[0]
            if partner.legal_name:
                partner_name = partner.legal_name
            else:
                partner_name =  partner.name
            #partner_ad = partner.address[0]
            #bol_conf_id = company.boleto_company_config_ids.id
            #bol_conf = self.pool.get('boleto.company_config').browse(cr, uid, [bol_conf_id])[0]
            
            
            if bol.banco == 'bb':
                boleto = BoletoBB(7, 2)
            elif bol.banco == 'bradesco':
                boleto = BoletoBradesco()
            elif bol.banco == 'caixa':
                boleto = BoletoCaixa()
            elif bol.banco == 'real':
                boleto = BoletoReal()
            boleto.cedente = company.name
            boleto.cedente_documento = company.company_registry
            boleto.cedente_logradouro = company.street
            boleto.cedente_cep = company.zip
            boleto.cedente_cidade = company.city
            boleto.carteira = bol.carteira
            boleto.agencia_cedente = bol.agencia_cedente
            boleto.conta_cedente = bol.conta_cedente
            boleto.data_vencimento = datetime.date(datetime.strptime(bol.data_vencimento, '%Y-%m-%d'))
            boleto.data_documento = datetime.date(datetime.strptime(bol.data_documento, '%Y-%m-%d'))
            boleto.data_processamento = date.today()
            boleto.valor_documento = bol.valor
            boleto.nosso_numero = bol.numero_documento
            boleto.numero_documento = bol.numero_documento
            boleto.convenio = bol.convenio
            boleto.instrucoes = bol.instrucoes.split()
            boleto.sacado_documento = partner.cnpj_cpf
            boleto.sacado = [
                partner_name,
                bol.endereco,
                ""
                ]
#            boleto.sacado = [
#                "%s" % partner.legal_name or partner.name,
#                "%s, %s - %s - %s - Cep. %s" % (partner_ad.street, partner_ad.number, partner_ad.district, partner_ad.city, partner_ad.zip),
#                ""
#                ]
            boleto_pdf.drawBoleto(boleto)
            boleto_pdf.nextPage()

            boleto_pdf.save()
        #boleto_pdf.pdfCanvas.showPage()
        #arquivo.seek(0)
        #fl = arquivo.read()
        
        #boleto_file = fbuffer.getvalue().encode("base64")

            fbuffer.seek(0)
            conteudo = fbuffer.read()
            self.anexarFicheiro(cr,uid,boleto_id,conteudo) 
               
        #self.write(cr,uid,ids,{'file': base64.b64encode(fl),  'state': 'done'}, context=context)
        #fbuffer.seek(0)
        #print fbuffer.read()
            fbuffer.close()
            self.write(cr, uid, ids, {'state': 'done'}, context=context)
        #arquivo.close()
        
        _logger.info("Finalizando a Geracao do PDF 7")
                
        #self.write(cr, uid, ids, {'file': boleto_file, 'state': 'get'}, context=context)
        return False
        #return self.write(cr, uid, ids, {'state':'get', 'file':boleto_file, 'file_name':'Test.pdf'}, context=context)
        #return boleto_file
        #return self.write(cr, uid, ids, {'state':'get', 'data':boleto_file, 'name':'export.pdf'}, context=context)

boleto_create()
