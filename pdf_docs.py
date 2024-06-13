# -*- coding: utf-8 -*-

# Python libraries: NF-e utils
#
# Copyright (C) 2021-2022
# Copyright (C) Edson Bernardino <edsones at yahoo.com.br>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Library General Public License as
# published by the Free Software Foundation, either version 2.1 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# pdf_docs - Módulo Python NF-e utils

#
# Copyright (C) 2021-2022
# Copyright (C) Edson Bernardino <edsones arroba yahoo.com.br>
#
# Este programa é um software livre: você pode redistribuir e/ou modificar
# este programa sob os termos da licença GNU Library General Public License,
# publicada pela Free Software Foundation, em sua versão 2.1 ou, de acordo
# com sua opção, qualquer versão posterior.
#
# Este programa é distribuido na esperança de que venha a ser útil,
# porém SEM QUAISQUER GARANTIAS, nem mesmo a garantia implícita de
# COMERCIABILIDADE ou ADEQUAÇÃO A UMA FINALIDADE ESPECÍFICA. Veja a
# GNU Library General Public License para mais detalhes.
#
# Você deve ter recebido uma cópia da GNU Library General Public License
# juntamente com este programa. Caso esse não seja o caso, acesse:
# <http://www.gnu.org/licenses/>
#

"""
    Geração documentos auxiliares
    
    DANFE - Nota Fiscal Eletrônica
    DACCe - carta correção
    DACTe - Conhecimento de Transporte  TO DO
        
    :copyright: © 2022 by Edson Bernardino
    :license: BSD, see LICENSE for more details.
"""

import datetime
import re
import xml.etree.ElementTree as ET
from xfpdf import xFPDF


def getdateUTC(date_utc):
   dt = date_utc[0:10].split('-')
   dt.reverse()
   return '/'.join(dt), date_utc[11:19]               


def get_tag_text(node=None, url='', tag=None):
    try:
        text = node.find("%s%s" % (url, tag)).text
    except:
        text = ''
    return text

def number_filter(doc):
    # Remove todos os caracteres que não são dígitos
    return re.sub(r"\D", "", doc)

def format_cpf_cnpj(doc):
    doc = number_filter(doc) 
    if doc:
        if len(doc) > 11:         
            doc = '{:0>14.14}'.format(doc)    
            doc = '{}.{}.{}/{}-{}'.format(doc[:2], 
                                          doc[2:5], 
                                          doc[5:8], 
                                          doc[8:12], 
                                          doc[-2:])
        else:
            doc = '{:0>11.11}'.format(doc)
            doc = '{}.{}.{}-{}'.format(doc[:3], doc[3:6], doc[6:9], doc[9:])
                                                                              
    return doc

 
def chunks(cString, nLen):
   for start in range(0, len(cString), nLen):
      yield cString[start:start+nLen]


def format_number(cNumber, precision=0, group_sep='.', decimal_sep=','):
    try:
        number = ("{:,." + str(precision) + "f}").format(
            float(cNumber)).replace(",", "X").replace(".", ",").replace("X",".")
    except:
        number = ''
    return number

 
tp_frete = {'0': '0 - Emitente', 
            '1': '1 - Dest/Rem', 
            '2': '2 - Terceiros', 
            '3': '3 - Próprio/Rem',
            '4': '4 - Próprio/Dest',
            '9': '9 - Sem Frete'}


url = './/{http://www.portalfiscal.inf.br/nfe}'

# layouts colunas dados produtos
                
headers = ['CÓDIGO', 'DESCRIÇÃO DO PRODUTO/SERVIÇO', 'NCM/SH', 'CST', 'CFOP', 
           'UNID', 'QTD', 'VLR UNIT', 'VLR TOTAL', 'BC ICMS']

# ICMS - Variantes layout (Padrão)
headers_0 = ['VLR. ICMS', 'ALÍQ\nICMS']

# ICMS_ST-  Variantes layout
headers_1 = ['BC ICMS ST', 'VLR ICMS ST', 'VLR ICMS', 'ALÍQ\nICMS']

# ICMS_IPI - Variantes layout
headers_2 = ['VLR. ICMS', 'VLR. IPI', 'ALÍQ\nICMS', 'ALÍQ\nIPI']

# ICMS_ST_IPI - Variantes layout
headers_3 = ['BC ICMS ST', 'VLR ICMS ST', 'VLR ICMS', 'VLR. IPI', 'ALÍQ\nICMS', 
             'ALÍQ\nIPI']

                              
cells = [
    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, get_tag_text(
        node=kwargs['node_item'], url=url, tag='cProd'), 0, 0, 'L'),
        
    lambda **kwargs: kwargs['report'].desc_item(list_desc=kwargs['desc_item'], 
        width=kwargs['width']),

    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, get_tag_text(
        node=kwargs['node_item'], url=url, tag='NCM'), 0, 0, 'C'),
                    
    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, '%s%s' % (
        get_tag_text(node=kwargs['node_icms'], url=url, tag='orig'), 
        (get_tag_text(node=kwargs['node_icms'], url=url, tag='CST') or \
        get_tag_text(node=kwargs['node_icms'], url=url, tag='CSOSN'))), 
        0, 0, 'C'),

    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, get_tag_text(
        node=kwargs['node_item'], url=url, tag='CFOP'), 0, 0, 'C'),

    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, get_tag_text(
        node=kwargs['node_item'], url=url, tag='uCom'), 0, 0, 'C'),

    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, format_number(
        get_tag_text(node=kwargs['node_item'], url=url, tag='qCom'), 
        precision=4), 0, 0, 'R'),

    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, format_number(
        get_tag_text(node=kwargs['node_item'], url=url, tag='vUnCom'), 
        precision=2), 0, 0, 'R'),

    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, format_number(
        get_tag_text(node=kwargs['node_item'], url=url, tag='vProd'), 
        precision=2), 0, 0, 'R'),

    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, format_number(
        get_tag_text(node=kwargs['node_icms'], url=url, tag='vBC'), 
        precision=2), 0, 0, 'R'),
]

# ICMS - Variantes layout (Padrão)                            
cells_0 = [
    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, format_number(
        get_tag_text(node=kwargs['node_icms'], url=url, tag='vICMS'), 
        precision=2), 0, 0, 'R'),

    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, format_number(
        get_tag_text(node=kwargs['node_icms'], url=url, tag='pICMS'), 
        precision=2), 0, 0, 'R'),                
]
           
# ICMS_ST-  Variantes layout
cells_1 = [
    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, format_number(
        get_tag_text(node=kwargs['node_icms'], url=url, tag='vBCST'), 
        precision=2), 0, 0, 'R'),

    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, format_number(
        get_tag_text(node=kwargs['node_icms'], url=url, tag='vICMSST'), 
        precision=2), 0, 0, 'R'),

    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, format_number(
        get_tag_text(node=kwargs['node_icms'], url=url, tag='vICMS'), 
        precision=2), 0, 0, 'R'),

    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, format_number(
        get_tag_text(node=kwargs['node_icms'], url=url, tag='pICMS'), 
        precision=2), 0, 0, 'R'),
]

# ICMS_IPI - Variantes layout
cells_2 = [
    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, format_number(
        get_tag_text(node=kwargs['node_icms'], url=url, tag='vICMS'), 
        precision=2), 0, 0, 'R'),

    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, format_number(
        get_tag_text(node=kwargs['node_ipi'], url=url, tag='vIPI'), 
        precision=2), 0, 0, 'R'),

    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, format_number(
        get_tag_text(node=kwargs['node_icms'], url=url, tag='pICMS'), 
        precision=2), 0, 0, 'R'),

    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, format_number(
        get_tag_text(node=kwargs['node_ipi'], url=url, tag='pIPI'), 
        precision=2), 0, 0, 'R'),

]

# ICMS_ST_IPI -  Variantes layout
cells_3 = [
    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, format_number(
        get_tag_text(node=kwargs['node_icms'], url=url, tag='vBCST'), 
        precision=2), 0, 0, 'R'),

    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, format_number(
        get_tag_text(node=kwargs['node_icms'], url=url, tag='vICMSST'), 
        precision=2), 0, 0, 'R'),

    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, format_number(
        get_tag_text(node=kwargs['node_icms'], url=url, tag='vICMS'), 
        precision=2), 0, 0, 'R'),

    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, format_number(
        get_tag_text(node=kwargs['node_ipi'], url=url, tag='vIPI'), 
        precision=2), 0, 0, 'R'),

    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, format_number(
        get_tag_text(node=kwargs['node_icms'], url=url, tag='pICMS'), 
        precision=2), 0, 0, 'R'),

    lambda **kwargs: kwargs['report'].cell(kwargs['width'], 3, format_number(
        get_tag_text(node=kwargs['node_ipi'], url=url, tag='pIPI'), 
        precision=2), 0, 0, 'R'),

]


cols_produtos_portable = {                                         

    'ICMS': [[11, 72, 13, 7, 7, 8, 13, 13, 15, 12, 12, 7], 
             headers + headers_0,
             cells + cells_0],        

    'ICMS_ST': [[11, 48, 13, 6.5, 6.5, 8, 13, 13, 15, 12, 12, 13, 12,7],
                headers + headers_1,
                cells + cells_1],
            
    'ICMS_IPI': [[11, 54, 13, 7, 7, 8, 13, 13, 14, 12, 12, 12, 7, 7],
                 headers + headers_2,
                 cells + cells_2],

    }

