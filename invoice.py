# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.model import fields
from trytond.config import config
import os
from jinja2 import Environment, FileSystemLoader
from trytond.i18n import gettext
from trytond.exceptions import UserError

__all__ = ['Invoice', 'GenerateFacturaeStart']

ELECTRONET = config.get('electronet', 'facturae_path', default='/tmp')
ELECTRONET_TEMPLATE = 'template_facturae_3.2.xml'
ELECTRONET_TEMPLATE_SCHEMA = 'Facturaev3_2.xsd'
MODULE_PATH = os.path.dirname(os.path.abspath(__file__))


class Invoice(metaclass=PoolMeta):
    __name__ = 'account.invoice'

    sale_point_code = fields.Function(fields.Char('Sale Point Code'),
        'get_sale_point_code')

    @classmethod
    def get_sale_point_code(cls, invoices, name):
        sale_points = {}
        for invoice in invoices:
            sale_point = u''
            address = invoice.shipment_origin_address
            if address:
                sale_point = address.electronet_sale_point
            sale_points[invoice.id] = sale_point
        return sale_points

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
            invoice_facturae = str(facturae_content)
            fname = '%s/%s' % (ELECTRONET,
                invoice.invoice_facturae_filename.replace('.xsig', '.xml'))
            with open(fname, 'w', encoding='utf-8') as output_file:
                output_file.write(invoice_facturae)
            to_write[0].append(invoice)
            to_write += ({'invoice_facturae': invoice_facturae},)
        if to_write:
            cls.write(*to_write)

    def get_facturae(self):
        for party in (self.party, self.company.party):
            missing_fields = set()
            for field in ('oficina_contable', 'organo_gestor',
                    'unidad_tramitadora'):
                if not getattr(party, field, False):
                    missing_fields.add(field)

            if len(missing_fields) > 2:
                fields = ', '.join(missing_fields)
                raise UserError(gettext('missing_facturae_party_info',
                        party=party.rec_name,
                        field=fields))
            if not party.id_electronet:
                raise UserError(gettext('missing_facturae_party_info',
                        party=party.rec_name,
                        field='ID Electronet'))

            if not self.invoice_address.electronet_sale_point:
                raise UserError(gettext('missing_facturae_party_address_info',
                        party=party.rec_name,
                        field='Electronet Sale Point'))

        jinja_env = Environment(
            loader=FileSystemLoader(MODULE_PATH),
            trim_blocks=True,
            lstrip_blocks=True,
            )
        jinja_template = self._get_jinja_template(jinja_env,
            ELECTRONET_TEMPLATE)
        return jinja_template.render(
            self._get_content_to_render(), ).encode('utf-8')


class GenerateFacturaeStart(metaclass=PoolMeta):
    __name__ = 'account.invoice.generate_facturae.start'

    @classmethod
    def __setup__(cls):
        super(GenerateFacturaeStart, cls).__setup__()
        cls.service.selection += [('electronet', 'Electronet')]
