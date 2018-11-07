# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = ['Party', 'Address']


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'

    id_electronet = fields.Char('Id Electronet')

class Address(metaclass=PoolMeta):
    __name__ = 'party.address'

    electronet_sale_point = fields.Char('Electronet Sale Point')
