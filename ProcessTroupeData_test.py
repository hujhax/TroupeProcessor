import ProcessTroupeData
import unittest


class SimpleValidDatabases(unittest.TestCase):

    def validate_troupe_data(self, file_name, name, test_data):
        dict = ProcessTroupeData.process_troupe_data(file_name)

        self.assertTrue(name in dict)
        dict_data = dict[name]

        for k, v in test_data:
            self.assertEqual(dict_data[k], v)

    def test_one_row(self):
        """We should be able to process a one-row database."""

        test_data = [("site", "www.site1"),
                     ("cast", "cast1"),
                     ("blurb", "blurb1"),
                     ("deal", "deal1"),
                     ("photo", "www.photo1"),
                     ("video", "www.video1")]
        self.validate_troupe_data("test/OneRow.ods", "name1", test_data)

if __name__ == "__main__":
    unittest.main(verbosity=2)