cols_produtos_landscape = {                                         
            
    'ICMS_ST_IPI': [[22, 72, 13, 7, 7, 8, 13, 13, 14, 12, 12, 13, 12, 12, 9, 9],
                    headers + headers_3,
                    cells + cells_3],

    }

# Recebe list xmls em string e image base64 - Modo retrato ou paisagem
class Danfe(xFPDF):
    def __init__(self, xmls=None, image=None, cfg_layout='ICMS_ST', 
        receipt_pos='top'):
         
        super(Danfe, self).__init__('P', 'mm', 'A4')     
        
        self.set_auto_page_break(auto=False, margin=10.0)
        
        self.set_title('DANFE')
        #self.add_font('NimbusSanLBold', '', 'NimbusSanLBold.ttf', uni=True)
        #self.add_font('NimbusSanL', '', 'NimbusSanL.ttf', uni=True)
        self.logo_image = image
        self.receipt_pos = receipt_pos
                        
        if xmls is None:
            raise NameError('XML não informado!')
        
        if not isinstance(xmls, list):
            xmls = [xmls]                
        
        self.tasks = {'P': [lambda: self.recibo_p(),                
                            lambda: self.emit_p(),
                            lambda: self.dest_p(),
                            lambda: self.fat_p(),
                            lambda: self.impostos_p(),
                            lambda: self.transp_p(),                            
                            lambda: self.adic_p(),                            
                           ],
                            
                      'L': [lambda: self.recibo_l(),
                            lambda: self.emit_l(),
                            lambda: self.dest_l(),
                            lambda: self.fat_l(),
                            lambda: self.impostos_l(),
                            lambda: self.transp_l(),
                            lambda: self.adic_l(),                                            
                           ]
                     } 
        
        for xml in xmls:
                        
            root = ET.fromstring(xml)
            
            self.inf_nfe = root.find("%sinfNFe" % url)
            self.prot_nfe = root.find("%sprotNFe" % url)
            self.emit = root.find("%semit" % url)
            self.ide = root.find("%side" % url)
            self.dest = root.find("%sdest" % url)            
            self.totais = root.find("%stotal" % url)
            self.transp = root.find("%stransp" % url)
            self.cobr = root.find("%scobr" % url) 
            self.det = root.findall("%sdet" % url)
            self.inf_adic = root.find("%sinfAdic" % url)
                                    
            # Buscando orientação de impressão do xml
            tpImp = get_tag_text(node=self.ide, url=url, tag='tpImp')            
            if tpImp == '1':
                orientation = 'P'
                nr_lin_pg_1 = 23
                nr_lin_pg = 70
                
                if self.receipt_pos == 'top':
                    self.lin_emit = 31
                    self.lin_prod = 161
                else:
                    self.lin_emit = 10
                    self.lin_prod = 140

                self.lin_adic = self.lin_emit + 209.5
                self.height_adic = 29
                    
                self.cols_produtos = cols_produtos_portable[cfg_layout]
                  
            else: 
                orientation = 'L'
                nr_lin_pg_1 = 6
                nr_lin_pg = 45
                self.lin_emit = 10
                self.lin_prod = 134
                self.cols_produtos = cols_produtos_landscape['ICMS_ST_IPI']
                
            self.add_page(orientation=orientation, format='A4')
            
            # Calculando total linhas usadas para descrições dos itens
            self.nr_pages = 1
            self.current_page = 1
                                                                   
            #[ rec_ini , rec_fim , lines , limit_lines ]
            paginator = [[0, 0, 0, nr_lin_pg_1]]

            if self.det is not None:

                list_desc = []
                n_pg = 0                  
                for id_ , item in enumerate(self.det):
                    el_prod = item.find(
                        ".//{http://www.portalfiscal.inf.br/nfe}prod")
                    inf_add = item.find(
                        ".//{http://www.portalfiscal.inf.br/nfe}infAdProd")
                    
                    # Width da coluna descrição produto                  
                    self.set_font('Times', '', 6)
                    col_w = self.cols_produtos[0][1]                                                            
                    list_ = self.multi_cell(w=col_w, h=3, txt=get_tag_text(
                        node=el_prod, url=url, tag='xProd'), split_only=True)                  
                                                             
                    if inf_add is not None:
                        list_.extend(self.multi_cell(w=col_w, h=3, 
                            txt=inf_add.text, split_only=True))
                        
                    list_desc.append(list_)
                    
                    # Nr linhas necessárias p/ descrição item
                    lin_itens = len(list_) 
               
                    if (paginator[n_pg][2] + lin_itens) > paginator[n_pg][3]:
                        paginator.append([0, 0, 0, nr_lin_pg])
                        n_pg += 1
                        paginator[n_pg][0] = id_
                        paginator[n_pg][1] = id_ +1
                        paginator[n_pg][2] = lin_itens
                    else:
                        # adiciona-se 1 pelo funcionamento de xrange
                        paginator[n_pg][1] = id_ +1  
                        paginator[n_pg ][2] += lin_itens
                  
                self.nr_pages = len(paginator)   # Calculando nr. páginas
                              
                                            
            dt, hr = getdateUTC(
                get_tag_text(node=self.ide, url=url, tag='dhEmi'))
                                             
            total_nf = format_number(get_tag_text(
                            node=self.totais, url=url, tag='vNF'), precision=2)
                              
            end = "%s - %s, %s, %s, %s - %s" % (
                        get_tag_text(node=self.dest, url=url, tag='xNome'),
                        get_tag_text(node=self.dest, url=url, tag='xLgr'),
                        get_tag_text(node=self.dest, url=url, tag='nro'),
                        get_tag_text(node=self.dest, url=url, tag='xBairro'),
                        get_tag_text(node=self.dest, url=url, tag='xMun'),
                        get_tag_text(node=self.dest, url=url, tag='UF')                
                                            )

            self.recibo_txt = ("RECEBEMOS DE %s OS PRODUTOS/SERVIÇOS "
                               "CONSTANTES DA NOTA FISCAL INDICADA "
                               "ABAIXO. EMISSÃO: %s VALOR TOTAL: %s " 
                               "DESTINATARIO: %s" % (
                                        get_tag_text(node=self.emit, 
                                                     url=url, 
                                                     tag='xNome'),           
                                        dt, 
                                        total_nf, 
                                        end)
                              )
            
            self.nr_nota = get_tag_text(node=self.ide, url=url, tag='nNF')
            self.serie_nf = get_tag_text(node=self.ide, url=url, tag='serie')
            self.tp_nf = get_tag_text(node=self.ide, url=url, tag='tpNF')            
            self.key_nfe = self.inf_nfe.attrib.get('Id')[3:]
            
            dt, hr = getdateUTC(get_tag_text(
                node=self.prot_nfe, url=url, tag='dhRecbto'))             
            
            protocolo = get_tag_text(node=self.prot_nfe, url=url, tag='nProt')
            self.prot_uso = '%s - %s %s' % (protocolo, dt, hr)     

            self.current_page = 1
            
            #self.add_page(orientation=orientation, format='A4')
            for task in self.tasks[orientation]:
                task() 
            
            if tpImp == '1':
                self.produtos_p(paginator=paginator[0], list_desc=list_desc)
            else:
                self.produtos_l(paginator=paginator[0], list_desc=list_desc)
            
            # Gera o restante das páginas do XML
            if paginator[1:]:
                
                self.lin_emit = 11
                if tpImp == '1':
                    self.lin_prod = self.lin_emit +49
                else:
                    self.lin_prod = self.lin_emit +42
            
            for pag in paginator[1:]:
                self.current_page += 1
                self.add_page(orientation=orientation, format='A4')                            
                                                          
                if tpImp == '1':                                        
                    self.emit_p()
                    self.produtos_p(paginator=pag, list_desc=list_desc)
                else:
                    self.emit_l()
                    self.produtos_l(paginator=pag, list_desc=list_desc)
                
    def recibo_p(self):
        
        if self.receipt_pos == 'top':
            lin = 10
            self.dashed_line(10, lin +19, 200, lin +19, dash_length=0.5, 
                space_length=1)
        else:
            lin = self.lin_adic + self.height_adic +2
            self.dashed_line(10, lin, 200, lin, dash_length=0.5, space_length=1)
            lin += 2
                                                                                            
        self.rect(x=10, y=lin, w=190, h=17, style='')
        self.line(10, lin +8.5, 160, lin +8.5)
        self.line(160, lin, 160, lin +17)
        self.line(54, lin +8.5, 54, lin +17)
        
        self.set_font('Times', '', 5)
        self.set_xy(x=10, y=lin)
        self.multi_cell(w=150, h=3, txt=self.recibo_txt, border=0, 
                        align='L', fill=False)                  
        
        self.text(x=11, y=lin +10.5, txt='DATA DE RECEBIMENTO')
        self.text(x=55, y=lin +10.5, 
            txt='IDENTIFICAÇÃO E ASSINATURA DO RECEBEDOR')
        self.text(x=178, y=lin +2, txt='NF-e')
        
        self.set_font('Times', 'B', 8)
        nf = '{0:011,}'.format(int(self.nr_nota)).replace( "," , "." )                     
        self.text(x=163, y=lin +8, txt='Nº %s' % nf) 
        self.text(x=163, y=lin +13, txt='SÉRIE %s' % self.serie_nf)
        
    def emit_p(self):
        
        self.rect(x=10, y=self.lin_emit, w=190, h=45, style='')
        self.line(95, self.lin_emit, 95, self.lin_emit +31)
        self.line(123, self.lin_emit, 123, self.lin_emit +38)
        self.line(10, self.lin_emit +31, 200, self.lin_emit +31)
        self.line(10, self.lin_emit +38, 200, self.lin_emit +38)
        
        self.line(70, self.lin_emit +38, 70, self.lin_emit +45)
        self.line(110, self.lin_emit +38, 110, self.lin_emit +45)
        
        if self.logo_image:
            self.image(self.logo_image, 11, self.lin_emit +1, 12, type='jpg')

        self.set_font('Times', 'B', 10)        
        self.set_xy(x=26, y=self.lin_emit +2)
        text = get_tag_text(node=self.emit, url=url, tag='xNome')
        self.multi_cell(w=70, h=5, txt=text, border=0, 
                        align='C', fill=False)                  
        
        self.set_font('Times', 'B', 7)
        self.set_xy(x=11, y=self.lin_emit +19)
        end = "%s, %s - %s - %s - %s - CEP: %s Fone: %s" % (                        
                        get_tag_text(node=self.emit, url=url, tag='xLgr'),
                        get_tag_text(node=self.emit, url=url, tag='nro'),
                        get_tag_text(node=self.emit, url=url, tag='xBairro'),
                        get_tag_text(node=self.emit, url=url, tag='xMun'),
                        get_tag_text(node=self.emit, url=url, tag='UF'),
                        get_tag_text(node=self.emit, url=url, tag='CEP'),
                        get_tag_text(node=self.emit, url=url, tag='fone')
                                            )
        
        self.multi_cell(w=83, h=4, txt=end, border=0, align='C', fill=False)                  
        
        self.set_font('Times', 'B', 12)
        self.text(x=102, y=self.lin_emit +5, txt='DANFE')
        
        self.set_font('Times', '', 7)
        self.text(x=96, y=self.lin_emit +9, txt='Documento Auxiliar da')
        self.text(x=96, y=self.lin_emit +12, txt='Nota Fiscal Eletrônica')        
        self.text(x=96, y=self.lin_emit +16, txt='0 - Entrada')
        self.text(x=96, y=self.lin_emit +19, txt='1 - Saída')
        self.rect(x=10, y=self.lin_emit, w=190, h=45, style='')
        
        self.rect(x=114, y=self.lin_emit +14, w=8, h=6, style='')
                
        self.set_font('Times', 'B', 10)
        self.text(x=117, y=self.lin_emit +18, txt=self.tp_nf)
                                    
        self.set_font('Times', 'B', 8)
        nf = '{0:011,}'.format(int(self.nr_nota)).replace( "," , "." )                     
        self.text(x=96, y=self.lin_emit +24, txt='Nº %s' % nf) 
        self.text(x=96, y=self.lin_emit +27, txt='SÉRIE %s' % self.serie_nf)
        self.text(x=100, y=self.lin_emit +30, txt='Página %s de %s' % (
            self.current_page, self.nr_pages))

        self.set_font('Times', '', 5)        
        self.text(x=124, y=self.lin_emit +2.5, txt='CONTROLE DO FISCO')
                
        self.code128(self.key_nfe, 125, self.lin_emit +4, height=9, 
            thickness=0.265, quiet_zone=True)
        
        self.rect(x=124, y=self.lin_emit +15, w=75, h=6, style='')
        self.text(x=125, y=self.lin_emit +17, txt='CHAVE DE ACESSO')
        self.set_font('Times', 'B', 7)
        self.text(x=131, y=self.lin_emit +20, 
            txt=' '.join(chunks(self.key_nfe, 4)))
        
        self.set_font('Times', '', 8)
        self.set_xy(x=124, y=self.lin_emit +23)
        text = ("Consulta de autenticidade no portal nacional da NF-e "
                "www.nfe.fazenda.gov.br/portal ou no site da "
                "Sefaz autorizadora")
        self.multi_cell(w=75, h=3, txt=text, border=0, align='L', fill=False)                  
                
        self.set_font('Times', '', 5)        
        self.text(x=11, y=self.lin_emit +33.1, txt='NATUREZA DA OPERAÇÃO')
        self.text(x=11, y=self.lin_emit +40, txt='INSCRIÇÃO ESTADUAL')
        self.text(x=71, y=self.lin_emit +40, 
            txt='INSCRIÇÃO ESTADUAL DO SUBST. TRIB')
        self.text(x=111, y=self.lin_emit +40, txt='CNPJ')

        self.text(x=124, y=self.lin_emit +33.1, 
            txt='PROTOCOLO DE AUTORIZAÇÃO DE USO')
                
        self.set_font('Times', '', 8)
        text = get_tag_text(node=self.ide, url=url, tag='natOp')                                                
        self.text(x=11, y=self.lin_emit +37, 
            txt=self.long_field(text=text, limit=112))
                       
        self.text(x=11, y=self.lin_emit +44, 
            txt=get_tag_text(node=self.emit, url=url, tag='IE'))
        
        text = get_tag_text(node=self.emit, url=url, tag='CNPJ')
        self.text(x=111, y=self.lin_emit +44, txt=format_cpf_cnpj(text))

        self.set_font('Times', 'B', 7)
        self.set_xy(x=123, y=self.lin_emit +34)
        self.cell(77, 5, self.prot_uso, 0, 0, 'C') 
                
        # Homologação
        if get_tag_text(node=self.ide, url=url, tag='tpAmb') == '2':
            
            self.set_text_color(r=145, g=145, b=145)
            self.rotate(90, x=197, y=70)
            self.set_font('Times', 'B', 40)        
            self.set_xy(x=33, y=10)
            self.text(x=34, y=20.5, txt='SEM VALOR FISCAL')            
            self.rotate(0, x=197, y=70) 
            self.set_text_color(r=0, g=0, b=0)           

    def dest_p(self):
        lin = self.lin_emit + 49
        self.set_font('Times', 'B', 7)        
        self.text(x=11, y=lin -1, txt='DESTINATÁRIO/REMETENTE')
        self.rect(x=10, y=lin, w=190, h=20, style='')
        
        self.line(10, lin +6.66, 200, lin +6.66)
        self.line(10, lin +13.32, 200, lin +13.32)
        self.line(123, lin, 123, lin +6.66)
        self.line(169, lin, 169, lin +20)
        self.line(97, lin +6.66, 97, lin +20) 
        self.line(142, lin +6.66, 142, lin +13.32)
        self.line(60, lin +13.32, 60, lin +20)
        self.line(107, lin +13.32, 107, lin +20)
        
        self.set_font('Times', '', 5)        
        self.text(x=11, y=lin +2, txt='NOME/RAZÃO SOCIAL')
        self.text(x=124, y=lin +2, txt='CNPJ/CPF')
        self.text(x=170, y=lin +2, txt='DATA DA EMISSÃO')
        
        self.text(x=11, y=lin +8.66, txt='ENDEREÇO')
        self.text(x=98, y=lin +8.66, txt='BAIRRO/DISTRITO')
        self.text(x=143, y=lin +8.66, txt='CEP')
        self.text(x=170, y=lin +8.66, txt='DATA DA ENTRADA/SAÍDA')
        
        self.text(x=11, y=lin +15.32, txt='MUNICÍPIO')
        self.text(x=61, y=lin +15.32, txt='FONE/FAX')
        self.text(x=98, y=lin +15.32, txt='UF')
        self.text(x=108, y=lin +15.32, txt='INSCRIÇÃO ESTADUAL')
        self.text(x=170, y=lin +15.32, txt='HORA DE ENTRADA/SAÍDA')

        self.set_font('Times', '', 8)
        
        # Homologação
        if get_tag_text(node=self.ide, url=url, tag='tpAmb') == '1':
            txt = get_tag_text(node=self.dest, url=url, tag='xNome')
        else:
            txt = "NF-E EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL"
                
        self.text(x=11, y=lin +5.7, txt=self.long_field(text=txt, limit=110))
        
        txt = get_tag_text(node=self.dest, url=url, tag='CNPJ')
        if not txt:
            txt = get_tag_text(node=self.dest, url=url, tag='CPF')            
        self.text(x=124, y=lin +5.7, txt=format_cpf_cnpj(txt))
        
        dt, h = getdateUTC(get_tag_text(node=self.ide, url=url, tag='dhEmi'))
        self.text(x=170, y=lin +5.7, txt=dt)
        
        end = '%s, %s' % (get_tag_text(node=self.dest, url=url, tag='xLgr'),
                          get_tag_text(node=self.dest, url=url, tag='nro'))         
        self.text(x=11, y=lin +12.4, txt=self.long_field(text=end, limit=86))
        
        txt = get_tag_text(node=self.dest, url=url, tag='xBairro')
        self.text(x=98, y=lin +12.4, txt=self.long_field(text=txt, limit=44))

        self.text(x=143, y=lin +12.4, 
            txt=get_tag_text(node=self.dest, url=url, tag='CEP'))
        
        dt, h = getdateUTC(get_tag_text(node=self.ide, url=url, tag='dhSaiEnt'))
        self.text(x=170, y=lin +12.4, txt=dt)
        
        txt = get_tag_text(node=self.dest, url=url, tag='xMun')
        self.text(x=11, y=lin +19.1, txt=self.long_field(text=txt, limit=50))

        self.text(x=61, y=lin +19.1, 
            txt=get_tag_text(node=self.dest, url=url, tag='fone'))
                                         
        self.text(x=98, y=lin +19.1, 
            txt=get_tag_text(node=self.dest, url=url, tag='UF'))
        
        self.text(x=108, y=lin +19.1, 
            txt=get_tag_text(node=self.dest, url=url, tag='IE'))
        
    def fat_p(self):    
                
        lin = self.lin_emit +73
        self.set_font('Times', 'B', 7)
        self.text(x=11, y=lin -1, txt='FATURA')
        self.rect(x=10, y=lin, w=190, h=13, style='')
        self.line(57.5, lin, 57.5, lin +13)
        self.line(105, lin, 105, lin +13)
        self.line(152.5, lin, 152.5, lin +13)
        self.line(152.5, lin +6.5, 200, lin +6.5)
                                
        if self.inf_adic is not None:
            self.set_font('Times', '', 8)
            codvend = self.inf_adic.find(".//{http://www.portalfiscal.inf.br/"
                "nfe}obsCont[@xCampo='CodVendedor']")      
            
            self.text(x=153.5, y=lin +5.7, 
                txt=get_tag_text(node=codvend, url=url, tag='xTexto'))
                  
            vend = self.inf_adic.find(".//{http://www.portalfiscal.inf.br/nfe}"
                "obsCont[@xCampo='NomeVendedor']")

            txt = get_tag_text(node=vend, url=url, tag='xTexto')
            self.text(x=153.5, y=lin +12.24, 
                txt=self.long_field(text=txt, limit=47))
                                               
        self.set_font('Times', '', 5)
        self.text(x=153.5, y=lin +2, txt='CÓDIGO VENDEDOR')
        self.text(x=153.5, y=lin +8.5, txt='NOME VENDEDOR')

        self.set_xy(x=10, y=lin +0.5)        
        self.cell(14.5, 2.5, 'FATURA', 0, 0, 'L')
        self.cell(15, 2.5, 'VENCIMENTO', 0, 0, 'C')
        self.cell(18, 2.5, 'VALOR', 0, 0, 'R')
        self.cell(14.5, 2.5, 'FATURA', 0, 0, 'L')
        self.cell(15, 2.5, 'VENCIMENTO', 0, 0, 'C')
        self.cell(18, 2.5, 'VALOR', 0, 0, 'R')
        self.cell(14.5, 2.5, 'FATURA', 0, 0, 'L')
        self.cell(15, 2.5, 'VENCIMENTO', 0, 0, 'C')
        self.cell(18, 2.5, 'VALOR', 0, 0, 'R')
        
        # Salta elemt 1 (tag fat) e considera os próximos 9 (tags dup)    
        self.set_font('Times', '', 7)
        cobr_iter = iter(self.cobr[1:10]) if self.cobr is not None else [] 
        n_dup_ = 1
        col_ = 10            
        self.set_xy(x=col_ , y=lin +3)
        for i, dup in enumerate(cobr_iter):
         
            dt, hr = getdateUTC(
                get_tag_text(node=dup, url=url, tag='dVenc'))
            n_dup = get_tag_text(node=dup, url=url, tag='nDup')
            vlr = format_number(
                    get_tag_text(node=dup, url=url, tag='vDup'), precision=2)
                
            self.cell(14.5, 4, n_dup, 0, 0, 'L')
            self.cell(15, 4, dt, 0, 0, 'C')
            self.cell(18, 4, vlr, 0, 0, 'R')                                
                                                   
            if n_dup_ == 3:
                col_ += 47.5
                self.set_y(y=lin +3)
                n_dup_ = 1
            else:                
                n_dup_ += 1                    
                self.ln(3)
                
            self.set_x(x=col_)
                                                
    def impostos_p(self):    
        lin = self.lin_emit +90
        self.set_font('Times', 'B', 7)
        self.text(x=11, y=lin -1, txt='CÁLCULO DO IMPOSTO')
        self.rect(x=10, y=lin, w=190, h=13, style='')
        self.line(10, lin +6.5, 200, lin +6.5)
        self.line(48, lin, 48, lin +6.5)
        self.line(86, lin, 86, lin +6.5)
        self.line(124, lin, 124, lin +6.5)
        self.line(162, lin, 162, lin +13)
        
        self.line(32, lin +6.5, 32, lin +13)
        self.line(54, lin +6.5, 54, lin +13)
        self.line(76, lin +6.5, 76, lin +13)
        self.line(103, lin +6.5, 103, lin +13)
        self.line(130, lin +6.5, 130, lin +13)
        
        self.set_font('Times', '', 5)        
        self.text(x=11, y=lin +2, txt='BASE DE CÁLCULO DO ICMS')
        self.text(x=49, y=lin +2, txt='VALOR DO ICMS')
        self.text(x=87, y=lin +2, txt='BASE DE CÁLCULO DO ICMS ST')
        self.text(x=125, y=lin +2, txt='VALOR DO ICMS ST')
        self.text(x=163, y=lin +2, txt='VALOR TOTAL DOS PRODUTOS')
        
        self.text(x=11, y=lin +8.5, txt='VALOR DO FRETE')
        self.text(x=33, y=lin +8.5, txt='VALOR DO SEGURO')
        self.text(x=55, y=lin +8.5, txt='DESCONTO')
        self.text(x=77, y=lin +8.5, txt='OUTRAS DESP. ACESSÓRIAS')
        self.text(x=104, y=lin +8.5, txt='VALOR DO IPI')
        self.text(x=131, y=lin +8.5, txt='VALOR APROX. TRIBUTOS')
        self.text(x=163, y=lin +8.5, txt='VALOR TOTAL DA NOTA')
        
        self.set_font('Times', '', 8)
        self.set_xy(x=11, y=lin +2.7)        
        self.cell(37, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vBC'), precision=2), 0, 0, 'R')
        self.cell(38, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vICMS'), precision=2), 0, 0, 'R')
        self.cell(38, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vBCST'), precision=2), 0, 0, 'R')
        self.cell(38, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vST'), precision=2), 0, 0, 'R')
        self.cell(38, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vProd'), precision=2), 0, 0, 'R')
        
        self.set_xy(x=11, y=lin +9.2)        
        self.cell(21, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vFrete'), precision=2), 0, 0, 'R')
        self.cell(22, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vSeg'), precision=2), 0, 0, 'R')
        self.cell(22, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vDesc'), precision=2), 0, 0, 'R')
        self.cell(27, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vOutro'), precision=2), 0, 0, 'R')
        self.cell(27, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vIPI'), precision=2), 0, 0, 'R')
        self.cell(32, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vTotTrib'), precision=2), 0, 0, 'R')
        self.cell(38, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vNF'), precision=2), 0, 0, 'R')
    
    def transp_p(self):
        lin = self.lin_emit +107
        self.set_font('Times', 'B', 7)
        self.text(x=11, y=lin -1, txt='TRANSPORTADOR/VOLUMES TRANSPORTADOS')
        self.rect(x=10, y=lin, w=190, h=19, style='')
        self.line(10, lin +6.33, 200, lin +6.33)
        self.line(10, lin +12.66, 200, lin +12.66)
        
        self.line(80, lin, 80, lin +6.33)
        self.line(105, lin, 105, lin +6.33)
        self.line(125, lin, 125, lin +6.33)
        self.line(147, lin, 147, lin +19)
        self.line(156, lin, 156, lin +12.66)
        self.line(97, lin +6.33, 97, lin +12.66)
        self.line(36, lin +12.66, 36, lin +19)
        self.line(73, lin +12.66, 73, lin +19)
        self.line(111, lin +12.66, 111, lin +19)
        self.line(173, lin +12.66, 173, lin +19)

        self.set_font('Times', '', 5)        
        self.text(x=11, y=lin +2, txt='RAZÃO SOCIAL')
        self.text(x=81, y=lin +2, txt='FRETE POR CONTA')
        self.text(x=106, y=lin +2, txt='CÓDIGO ANTT')
        self.text(x=126, y=lin +2, txt='PLACA DO VEÍCULO')
        self.text(x=148, y=lin +2, txt='UF')
        self.text(x=157, y=lin +2, txt='CNPJ/CPF')
        self.text(x=11, y=lin +8.33, txt='ENDEREÇO')
        self.text(x=98, y=lin +8.33, txt='MUNICÍPIO')
        self.text(x=148, y=lin +8.33, txt='UF')
        self.text(x=157, y=lin +8.33, txt='INSCRIÇÃO ESTADUAL')
        
        self.text(x=11, y=lin +14.66, txt='QUANTIDADE')
        self.text(x=37, y=lin +14.66, txt='ESPÉCIE')
        self.text(x=74, y=lin +14.66, txt='MARCA')
        self.text(x=112, y=lin +14.66, txt='NUMERAÇÃO')
        self.text(x=148, y=lin +14.66, txt='PESO BRUTO')
        self.text(x=174, y=lin +14.66, txt='PESO LÍQUIDO')
        
        self.set_font('Times', '', 8)
        text = get_tag_text(node=self.transp, url=url, tag='xNome')                                                
        self.text(x=11, y=lin +5.7, 
            txt=self.long_field(text=text, limit=69))
        
        self.text(x=81, y=lin +5.7, txt=tp_frete[get_tag_text(
            node=self.transp, url=url, tag='modFrete')])

        text = get_tag_text(node=self.transp, url=url, tag='CNPJ')
        self.text(x=158, y=lin +5.7, txt=format_cpf_cnpj(text))

        text = get_tag_text(node=self.transp, url=url, tag='xEnder')                                                
        self.text(x=11, y=lin +12.03, 
            txt=self.long_field(text=text, limit=86))

        text = get_tag_text(node=self.transp, url=url, tag='xMun')                                                
        self.text(x=98, y=lin +12.03, 
            txt=self.long_field(text=text, limit=51))

        self.text(x=148, y=lin +12.03, 
            txt=get_tag_text(node=self.transp, url=url, tag='UF'))

        self.text(x=157, y=lin +12.03, 
            txt=get_tag_text(node=self.transp, url=url, tag='IE'))

        self.text(x=11, y=lin +18.36, 
            txt=get_tag_text(node=self.transp, url=url, tag='qVol'))

        self.text(x=37, y=lin +18.36, 
            txt=get_tag_text(node=self.transp, url=url, tag='esp'))

        self.text(x=74, y=lin +18.36, 
            txt=get_tag_text(node=self.transp, url=url, tag='marca'))

        self.text(x=112, y=lin +18.36, 
            txt=get_tag_text(node=self.transp, url=url, tag='nVol'))
        
        self.set_xy(x=147, y=lin +16)
        self.cell(26, 3, format_number(get_tag_text(
            node=self.transp, url=url, tag='pesoB'), precision=3), 0, 0, 'R')

        self.cell(27, 3, format_number(get_tag_text(
            node=self.transp, url=url, tag='pesoL'), precision=3), 0, 0, 'R')
            
    
    def produtos_p(self, paginator=None, list_desc=None):
        h_produtos = (paginator[2] * 3) +6.5
        self.set_font('Times', 'B', 7)
        self.text(x=11, y=self.lin_prod -1, txt='DADOS DO PRODUTO/SERVIÇO')
        self.rect(x=10, y=self.lin_prod, w=190, h=h_produtos, style='')
                                                 
        cols = self.cols_produtos[0]
        captions = self.cols_produtos[1]
        cells = self.cols_produtos[2]
        
        # Colunas            
        self.set_font('Times', 'B', 5)        
        self.line(10, self.lin_prod +6, 200, self.lin_prod +6)
        col_ = 10 # 10 mm margem
        self.set_xy(x=10, y=self.lin_prod +1)
        for id, col in enumerate(cols):
            col_ += col            
            self.line(col_, self.lin_prod, col_, self.lin_prod + h_produtos)
            
            lbl = captions[id].split('\n')                              
            if len(lbl) == 1:
                self.cell(col, 4, captions[id], 0, 0, 'C')
            else:
                current_col = self.get_x()               
                current_lin = self.get_y()
                             
                self.multi_cell(w=col, h=2, txt=captions[id], 
                    border=0, align='C', fill=False)
                
                self.set_xy(current_col + col, current_lin)                   
        
        # Dados dos produtos        
        self.set_font('Times', '', 6)        
        self.set_xy(x=10, y=self.lin_prod + 6.5)        
        #self.set_fill_color(235, 235, 235)
                
        for id in range(paginator[0], paginator[1]):
            
            item = self.det[id] 
            el_prod = item.find(".//{http://www.portalfiscal.inf.br/"
                "nfe}prod")
            el_imp  = item.find(".//{http://www.portalfiscal.inf.br/nfe}"
                "imposto")
         
            el_imp_ICMS = el_imp.find(".//{http://www.portalfiscal.inf.br/"
                "nfe}ICMS")

            el_imp_IPI  = el_imp.find(".//{http://www.portalfiscal.inf.br/"
                "nfe}IPI")
                            
            for id_col, col in enumerate(cols):
                cells[id_col](report=self,
                              node_item=el_prod, 
                              node_icms=el_imp_ICMS, 
                              node_ipi=el_imp_IPI,                               
                              width=col,                              
                              desc_item=list_desc[id])
                                        
            self.ln(3 * len(list_desc[id]))            
            
            if self.get_y() < (self.lin_prod + h_produtos): # id % 2:                                
                self.set_line_width(width=0.1)
                self.set_draw_color(r=177, g=177, b=177)                       
                y = self.get_y() -0.1 
                self.dashed_line(10, y, 200, y, dash_length=0.5, 
                    space_length=0.5)
                self.set_line_width(width=0.2)
                #self.set_draw_color(r=0, g=0, b=0)       
                                        
    def desc_item(self, list_desc=None, width=None):

        col = self.get_x()               
        lin = self.get_y()

        self.cell(width, 3, list_desc[0], 0, 0, 'L')
        self.ln(3)
                                
        for desc in list_desc[1:]:
            self.set_x(x=col)
            self.cell(width, 3, desc, 0, 0, 'L')            
            self.ln(3)
                        
        self.set_xy(col +width, lin) 
        
    def adic_p(self):
        lin = self.lin_adic
        self.set_font('Times', 'B', 7)
        self.text(x=11, y=lin -1, txt='DADOS ADICIONAIS')
        self.set_font('Times', '', 5)
        self.text(x=11, y=lin +2.5, txt='INFORMAÇÕES COMPLEMENTARES')
        self.text(x=106, y=lin +2.5, txt='RESERVADO AO FISCO')
        self.rect(x=10, y=lin, w=190, h=self.height_adic, style='')
        self.line(105, lin, 105, lin +29)

        fisco = get_tag_text(node=self.inf_adic, url=url, tag='infAdFisco')    
        obs = get_tag_text(node=self.inf_adic, url=url, tag='infCpl') 
        if fisco:
            obs = "%s %s" %(fisco, obs)
                        
        if obs:
            txt_width = 700                                  
            self.set_xy(x=11, y=lin +3.5) 
            self.set_font('Times', '', 6)
            self.multi_cell(w=93, h=3, txt=self.long_field(text=obs, 
                limit=txt_width), border=0, align='L', fill=False)                  

    
    # Layout paisagem
    def recibo_l(self):
        
        self.rect(x=16, y=10, w=17, h=190, style='')
        self.line(24.5, 10, 24.5, 160)
        self.line(16, 160, 33, 160)
        self.line(16, 54, 24.5, 54)
        self.dashed_line(34.5, 10, 34.5, 200, dash_length=0.5, space_length=1)
         
        self.rotate(-90, x=33, y=10)
        
        self.set_font('Times', 'B', 5)        
        self.set_xy(x=33, y=10)
        
        self.multi_cell(w=150, h=3, txt=self.recibo_txt, border=0, 
                       align='L', fill=False)                  
        self.text(x=34, y=20.5, txt='DATA DE RECEBIMENTO')
        self.text(x=79, y=20.5, txt='IDENTIFICAÇÃO E ASSINATURA DO RECEBEDOR')
        self.text(x=201, y=12, txt='NF-e')
        self.set_font('Times', 'B', 8)
        
        nf = '{0:011,}'.format(int(self.nr_nota)).replace( "," , "." )                     
        self.text(x=186, y=18, txt='Nº %s' % nf) 
        self.text(x=186, y=23, txt='SÉRIE %s' % self.serie_nf)
        
        self.rotate(0, x=33, y=10) 
    
    def emit_l(self):
        
        self.rect(x=36, y=self.lin_emit, w=248, h=38, style='')                        
        self.line(146, self.lin_emit, 146, self.lin_emit +38)        
        self.line(184, self.lin_emit, 184, self.lin_emit +38)        
        self.line(36, self.lin_emit +24, 146, self.lin_emit +24)
        self.line(36, self.lin_emit +31, 284, self.lin_emit +31)
        self.line(86, self.lin_emit +31, 86, self.lin_emit +38)
        
        if self.logo_image:
            self.image(self.logo_image, 37, self.lin_emit +2, 15, type='jpg')
                
        self.set_font('Times', 'B', 10)        
        self.set_xy(x=55, y=self.lin_emit +2)
        text = get_tag_text(node=self.emit, url=url, tag='xNome')
        self.multi_cell(w=90, h=5, txt=text, border=0, 
                        align='C', fill=False)                  
                
        self.set_font('Times', 'B', 7)
        self.set_xy(x=55, y=self.lin_emit +15)
        end = "%s, %s - %s - %s - %s - CEP: %s Fone: %s" % (                        
                        get_tag_text(node=self.emit, url=url, tag='xLgr'),
                        get_tag_text(node=self.emit, url=url, tag='nro'),
                        get_tag_text(node=self.emit, url=url, tag='xBairro'),
                        get_tag_text(node=self.emit, url=url, tag='xMun'),
                        get_tag_text(node=self.emit, url=url, tag='UF'),
                        get_tag_text(node=self.emit, url=url, tag='CEP'),
                        get_tag_text(node=self.emit, url=url, tag='fone')
                                            )
        
        self.multi_cell(w=90, h=4, txt=end, border=0, align='C', fill=False)                  
               
        self.set_font('Times', 'B', 12)
        self.text(x=158, y=self.lin_emit +5, txt='DANFE')
        
        self.set_font('Times', '', 7)
        self.text(x=152, y=self.lin_emit +9, txt='Documento Auxiliar da')
        self.text(x=152, y=self.lin_emit +12, txt='Nota Fiscal Eletrônica')        
        self.text(x=152, y=self.lin_emit +16, txt='0 - Entrada')
        self.text(x=152, y=self.lin_emit +19, txt='1 - Saída')        
        self.rect(x=170, y=self.lin_emit +14, w=8, h=6, style='')
                
        self.set_font('Times', 'B', 10)
        self.text(x=173, y=self.lin_emit +18, txt=self.tp_nf)
        
        self.set_font('Times', 'B', 8)        
        nf = '{0:011,}'.format(int(self.nr_nota)).replace( "," , "." )                     
        self.text(x=152, y=self.lin_emit +24, txt='Nº %s' % nf) 
        self.text(x=152, y=self.lin_emit +27, txt='SÉRIE %s' % self.serie_nf)
        self.text(x=156, y=self.lin_emit +30, txt='Página %s de %s' % (
            self.current_page, self.nr_pages))
        
        self.set_font('Times', '', 5)        
        self.text(x=185, y=self.lin_emit +2.5, txt='CONTROLE DO FISCO')
                
        self.code128(self.key_nfe, 197.1, self.lin_emit +4, height=9, 
            thickness=0.265, quiet_zone=True)
        
        self.rect(x=185, y=self.lin_emit +15, w=98, h=6, style='')
        self.text(x=186, y=self.lin_emit +17.2, txt='CHAVE DE ACESSO')
        self.set_font('Times', 'B', 7)
        self.text(x=205, y=self.lin_emit +20, 
            txt=' '.join(chunks(self.key_nfe, 4)))
        
        self.set_font('Times', '', 8)
        self.set_xy(x=185, y=self.lin_emit +23)
        text = ("Consulta de autenticidade no portal nacional da NF-e "
                "www.nfe.fazenda.gov.br/portal ou no site da "
                "Sefaz autorizadora")
        self.multi_cell(w=98, h=3, txt=text, border=0, align='L', fill=False)                  
                
        self.set_font('Times', '', 5)        
        self.text(x=37, y=self.lin_emit +26.1, txt='NATUREZA DA OPERAÇÃO')
        self.text(x=37, y=self.lin_emit +33.2, txt='INSCRIÇÃO ESTADUAL')
        self.text(x=87, y=self.lin_emit +33.2, 
            txt='INSCRIÇÃO ESTADUAL DO SUBST. TRIB')
        self.text(x=147, y=self.lin_emit +33.2, txt='CNPJ')

        self.text(x=185, y=self.lin_emit +33.1, 
            txt='PROTOCOLO DE AUTORIZAÇÃO DE USO')
                
        self.set_font('Times', '', 8)
        text = get_tag_text(node=self.ide, url=url, tag='natOp')                                                
        self.text(x=37, y=self.lin_emit +30, 
            txt=self.long_field(text=text, limit=112))
                       
        self.text(x=37, y=self.lin_emit +37.1, 
            txt=get_tag_text(node=self.emit, url=url, tag='IE'))
        
        text = get_tag_text(node=self.emit, url=url, tag='CNPJ')
        self.text(x=147, y=self.lin_emit +37.1, txt=format_cpf_cnpj(text))

        self.set_font('Times', 'B', 7)
        self.set_xy(x=184, y=self.lin_emit +34)
        self.cell(100, 5, self.prot_uso, 0, 0, 'C')        

        # Homologação
        if get_tag_text(node=self.ide, url=url, tag='tpAmb') == '2':
            
            self.set_text_color(r=145, g=145, b=145)
            self.rotate(90, x=204, y=14)
            self.set_font('Times', 'B', 40)        
            self.set_xy(x=33, y=10)
            self.text(x=34, y=20.5, txt='SEM VALOR FISCAL')            
            self.rotate(0, x=90, y=60) 
            self.set_text_color(r=0, g=0, b=0)           
            
    def dest_l(self):
        lin = self.lin_emit +42
        
        self.set_font('Times', 'B', 7)        
        self.text(x=37, y=lin -1, txt='DESTINATÁRIO/REMETENTE')
        self.rect(x=36, y=lin, w=248, h=20, style='')        
        self.line(36, self.lin_emit +48.66, 284, self.lin_emit +48.66)
        self.line(36, self.lin_emit +55.32, 284, self.lin_emit +55.32)
        self.line(184, self.lin_emit +42, 184, self.lin_emit +48.66)
        self.line(242, self.lin_emit +42, 242, self.lin_emit +62)
        self.line(151, self.lin_emit +48.66, 151, self.lin_emit +55.33)
        self.line(204, self.lin_emit +48.66, 204, self.lin_emit +55.33)
        
        self.line(96, self.lin_emit +55.33, 96, self.lin_emit +62)
        self.line(141, self.lin_emit +55.33, 141, self.lin_emit +62)
        self.line(158, self.lin_emit +55.33, 158, self.lin_emit +62)
                        
        self.set_font('Times', '', 5)        
        self.text(x=37, y=lin +2, txt='NOME/RAZÃO SOCIAL')
        self.text(x=185, y=lin +2, txt='CNPJ/CPF')
        self.text(x=243, y=lin +2, txt='DATA DE EMISSÃO')
        
        self.text(x=37, y=lin +8.66, txt='ENDEREÇO')
        self.text(x=152, y=lin +8.66, txt='BAIRRO/DISTRITO')
        self.text(x=205, y=lin +8.66, txt='CEP')
        self.text(x=243, y=lin +8.66, txt='DATA DE ENTRADA/SAÍDA')
        
        self.text(x=37, y=lin +15.32, txt='MUNICÍPIO')
        self.text(x=97, y=lin +15.32, txt='FONE/FAX')
        self.text(x=142, y=lin +15.32, txt='UF')
        self.text(x=159, y=lin +15.32, txt='INSCRIÇÃO ESTADUAL')
        self.text(x=243, y=lin +15.32, txt='HORA DE ENTRADA/SAÍDA')

        self.set_font('Times', '', 8)
        
        # Homologação
        if get_tag_text(node=self.ide, url=url, tag='tpAmb') == '1':
            txt = get_tag_text(node=self.dest, url=url, tag='xNome')
        else:
            txt = "NF-E EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL"
                
        self.text(x=37, y=lin +5.7, txt=self.long_field(text=txt, limit=145))
        
        txt = get_tag_text(node=self.dest, url=url, tag='CNPJ')
        if not txt:
            txt = get_tag_text(node=self.dest, url=url, tag='CPF')            
        self.text(x=185, y=lin +5.7, txt=format_cpf_cnpj(txt))
        
        dt, h = getdateUTC(get_tag_text(node=self.ide, url=url, tag='dhEmi'))
        self.text(x=243, y=lin +5.7, txt=dt)
        
        end = '%s, %s' % (get_tag_text(node=self.dest, url=url, tag='xLgr'),
                          get_tag_text(node=self.dest, url=url, tag='nro'))         
        self.text(x=37, y=lin +12.4, txt=self.long_field(text=end, limit=86))
        
        txt = get_tag_text(node=self.dest, url=url, tag='xBairro')
        self.text(x=152, y=lin +12.4, txt=self.long_field(text=txt, limit=50))

        self.text(x=205, y=lin +12.4, 
            txt=get_tag_text(node=self.dest, url=url, tag='CEP'))
        
        dt, h = getdateUTC(get_tag_text(node=self.ide, url=url, tag='dhSaiEnt'))
        self.text(x=243, y=lin +12.4, txt=dt)
        
        txt = get_tag_text(node=self.dest, url=url, tag='xMun')
        self.text(x=37, y=lin +19.1, txt=self.long_field(text=txt, limit=50))

        self.text(x=97, y=lin +19.1, 
            txt=get_tag_text(node=self.dest, url=url, tag='fone'))
                                         
        self.text(x=142, y=lin +19.1, 
            txt=get_tag_text(node=self.dest, url=url, tag='UF'))
        
        self.text(x=159, y=lin +19.1, 
            txt=get_tag_text(node=self.dest, url=url, tag='IE'))
                
    def fat_l(self):    
        lin = self.lin_emit +66 
        self.set_font('Times', 'B', 7)
        self.text(x=37, y=lin -1, txt='FATURA')
        self.rect(x=36, y=lin, w=248, h=13, style='')
        self.line(98, self.lin_emit +66, 98, self.lin_emit +79)
        self.line(160, self.lin_emit +66, 160, self.lin_emit +79)
        self.line(222, self.lin_emit +66, 222, self.lin_emit +79)
        self.line(222, self.lin_emit +72.5, 284, self.lin_emit +72.5)

        if self.inf_adic is not None:
            self.set_font('Times', '', 8)
            codvend = self.inf_adic.find(".//{http://www.portalfiscal.inf.br/"
                "nfe}obsCont[@xCampo='CodVendedor']")      
            
            self.text(x=223, y=lin +5.7, 
                txt=get_tag_text(node=codvend, url=url, tag='xTexto'))
                  
            vend = self.inf_adic.find(".//{http://www.portalfiscal.inf.br/nfe}"
                "obsCont[@xCampo='NomeVendedor']")

            txt = get_tag_text(node=vend, url=url, tag='xTexto')
            self.text(x=223, y=lin +12.24, 
                txt=self.long_field(text=txt, limit=60))
                                               
        self.set_font('Times', '', 5)
        self.text(x=223, y=lin +2.3, txt='CÓDIGO VENDEDOR')
        self.text(x=223, y=lin +8.6, txt='NOME VENDEDOR')

        self.set_xy(x=36, y=lin +0.5)        
        self.cell(19, 2.5, 'FATURA', 0, 0, 'L')
        self.cell(22, 2.5, 'VENCIMENTO', 0, 0, 'C')
        self.cell(21, 2.5, 'VALOR', 0, 0, 'R')
        self.cell(19, 2.5, 'FATURA', 0, 0, 'L')
        self.cell(22, 2.5, 'VENCIMENTO', 0, 0, 'C')
        self.cell(21, 2.5, 'VALOR', 0, 0, 'R')
        self.cell(19, 2.5, 'FATURA', 0, 0, 'L')
        self.cell(22, 2.5, 'VENCIMENTO', 0, 0, 'C')
        self.cell(21, 2.5, 'VALOR', 0, 0, 'R')
        
        # Salta elemt 1 (tag fat) e considera os próximos 9 (tags dup)    
        self.set_font('Times', '', 7)
        cobr_iter = iter(self.cobr[1:10]) if self.cobr is not None else [] 
        n_dup_ = 1
        col_ = 36            
        self.set_xy(x=col_ , y=lin +3)
        for i, dup in enumerate(cobr_iter):
         
            dt, hr = getdateUTC(
                get_tag_text(node=dup, url=url, tag='dVenc'))
            n_dup = get_tag_text(node=dup, url=url, tag='nDup')
            vlr = format_number(
                    get_tag_text(node=dup, url=url, tag='vDup'), precision=2)
                
            self.cell(19, 4, n_dup, 0, 0, 'L')
            self.cell(22, 4, dt, 0, 0, 'C')
            self.cell(21, 4, vlr, 0, 0, 'R')                                
                                                   
            if n_dup_ == 3:
                col_ += 62
                self.set_y(y=lin +3)
                n_dup_ = 1
            else:                
                n_dup_ += 1                    
                self.ln(3)
                
            self.set_x(x=col_)
        
    
    def impostos_l(self):    
        lin = self.lin_emit +83
        self.set_font('Times', 'B', 7)
        self.text(x=37, y=92, txt='CÁLCULO DO IMPOSTO')
        self.rect(x=36, y=lin, w=248, h=13, style='')
        self.line(36, self.lin_emit +89.5, 284, self.lin_emit +89.5)
        
        self.line(86, lin, 86, self.lin_emit +89.5)
        self.line(137, lin, 137, self.lin_emit +89.5)
        self.line(187, lin, 187, self.lin_emit +89.5)
        self.line(237, lin, 237, self.lin_emit +96)
        
        self.line(66, self.lin_emit +89.5, 66, self.lin_emit +96)
        self.line(95, self.lin_emit +89.5, 95, self.lin_emit +96)
        self.line(125, self.lin_emit +89.5, 125, self.lin_emit +96)
        self.line(165, self.lin_emit +89.5, 165, self.lin_emit +96)
        self.line(195, self.lin_emit +89.5, 195, self.lin_emit +96)
        
        self.set_font('Times', '', 5)        
        self.text(x=37, y=lin +2, txt='BASE DE CÁLCULO DO ICMS')
        self.text(x=87, y=lin +2, txt='VALOR DO ICMS')
        self.text(x=138, y=lin +2, txt='BASE DE CÁLCULO DO ICMS ST')
        self.text(x=188, y=lin +2, txt='VALOR DO ICMS ST')
        self.text(x=238, y=lin +2, txt='VALOR TOTAL DOS PRODUTOS')
        
        self.text(x=37, y=lin +8.5, txt='VALOR DO FRETE')
        self.text(x=67, y=lin +8.5, txt='VALOR DO SEGURO')
        self.text(x=96, y=lin +8.5, txt='DESCONTO')
        self.text(x=126, y=lin +8.5, txt='OUTRAS DESP. ACESSÓRIAS')
        self.text(x=166, y=lin +8.5, txt='VALOR DO IPI')
        self.text(x=196, y=lin +8.5, txt='VALOR APROX. TRIBUTOS')
        self.text(x=238, y=lin +8.5, txt='VALOR TOTAL DA NOTA')
        
        self.set_font('Times', '', 8)
        self.set_xy(x=36, y=lin +2.7)        
        self.cell(50, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vBC'), precision=2), 0, 0, 'R')
        self.cell(51, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vICMS'), precision=2), 0, 0, 'R')
        self.cell(50, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vBCST'), precision=2), 0, 0, 'R')
        self.cell(50, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vST'), precision=2), 0, 0, 'R')
        self.cell(47, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vProd'), precision=2), 0, 0, 'R')
        
        self.set_xy(x=36, y=lin +9.2)        
        self.cell(30, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vFrete'), precision=2), 0, 0, 'R')
        self.cell(29, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vSeg'), precision=2), 0, 0, 'R')
        self.cell(30, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vDesc'), precision=2), 0, 0, 'R')
        self.cell(40, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vOutro'), precision=2), 0, 0, 'R')
        self.cell(30, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vIPI'), precision=2), 0, 0, 'R')
        self.cell(42, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vTotTrib'), precision=2), 0, 0, 'R')
        self.cell(47, 4, format_number(get_tag_text(
            node=self.totais, url=url, tag='vNF'), precision=2), 0, 0, 'R')

    def transp_l(self):
        lin = self.lin_emit +100
        self.set_font('Times', 'B', 7)
        self.text(x=37, y=lin -1, txt='TRANSPORTADOR/VOLUMES TRANSPORTADOS')
        self.rect(x=36, y=lin, w=248, h=20, style='')        
        self.line(36, self.lin_emit +106.66, 284, self.lin_emit +106.66)
        self.line(36, self.lin_emit +113.3, 284, self.lin_emit +113.3)
        
        self.line(121, self.lin_emit +100, 121, self.lin_emit +106.66)
        self.line(146, self.lin_emit +100, 146, self.lin_emit +113.3)
        self.line(183, self.lin_emit +100, 183, self.lin_emit +106.66)
        self.line(214, self.lin_emit +100, 214, self.lin_emit +120)
        self.line(226, self.lin_emit +100, 226, self.lin_emit +113.3)
        
        self.line(71, self.lin_emit +113.3, 71, self.lin_emit +120)
        self.line(121, self.lin_emit +113.3, 121, self.lin_emit +120)
        self.line(170, self.lin_emit +113.3, 170, self.lin_emit +120)
        self.line(248, self.lin_emit +113.3, 248, self.lin_emit +120)
        
    

        self.set_font('Times', '', 5)        
        self.text(x=37, y=lin +2, txt='RAZÃO SOCIAL')
        self.text(x=122, y=lin +2, txt='FRETE POR CONTA')
        self.text(x=147, y=lin +2, txt='CÓDIGO ANTT')
        self.text(x=184, y=lin +2, txt='PLACA DO VEÍCULO')
        self.text(x=215, y=lin +2, txt='UF')
        self.text(x=227, y=lin +2, txt='CNPJ/CPF')
        self.text(x=37, y=lin +8.7, txt='ENDEREÇO')
        self.text(x=147, y=lin +8.7, txt='MUNICÍPIO')
        self.text(x=215, y=lin +8.7, txt='UF')
        self.text(x=227, y=lin +8.7, txt='INSCRIÇÃO ESTADUAL')
        
        self.text(x=37, y=lin +15.4, txt='QUANTIDADE')
        self.text(x=72, y=lin +15.4, txt='ESPÉCIE')
        self.text(x=122, y=lin +15.4, txt='MARCA')
        self.text(x=171, y=lin +15.4, txt='NUMERAÇÃO')
        self.text(x=215, y=lin +15.4, txt='PESO BRUTO')
        self.text(x=249, y=lin +15.4, txt='PESO LÍQUIDO')
        
        self.set_font('Times', '', 8)
        text = get_tag_text(node=self.transp, url=url, tag='xNome')                                                
        self.text(x=37, y=lin +5.7, 
            txt=self.long_field(text=text, limit=85))
        
        self.text(x=122, y=lin +5.7, txt=tp_frete[get_tag_text(
            node=self.transp, url=url, tag='modFrete')])

        text = get_tag_text(node=self.transp, url=url, tag='CNPJ')
        self.text(x=227, y=lin +5.7, txt=format_cpf_cnpj(text))

        text = get_tag_text(node=self.transp, url=url, tag='xEnder')                                                
        self.text(x=37, y=lin +12.5, 
            txt=self.long_field(text=text, limit=110))

        text = get_tag_text(node=self.transp, url=url, tag='xMun')                                                
        self.text(x=147, y=lin +12.5, 
            txt=self.long_field(text=text, limit=51))

        self.text(x=215, y=lin +12.5, 
            txt=get_tag_text(node=self.transp, url=url, tag='UF'))

        self.text(x=227, y=lin +12.5, 
            txt=get_tag_text(node=self.transp, url=url, tag='IE'))

        self.text(x=37, y=lin +19.2, 
            txt=get_tag_text(node=self.transp, url=url, tag='qVol'))

        self.text(x=72, y=lin +19.2, 
            txt=get_tag_text(node=self.transp, url=url, tag='esp'))

        self.text(x=122, y=lin +19.2, 
            txt=get_tag_text(node=self.transp, url=url, tag='marca'))

        self.text(x=171, y=lin +19.2, 
            txt=get_tag_text(node=self.transp, url=url, tag='nVol'))
        
        self.set_xy(x=214, y=lin +16.7)
        self.cell(34, 3, format_number(get_tag_text(
            node=self.transp, url=url, tag='pesoB'), precision=3), 0, 0, 'R')

        self.cell(36, 3, format_number(get_tag_text(
            node=self.transp, url=url, tag='pesoL'), precision=3), 0, 0, 'R')

    def produtos_l(self, paginator=None, list_desc=None):
        
        h_produtos = (paginator[2] * 3) +6.5
        self.set_font('Times', 'B', 7)
        self.text(x=37, y=self.lin_prod -1, txt='DADOS DO PRODUTO/SERVIÇO')
        self.rect(x=36, y=self.lin_prod, w=248, h=h_produtos, style='')
                                                 
        cols = self.cols_produtos[0]
        captions = self.cols_produtos[1]
        cells = self.cols_produtos[2]
        
        # Colunas            
        self.set_font('Times', 'B', 5)        
        self.line(36, self.lin_prod +6, 284, self.lin_prod +6)
        col_ = 36 # 10 mm margem
        self.set_xy(x=36, y=self.lin_prod +1)
        for id, col in enumerate(cols):
            col_ += col            
            self.line(col_, self.lin_prod, col_, self.lin_prod + h_produtos)
            
            lbl = captions[id].split('\n')                              
            if len(lbl) == 1:
                self.cell(col, 4, captions[id], 0, 0, 'C')
            else:
                current_col = self.get_x()               
                current_lin = self.get_y()
                             
                self.multi_cell(w=col, h=2, txt=captions[id], 
                    border=0, align='C', fill=False)
                
                self.set_xy(current_col + col, current_lin)                   
        
        # Dados dos produtos        
        self.set_font('Times', '', 6)        
        self.set_xy(x=36, y=self.lin_prod + 6.5)        
        #self.set_fill_color(235, 235, 235)
                
        for id in range(paginator[0], paginator[1]):
            
            item = self.det[id] 
            el_prod = item.find(".//{http://www.portalfiscal.inf.br/"
                "nfe}prod")

            el_imp  = item.find(".//{http://www.portalfiscal.inf.br/nfe}"
                "imposto")
         
            el_imp_ICMS = el_imp.find(".//{http://www.portalfiscal.inf.br/"
                "nfe}ICMS")

            el_imp_IPI  = el_imp.find(".//{http://www.portalfiscal.inf.br/"
                "nfe}IPI")
                            
            for id_col, col in enumerate(cols):
                cells[id_col](report=self,
                              node_item=el_prod, 
                              node_icms=el_imp_ICMS, 
                              node_ipi=el_imp_IPI,                               
                              width=col,                              
                              desc_item=list_desc[id])
                                        
            self.ln(3 * len(list_desc[id]))
            self.set_x(x=36) 
            
            if self.get_y() < (self.lin_prod + h_produtos): # id % 2:                
                y = self.get_y() -0.1 
                self.dashed_line(36, y, 284, y, dash_length=1, space_length=1)       
        
    
    def adic_l(self):
        self.set_font('Times', 'B', 7)
        self.text(x=37, y=166, txt='DADOS ADICIONAIS')
        self.set_font('Times', '', 5)
        self.text(x=37, y=169.5, txt='INFORMAÇÕES COMPLEMENTARES')
        self.text(x=161, y=169.5, txt='RESERVADO AO FISCO')
        self.rect(x=36, y=167, w=248, h=29, style='')
        self.line(160, 167, 160, 196)

        fisco = get_tag_text(node=self.inf_adic, url=url, tag='infAdFisco')    
        obs = get_tag_text(node=self.inf_adic, url=url, tag='infCpl') 
        if fisco:
            obs = "%s %s" %(fisco, obs)
                        
        if obs:
            txt_width = 910                                  
            self.set_xy(x=36, y=171) 
            self.set_font('Times', '', 6)
            self.multi_cell(w=120, h=3, txt=self.long_field(text=obs, 
                                                            limit=txt_width), 
                            border=0, align='L', fill=False)                  

        
# Recebe list xmls em string e image base64 - Modo retrato
class DaCCe(xFPDF):
    def __init__(self, xmls=None, emitente=None, image=None):
         
        super(DaCCe, self).__init__('P', 'mm', 'A4')     
        
        self.set_auto_page_break(auto=False, margin=10.0)
        
        self.set_title('DACCe')
        #self.add_font('NimbusSanLBold', '', 'NimbusSanLBold.ttf', uni=True)
        #self.add_font('NimbusSanL', '', 'NimbusSanL.ttf', uni=True)
        #self.add_font('NimbusSanLItalic', '', 'NimbusSanLItalic.ttf', uni=True)
                
        if xmls is None:
            raise NameError('XML não informado!')
        
        if not isinstance(xmls, list):
            xmls = [xmls]

        for xml in xmls:
                        
            root = ET.fromstring(xml)
            det_event = root.find("%sdetEvento" % url)
            inf_event = root.find("%sinfEvento" % url)
            ret_Event = root.find("%sretEvento" % url)
            inf_ret_Event = ret_Event.find("%sinfEvento" % url)
                            
            self.add_page(orientation='P', format='A4')
            
            # Emitente
            self.rect(x=10, y=10, w=190, h=33, style='')
            self.line(90, 10, 90, 43)

            cc = ''
            txt = ''
            if emitente:
                emitente_nome = emitente['nome']
                txt = '%s\n%s\n%s - %s %s' % (emitente['end'],
                emitente['bairro'],
                emitente['cidade'],
                emitente['uf'],
                emitente['fone'])
            
            if image:
                col_ = 23
                col_end = 28
                w_ = 67 
                self.image(image, 12, 12, 12, type='jpg')
            else:
                col_ = 11
                col_end = 24
                w_ = 80
            
            self.set_xy(x=col_, y=16)
            self.set_font('Times', 'B', 10)
            self.multi_cell(w=w_, h=4, txt=emitente_nome, border=0, align='C', 
                fill=False)                  
            self.set_xy(x=11, y=col_end)
            self.set_font('Times', '', 8)
            self.multi_cell(w=80, h=4, txt=txt, border=0, align='C', 
                fill=False)                  

            self.set_font('Times', 'B', 10)
            self.text(x=118, y=16, txt='Representação Gráfica de CC-e')
            self.set_font('Times', 'I', 9)
            self.text(x=123, y=20, txt='(Carta de Correção Eletrônica)')
                                                
            self.set_font('Times', '', 8)
            self.text(x=92, y=30, 
                txt='ID do Evento: %s' % inf_event.attrib.get('Id')[2:])

            dt, hr = getdateUTC(
                get_tag_text(node=inf_event, url=url, tag='dhEvento'))
             
            self.text(x=92, y=35, txt='Criado em:  %s %s' % (dt, hr))

            dt, hr = getdateUTC(
                get_tag_text(node=inf_ret_Event, url=url, tag='dhRegEvento'))

            n_prot = get_tag_text(node=inf_ret_Event, url=url, tag='nProt')
             
            self.text(x=92, y=40, txt='Prococolo: %s - '
                'Registrado na SEFAZ em: %s %s' % (n_prot, dt, hr))
            
            # Destinatário
            self.rect(x=10, y=47, w=190, h=50, style='')
            self.line(10, 83, 200, 83)
            
            self.set_xy(x=11, y=48)
            txt = ("De acordo com as determinações legais vigentes, vimos por "
                   "meio desta comunicar-lhe que a Nota Fiscal, "
                   "abaixo referenciada, contêm irregularidades que estão "
                   "destacadas e suas respectivas correções, solicitamos que "
                   "sejam aplicadas essas correções ao executar seus "
                   "lançamentos fiscais.") 

            self.set_font('Times', '', 8)
            self.multi_cell(w=185, h=4, txt=txt, border=0, align='L', 
                fill=False)                  

            key = get_tag_text(node=inf_event, url=url, tag='chNFe')
            self.code128(key, 124, 60, height=15, thickness=0.265, 
                quiet_zone=True)

            self.set_font('Times', '', 7)
            self.text(x=130, y=78, txt=' '.join(chunks(key, 4)))
                     
            self.set_font('Times', 'B', 9)
            
            txt = "CNPJ Destinatário:  %s" % format_cpf_cnpj(get_tag_text(
                node=inf_ret_Event, url=url, tag='CNPJDest'))
            self.text(x=12, y=71, txt=txt)
            
            txt = "Nota Fiscal: %s - Série: %s" % ( 
                  '{0:011,}'.format(int(key[25:34])).replace( "," , "." ),
                  key[22:25])
            
            self.text(x=12, y=76, txt=txt)

            self.set_xy(x=11, y=84)
            txt = get_tag_text(node=det_event, url=url, tag='xCondUso')                        
            self.set_font('Times', 'I', 7)
            self.multi_cell(w=185, h=3, txt=txt, border=0, align='L', 
                fill=False)
                                  
            # Correções
            self.set_font('Times', 'B', 9)
            self.text(x=11, y=103, 
                txt='CORREÇÕES A SEREM CONSIDERADAS')

            self.rect(x=10, y=104, w=190, h=170, style='')
            
            self.set_xy(x=11, y=106)
            txt = get_tag_text(node=det_event, url=url, tag='xCorrecao')                        
            self.multi_cell(w=185, h=4, txt=txt, border=0, align='L', 
                fill=False)                  

            self.set_xy(x=11, y=265)
            txt = ("Este documento é uma representação gráfica da CC-e e "
            "foi impresso apenas para sua informação e não possue validade "
            "fiscal.\nA CC-e deve ser recebida e mantida em arquivo "
            "eletrônico XML e pode ser consultada através dos portais "
            "das SEFAZ.") 
            
            self.set_font('Times', 'I', 8)
            self.multi_cell(w=185, h=4, txt=txt, border=0, align='C', 
                fill=False)                  
                                 