import json

from nexuscli import exception, nexus_util
from .model import CleanupPolicy


class CleanupPolicyCollection(object):
    """
    A class to manage Nexus 3 Cleanup Policies.

    Args:
        client(nexuscli.nexus_client.NexusClient): the client instance that
            will be used to perform operations against the Nexus 3 service. You
            must provide this at instantiation or set it before calling any
            methods that require connectivity to Nexus.

    Attributes:
        client(nexuscli.nexus_client.NexusClient): as per ``client``
            argument of :class:`RepositoryCollection`.
    """
    GROOVY_SCRIPT_NAME = 'nexus3-cli-cleanup-policy'

    def __init__(self, client=None):
        self._client = client
        script_content = nexus_util.groovy_script(self.GROOVY_SCRIPT_NAME)
        self._client.scripts.create_if_missing(
            self.GROOVY_SCRIPT_NAME, script_content)

    def create_or_update(self, cleanup_policy):
        """
        Creates the given Cleanup Policy in the Nexus repository. If a policy
        with the same name already exists, it will be updated.

        :param cleanup_policy: the policy to create or update.
        :type cleanup_policy: CleanupPolicy
        :return: None
        """
        if not isinstance(cleanup_policy, CleanupPolicy):
            raise TypeError(
                f'cleanup_policy ({type(cleanup_policy)}) must be a '
                f'CleanupPolicy')

        script_args = json.dumps(cleanup_policy.configuration)
        try:
            response = self._client.scripts.run(
                self.GROOVY_SCRIPT_NAME, data=script_args)
        except exception.NexusClientAPIError:
            raise exception.NexusClientCreateCleanupPolicyError(
                cleanup_policy.configuration['name'])

        result = json.loads(response['result'])
        if result['name'] != cleanup_policy.configuration['name']:
            raise exception.NexusClientCreateCleanupPolicyError(response)

    def get_by_name(self, name):
        """
        Get a Nexus 3 cleanup policy by its name.

        :param name: name of the wanted policy
        :type name: str
        :return: the requested object
        :rtype: CleanupPolicy
        :raise exception.NexusClientInvalidRepository: when a repository with
            the given name isn't found.
        """
        script_args = json.dumps({'name': name})

        try:
            response = self._client.scripts.run(
                self.GROOVY_SCRIPT_NAME, data=script_args)
        except exception.NexusClientAPIError:
            raise exception.NexusClientInvalidCleanupPolicy(name)

        cleanup_policy = json.loads(response['result'])

        return CleanupPolicy(self._client, **cleanup_policy)
