# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.config import config
from trytond import backend
from trytond.transaction import Transaction
import os
from jinja2 import Environment, FileSystemLoader

__all__ = ['Invoice', 'GenerateFacturaeStart']

ELECTRONET = config.get('electronet', 'facturae_path', default='/tmp')
ELECTRONET_TEMPLATE = 'template_facturae_3.2.xml'
ELECTRONET_TEMPLATE_SCHEMA = 'Facturaev3_2.xsd'
MODULE_PATH = os.path.dirname(os.path.abspath(__file__))


class Invoice:
    __metaclass__ = PoolMeta
    __name__ = 'account.invoice'

    @classmethod
    def __setup__(cls):
        super(Invoice, cls).__setup__()
        cls._error_messages.update({
            'missing_facturae_party_info': (
                    'Missing Factura-e info in party "%(party)s", '
                    'review the tab Factura-e of this party: "%(field)s"')
            })

    @classmethod
    def generate_facturae_electronet(cls, invoices, certificate_password=None):
        to_write = ([],)
        for invoice in invoices:
            if invoice.invoice_facturae:
                continue
            facturae_content = invoice.get_facturae()
            schema_file_path = os.path.join(MODULE_PATH,
                ELECTRONET_TEMPLATE_SCHEMA)
            invoice._validate_facturae(facturae_content, schema_file_path)
            invoice_facturae = facturae_content
            fname = '%s/%s' % (ELECTRONET,
                invoice.invoice_facturae_filename.replace('.xsig', '.xml'))
            with open(fname, 'w') as output_file:
                output_file.write(invoice_facturae)
            to_write[0].append(invoice)
            to_write += ({'invoice_facturae': invoice_facturae},)
        if to_write:
            cls.write(*to_write)

    def get_facturae(self):
        for party in (self.party, self.company.party):
            if not (party.oficina_contable or party.organo_gestor or
                    party.unidad_tramitadora or party.organo_proponente):
                self.raise_user_error('missing_facturae_party_info', {
                        'party': party.rec_name,
                        'field': '',
                        })
            elif not party.id_electronet:
                self.raise_user_error('missing_facturae_party_info', {
                        'party': party.rec_name,
                        'field': 'ID Electronet'
                        })

        jinja_env = Environment(
            loader=FileSystemLoader(MODULE_PATH),
            trim_blocks=True,
            lstrip_blocks=True,
            )
        jinja_template = self._get_jinja_template(jinja_env,
            ELECTRONET_TEMPLATE)
        return jinja_template.render(
            self._get_content_to_render(), ).encode('utf-8')


class GenerateFacturaeStart:
    __metaclass__ = PoolMeta
    __name__ = 'account.invoice.generate_facturae.start'

    @classmethod
    def __setup__(cls):
        super(GenerateFacturaeStart, cls).__setup__()
        cls.service.selection += [('electronet', 'Electronet')]
