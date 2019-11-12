import papis
import logging
import os.path
import papis.plugin
from typing import Optional, List, Dict, Any, Callable

logger = logging.getLogger('importer')


class Context:
    def __init__(self) -> None:
        self.data = dict()  # type: Dict[str, Any]
        self.files = []  # type: List[str]

    def __bool__(self) -> bool:
        return bool(self.files) or bool(self.data)


class Importer:

    """This is the base class for every importer"""

    def __init__(self, uri: str = "", name: str = "",
            ctx: Context = Context()):
        """
        :param uri: uri
        :type  uri: str
        :param name: Name of the importer
        :type  name: str
        """
        self.ctx = Context()
        assert(isinstance(uri, str))
        assert(isinstance(name, str))
        assert(isinstance(self.ctx, Context))
        self.uri = uri  # type: str
        self.name = name or os.path.basename(__file__)  # type: str
        self.logger = logging.getLogger("importer:{0}".format(self.name))

    @classmethod
    def match(cls, uri: str):
        """This method should be called to know if a given uri matches
        the importer or not.

        For example, a valid match for archive would be:
        .. code:: python

            return re.match(r".*arxiv.org.*", uri)

        it will return something that is true if it matches and something
        falsely otherwise.

        :param uri: uri where the document should be retrieved from.
        :type  uri: str
        """
        raise NotImplementedError(
            "Matching uri not implemented for this importer")

    @classmethod
    def match_data(cls, data: Dict[str, Any]) -> None:
        """Get a dictionary of data and try to decide if there is
        a valid uri in it.

        :param data: Data to look into
        :type  data: dict
        """
        raise NotImplementedError(
            "Matching data not implemented for this importer")

    def fetch(self) -> str:
        """
        can return a dict to update the document with
        """
        raise NotImplementedError()

    def __str__(self) -> str:
        return 'Importer({0}, uri={1})'.format(self.name, self.uri)


def _extension_name() -> str:
    return "papis.importer"


def get_import_mgr() -> papis.plugin.ExtensionManager:
    """Get the import manager
    :returns: Import manager
    """
    return papis.plugin.get_extension_manager(_extension_name())


def available_importers() -> List[str]:
    """Get the available importers defined.
    :returns: List of importer names
    :rtype:  list(str)
    """
    return papis.plugin.get_available_entrypoints(_extension_name())


def get_importers() -> List[Importer]:
    return [e.plugin for e in get_import_mgr()]


def get_importer_by_name(name: str) -> Any:
    """Get importer by name
    :param name: Name of the importer
    :type  name: str
    :returns: The importer
    :rtype:  Importer
    """
    assert(isinstance(name, str))
    return get_import_mgr()[name].plugin


def cache(f: Callable[[Importer], Any]) -> Callable[[Importer], Any]:
    """
    This is a decorator to be used if a method of an Importer
    is to be cached, i.e., if the context of the importer is already
    set, then one does not need to run the function anymore, even if
    it is explicitly run.

    :param self: Method of an Importer
    """
    def wrapper(self: Importer) -> Any:
        if not self.ctx:
            f(self)
    return wrapper
