import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
import get_interfacelist_from_tag as GetInterface

class TestGetInterfaceFromTag(unittest.TestCase):

    def test_compare_list_versions(self):
        stored_version = [[4, 1, 2, 5, 6], [4], [4, 0, 1]]
        version_to_eval = [[4, 1, 3, 0], [3], [4, 0, 0, 1]]
        test_results = []
        for elem in range(len(stored_version)):
            this_version_is_latest = GetInterface.compare_list_versions(
                version_parts=version_to_eval[elem],
                latest_version=stored_version[elem])
            test_results.append(this_version_is_latest)

        self.assertEqual(test_results, [True, False, False])

    def test_get_version_parts(self):
        file_name = '4.1.2.xlsx'
        version_parts = GetInterface.get_version_parts(file_name)
        self.assertEqual(version_parts, [4, 1, 2])

if __name__ == '__main__':
    unittest.main()
