import unittest

from melvor_wiki_bot.wiki.manifest import load_manifest, WikiManifestEntry


class TestManifest(unittest.TestCase):
    def test_load_manifest_default_path(self):
        manifest = load_manifest()
        self.assertGreaterEqual(len(manifest), 1)
        self.assertIsInstance(manifest[0], WikiManifestEntry)


if __name__ == "__main__":
    unittest.main()
