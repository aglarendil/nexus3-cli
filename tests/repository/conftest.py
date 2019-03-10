import pytest

from nexuscli.repository import RepositoryCollection


@pytest.fixture
def repository_collection(mocker):
    fixture = RepositoryCollection(client=mocker.Mock())
    return fixture
