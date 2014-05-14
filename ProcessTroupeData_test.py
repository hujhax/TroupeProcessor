import ProcessTroupeData
import unittest


class SimpleValidDatabases(unittest.TestCase):

    def validate_troupe_data(self, file_name, troupe_name, troupe_data,
                             num_troupes=None):
        dict = ProcessTroupeData.process_troupe_data(file_name)

        self.assertTrue(troupe_name in dict)
        dict_data = dict[troupe_name]

        if num_troupes:
            self.assertEqual(len(dict), num_troupes)

        for k, v in troupe_data:
            try:
                self.assertEqual(dict_data[k], v)
            except KeyError:
                self.assertEqual("no value", v)

    def test_one_row(self):
        """We should be able to process a one-row database."""

        test_data = [("site", "www.site1"),
                     ("cast", {"cast1"}),
                     ("blurb", "blurb1"),
                     ("deal", "deal1"),
                     ("photo", "www.photo1"),
                     ("video", "www.video1")]
        self.validate_troupe_data("test/OneRow.ods", "name1", test_data, 1)

    def test_two_rows_one_troupe(self):
        """Two rows describing one troupe should result in one item."""

        test_data = [("site", "www.site2"),
                     ("cast", {"cast1"}),
                     ("blurb", "blurb1"),
                     ("deal", "deal1"),
                     ("photo", "www.photo1"),
                     ("video", "www.video1")]
        self.validate_troupe_data("test/TwoRows.ods", "name1", test_data, 1)

    def test_ignore_invalid_urls(self):
        """We should ignore invalid URLs for site/photo/video"""

        test_data = [("site", "no value"),
                     ("cast", {"cast1"}),
                     ("photo", "no value"),
                     ("video", "no value")]
        self.validate_troupe_data("test/IgnoreInvalidURLs.ods", "name1",
                                  test_data)

    def test_use_longer_strings(self):
        """We should favor longer strings for the blurb and deal fields."""

        test_data = [("blurb", "longer blurb"),
                     ("deal", "longer deal")]
        self.validate_troupe_data("test/LongerStrings.ods", "name1",
                                  test_data)

    def test_casts(self):
        """We should load and collate cast lists for each troupe."""

        separators_data = [("cast", {"A", "B", "C", "D", "E", "F"})]
        self.validate_troupe_data("test/Casts.ods", "separators",
                                  separators_data)

        whitespace_data = [("cast", {"A"})]
        self.validate_troupe_data("test/Casts.ods", "whitespace",
                                  whitespace_data)

        union_data = [("cast", {"A", "B", "C"})]
        self.validate_troupe_data("test/Casts.ods", "union",
                                  union_data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
