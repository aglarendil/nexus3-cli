from urllib.parse import urlparse

from nexuscli.api.repository.base_models.repository import Repository


class ProxyRepository(Repository):
    """
    A proxy Nexus repository.

    :param name: name of the repository.
    :type name: str
    :param remote_url: The URL of the repository being proxied, including the
        protocol scheme.
    :type remote_url: str
    :param auto_block: Auto-block outbound connections on the repository if
        remote peer is detected as unreachable/unresponsive.
    :type auto_block: bool
    :param content_max_age: How long (in minutes) to cache artifacts before
        rechecking the remote repository. Release repositories should use -1.
    :type content_max_age: int
    :param metadata_max_age: How long (in minutes) to cache metadata before
        rechecking the remote repository.
    :type metadata_max_age: int
    :param negative_cache_enabled: Cache responses for content not present in
        the proxied repository
    :type negative_cache_enabled: bool
    :param negative_cache_ttl: How long to cache the fact that a file was not
        found in the repository (in minutes)
    :type negative_cache_ttl: int
    :param kwargs: see :class:`Repository`
    """

    TYPE = 'proxy'

    def __init__(self, name,
                 remote_url=None,
                 auto_block=True,
                 content_max_age=1440,
                 metadata_max_age=1440,
                 negative_cache_enabled=True,
                 negative_cache_ttl=1440,
                 remote_auth_type=None,
                 remote_username=None,
                 remote_password=None,
                 use_trust_store=False,
                 **kwargs):
        self.remote_url = remote_url
        self.auto_block = auto_block
        self.content_max_age = content_max_age
        self.metadata_max_age = metadata_max_age
        self.negative_cache_enabled = negative_cache_enabled
        self.negative_cache_ttl = negative_cache_ttl
        self.remote_username = remote_username
        self.remote_password = remote_password
        self.remote_auth_type = remote_auth_type
        self.use_trust_store = use_trust_store

        super().__init__(name, **kwargs)

        self.__validate_params()

    def __validate_params(self):
        if not isinstance(self.remote_url, str):
            raise ValueError('remote_url must be a str')

        parsed_url = urlparse(self.remote_url)
        if not (parsed_url.scheme and parsed_url.netloc):
            raise ValueError(
                f'remote_url={self.remote_url} is not a valid URL')

    @property
    def configuration(self):
        """
        As per :py:obj:`Repository.configuration` but specific to this
        repository recipe and type.

        :rtype: str
        """
        repo_config = super().configuration

        repo_config['attributes'].update({
            'httpclient': {
                'blocked': False,
                'autoBlock': self.auto_block,
                'connection': {'useTrustStore': self.use_trust_store}
            },
            'proxy': {
                'remoteUrl': self.remote_url,
                'contentMaxAge': self.content_max_age,
                'metadataMaxAge': self.metadata_max_age,
            },
            'negativeCache': {
                'enabled': self.negative_cache_enabled,
                'timeToLive': self.negative_cache_ttl,
            },
        })

        if self.remote_auth_type == 'username':
            repo_config['attributes']['httpclient'].update({
                'authentication': {
                    'type': self.remote_auth_type,
                    'username': self.remote_username,
                    'password': self.remote_password
                }
            })
        return repo_config
