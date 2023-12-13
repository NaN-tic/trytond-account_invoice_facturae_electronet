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

def module_path():
    return os.path.dirname(os.path.abspath(__file__))

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

    def send_facturae_electronet(self):
        if self.invoice_facturae_sent:
            return
        invoice_facturae = self.invoice_facturae
        fname = '%s/%s' % (ELECTRONET,
            self.invoice_facturae_filename.replace('.xsig', '.xml'))
        with open(fname, 'w', encoding='utf-8') as output_file:
            output_file.write(invoice_facturae)

    def get_facturae(self):
        for party in (self.party, self.company.party):
            missing_fields = set()
            for field in ('oficina_contable', 'organo_gestor',
                    'unidad_tramitadora'):
                if not getattr(party.addresses[0], field, False):
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
            loader=FileSystemLoader(module_path()),
            trim_blocks=True,
            lstrip_blocks=True,
            )
        template = ELECTRONET_TEMPLATE
        return self._get_jinja_template(jinja_env, template).render(
            self._get_content_to_render(), ).encode('utf-8')

    def _get_jinja_template(self, jinja_env, template):
        return jinja_env.get_template(template)


class GenerateFacturaeStart(metaclass=PoolMeta):
    __name__ = 'account.invoice.generate_facturae.start'

    @classmethod
    def __setup__(cls):
        super(GenerateFacturaeStart, cls).__setup__()
        cls.service.selection += [('electronet', 'Electronet')]
