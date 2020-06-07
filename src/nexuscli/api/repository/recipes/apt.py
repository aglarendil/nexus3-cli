from nexuscli.api.repository.base_models import Repository
from nexuscli.api.repository.base_models import HostedRepository
from nexuscli.api.repository.base_models import ProxyRepository

__all__ = ['AptHostedRepository', 'AptProxyRepository', 'AptGroupRepository']


class _AptRepository(Repository):
    DEFAULT_RECIPE = 'apt'
    RECIPES = ('apt',)

    def __init__(self, name: str, distribution: str = 'bionic', **kwargs):
        self.distribution = distribution
        kwargs.update({'recipe': 'apt'})
        super().__init__(name, **kwargs)

    @property
    def configuration(self):
        repo_config = super().configuration

        repo_config['attributes'].update({
            'apt': {
                'distribution': self.distribution,
            }
        })

        return repo_config


class AptHostedRepository(_AptRepository, HostedRepository):
    def __init__(self, name: str, gpg_keypair: str = None, passphrase: str = None, **kwargs):
        self.gpg_keypair = gpg_keypair
        self.passphrase = passphrase
        self.label = kwargs.pop('label', None)
        self.origin = kwargs.pop('origin', None)
        super().__init__(name, **kwargs)

    @property
    def configuration(self):
        repo_config = super().configuration
        repo_config['attributes'].update({
            'aptSigning': {
                'keypair': self.gpg_keypair,
                'passphrase': self.passphrase
            }
        })

        if self.label is not None:
            repo_config['attributes']['apt']['label'] = self.label
        if self.origin is not None:
            repo_config['attributes']['apt']['origin'] = self.origin

        return repo_config


class AptProxyRepository(_AptRepository, ProxyRepository):
    def __init__(self, name,
                 flat=False,
                 **kwargs):
        self.flat = flat
        super().__init__(name, **kwargs)

    @property
    def configuration(self):
        repo_config = super().configuration

        repo_config['attributes']['apt']['flat'] = self.flat

        return repo_config


class AptGroupRepository:
    def __init__(self):
        raise NotImplementedError
