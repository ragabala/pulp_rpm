# coding=utf-8
"""Tests that copy rpm repositories."""
import unittest

from pulp_smash import api, config
from pulp_smash.pulp3.constants import  REPO_PATH
from pulp_smash.pulp3.utils import (
    gen_repo,
    get_added_content_summary,
    get_content_summary,
    sync,
)

from pulp_rpm.tests.functional.utils import (
    gen_rpm_remote,
)
from pulp_rpm.tests.functional.constants import (
    RPM_FIXTURE_SUMMARY,
    RPM_REMOTE_PATH,
    RPM_COPY_REQUEST,
)


class CopyContentTestCase(unittest.TestCase):
    """Test whether content can be copied between repos"""

    @classmethod
    def setUpClass(cls):
        """Create class-wide variables."""
        cls.cfg = config.get_config()
        cls.client = api.Client(cls.cfg, api.json_handler)

    def test_all(self):
        """Test whether a particular repository content can be copied.

        1. Create an RPM repository.
        2. Populate it with content.
        3. Create a second, empty RPM repository.
        4. Use the copy API endpoint to copy all content from the first
           repository into the second repository.
        5. Check that a new repository version was created in the second
            repository, and that it has identical content to the first.
        """
        # Step 1
        repo = self.client.post(REPO_PATH, gen_repo())
        self.addCleanup(self.client.delete, repo['_href'])
        remote = self.client.post(RPM_REMOTE_PATH, gen_rpm_remote())
        self.addCleanup(self.client.delete, remote['_href'])

        # Step 2
        sync(self.cfg, remote, repo)

        # Step 3
        repo2 = self.client.post(REPO_PATH, gen_repo())
        self.addCleanup(self.client.delete, repo2['_href'])

        # Step 4
        body = {
            'source_repository': repo['_href'],
            'destination_repository': repo2['_href']
        }

        self.client.post(RPM_COPY_REQUEST, body)

        # Step 5
        self.assertIsNotNone(repo2['_latest_version_href'])
        self.assertDictEqual(
            get_content_summary(repo2),
            RPM_FIXTURE_SUMMARY
        )
        self.assertDictEqual(
            get_added_content_summary(repo),
            RPM_FIXTURE_SUMMARY
        )
