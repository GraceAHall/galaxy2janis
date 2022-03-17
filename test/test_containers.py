


import os
import unittest

from containers.Container import Container
from containers.ContainerFetcher import CondaBiocontainerFetcher
from containers.ContainerCache import ContainerCache
from tool.requirements import CondaRequirement

SIMPLE_GXTOOL_ID = 'abricate'
SIMPLE_GXTOOL_VERSION = '1.0.1'
SIMPLE_MAIN_REQ = CondaRequirement(name='abricate', version='1.0.1')
SIMPLE_CONTAINER = Container(
    galaxy_id=SIMPLE_GXTOOL_ID,
    galaxy_version=SIMPLE_GXTOOL_VERSION,
    url='quay.io/biocontainers/abricate:1.0.1--h1341992_0',
    image_type='Docker',
    registry_host='quay.io/',
    requirement_id=SIMPLE_MAIN_REQ.get_text(),
    requirement_version=SIMPLE_MAIN_REQ.get_version()
)

HARD_GXTOOL_ID = 'samtools_idxstats'
HARD_GXTOOL_VERSION = '2.0.4'
HARD_MAIN_REQ = CondaRequirement(name='samtools', version='1.13')
HARD_CONTAINER = Container(
    galaxy_id=HARD_GXTOOL_ID,
    galaxy_version=HARD_GXTOOL_VERSION,
    url='quay.io/biocontainers/samtools:1.13--h8c37831_0',
    image_type='Docker',
    registry_host='quay.io/',
    requirement_id=HARD_MAIN_REQ.get_text(),
    requirement_version=HARD_MAIN_REQ.get_version()
)


class TestContainerFetching(unittest.TestCase):
    """
    tests biocontainer fetching given a tool id, tool version, and a Requirement()
    """

    def setUp(self) -> None:
        """
        creates a temp container cache for use. the tearDown() method will remove this after tests have run. 
        """
        self.temp_cache_dir = 'test/temp/container_cache.json'
        with open(self.temp_cache_dir, 'w') as fp:
            fp.write('{}')
    
    def test_simple_fetching(self) -> None:
        cf = CondaBiocontainerFetcher()
        container = cf.fetch(
            SIMPLE_GXTOOL_ID,
            SIMPLE_GXTOOL_VERSION,
            SIMPLE_MAIN_REQ
        )
        self.assertEquals(container, SIMPLE_CONTAINER)
    
    def test_hard_fetching(self) -> None:
        cf = CondaBiocontainerFetcher()
        container = cf.fetch(
            HARD_GXTOOL_ID,
            HARD_GXTOOL_VERSION,
            HARD_MAIN_REQ
        )
        self.assertEquals(container, HARD_CONTAINER)

    def test_caching_and_retrieval(self) -> None:
        cache: ContainerCache = ContainerCache(self.temp_cache_dir)
        # assert the container hasn't been stored
        self.assertFalse(cache.exists(SIMPLE_GXTOOL_ID, SIMPLE_GXTOOL_VERSION))
        # add then assert the container can be retrieved
        cache.add(SIMPLE_CONTAINER)
        self.assertTrue(cache.exists(SIMPLE_GXTOOL_ID, SIMPLE_GXTOOL_VERSION))
        container = cache.get(SIMPLE_GXTOOL_ID, SIMPLE_GXTOOL_VERSION)
        self.assertEquals(container, SIMPLE_CONTAINER)

    def tearDown(self) -> None:
        if os.path.exists(self.temp_cache_dir):
            os.remove(self.temp_cache_dir)
        

