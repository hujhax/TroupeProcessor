import ProcessTroupeData
import unittest


class ValidateDatabaseProcessor(unittest.TestCase):

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
                     ("video", {"www.video1"})]
        self.validate_troupe_data("test/OneRow.ods", "name1", test_data, 1)

    def test_two_rows_one_troupe(self):
        """Two rows describing one troupe should result in one item."""

        test_data = [("site", "www.site2"),
                     ("cast", {"cast1"}),
                     ("blurb", "blurb1"),
                     ("deal", "deal1"),
                     ("photo", "www.photo1"),
                     ("video", {"www.video1"})]
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

        separators_data = [("cast", {"A", "B", "C", "D", "E", "F", "G", "H"})]
        self.validate_troupe_data("test/Casts.ods", "separators",
                                  separators_data)

        whitespace_data = [("cast", {"A"})]
        self.validate_troupe_data("test/Casts.ods", "whitespace",
                                  whitespace_data)

        union_data = [("cast", {"A", "B", "C"})]
        self.validate_troupe_data("test/Casts.ods", "union",
                                  union_data)

    def test_start_end_years(self):
        """We should pick the min and max years from a troupe's entries."""

        test_data = [("start_year", "2005"),
                     ("end_year", "2009")]
        self.validate_troupe_data("test/StartEndYears.ods", "name1",
                                  test_data)

    def test_video_accumulation(self):
        """We should accumulate all troupe videos into a set."""

        test_data = [("video", {"www.a", "www.b", "www.c"})]

        self.validate_troupe_data("test/VideoSet.ods", "name1",
                                  test_data)

    def test_performed_before(self):
        """We should note if the troupe has ever performed before."""

        test_1 = [("performed_before", "y")]
        test_2 = [("performed_before", "n")]
        test_3 = [("performed_before", "y")]

        self.validate_troupe_data("test/PerformedBefore.ods", "yestroupe1",
                                  test_1)
        self.validate_troupe_data("test/PerformedBefore.ods", "notroupe",
                                  test_2)
        self.validate_troupe_data("test/PerformedBefore.ods", "yestroupe2",
                                  test_3)

    def test_blurb_deal_years(self):
        """Store the year associated with the longest blurb/deal."""

        test_blurb = [("blurb_year", "2007")]
        test_deal = [("deal_year", "2010")]

        self.validate_troupe_data("test/BlurbDealYears.ods", "Deal",
                                  test_blurb)
        self.validate_troupe_data("test/BlurbDealYears.ods", "Blurb",
                                  test_deal)


class ValidatePageGenerator(unittest.TestCase):

    def validate_page_inclusions(self, troupe_data, yes_strings={},
                                 no_strings={}, debug_output=False):
        if not 'name' in troupe_data:
            troupe_data['name'] = "test_name"

        test_page = ProcessTroupeData.create_test_page(troupe_data['name'],
                                                       troupe_data)

        if (debug_output):
            print test_page.encode('utf8')

        {self.assertTrue(test_string in test_page)
            for test_string in yes_strings}

        {self.assertTrue(test_string not in test_page)
            for test_string in no_strings}

    def test_blank_dict(self):
        """Blank dictionary fields should not throw off the page generator."""

        self.validate_page_inclusions({})

    def test_simplest_dict(self):
        """Simple troupe info should omit all optional sections."""

        troupe_info = {"name": "bob"}
        yes_strings = {"???", "'''bob''' was an improv troupe",
                       "[[Category:Troupes]]"}
        no_strings = {"[[Category:Active]]", "== Press Blurb ==",
                      "== ""What's Your Deal?"" ==", "== Media ==",
                      "== Summary ==", "== More Information =="}
        self.validate_page_inclusions(troupe_info, yes_strings, no_strings)

    def test_normal_years(self):
        """Non-2014 years should show up in the resulting 'inactive' page."""

        troupe_info = {"start_year": "2010", "end_year": "2012"}
        yes_strings = {"2010-2012", "was an improv troupe"}
        no_strings = {"[[Category:Active]]"}
        self.validate_page_inclusions(troupe_info, yes_strings, no_strings)

    def test_current_year(self):
        """2014 should show up as "Present" in the "active" page."""

        troupe_info = {"start_year": "2010", "end_year": "2014"}
        yes_strings = {"2010-Present", "is an improv troupe",
                       "[[Category:Active]]"}
        self.validate_page_inclusions(troupe_info, yes_strings)

    def test_blurb(self):
        """Blurb section should show up correctly."""

        troupe_info = {"blurb": "They like to move it",
                       "blurb_year": "2002"}
        yes_strings = {"== Press Blurb ==", "They like to move it",
                       "taken from a 2002 application", "== Summary =="}
        self.validate_page_inclusions(troupe_info, yes_strings)

    def test_deal(self):
        """Deal section should show up correctly."""

        troupe_info = {"deal": "They like to move it",
                       "deal_year": "2002"}
        yes_strings = {"What's Your Deal?", "They like to move it",
                       "on a 2002 application", "== Summary =="}
        self.validate_page_inclusions(troupe_info, yes_strings)

    def test_cast(self):
        """Cast lists should show up alphabetized and formatted."""

        troupe_info = {"cast": {"a a", "c c", "b b"}}
        y_strings = {"{{ Unbulleted list | [[a a]] | [[b b]] | [[c c]] }}"}
        self.validate_page_inclusions(troupe_info, y_strings)

    def test_duos(self):
        """The duo category should only show up for a cast size of 2."""

        duo_info = {"cast": {"a a", "c c"}}
        no_duo_info = {"cast": {"a a", "c c", "b b"}}
        duo_category = {"[[Category:Duos]]"}
        self.validate_page_inclusions(duo_info, duo_category)
        self.validate_page_inclusions(no_duo_info, no_strings=duo_category)

    def test_videos(self):
        """The set of videos should translate to a bulleted list of videos."""

        troupe_info = {"video": {"video1", "video2"}}
        yes_strings = {"== Media ==", "video1", "video1", "Video #1",
                       "Video #2"}
        self.validate_page_inclusions(troupe_info, yes_strings)

    def test_site(self):
        """We should show the troupe's web site, if available."""

        troupe_info = {"site": "http://www.mysite.com"}
        yes_strings = {"== More Information ==", "http://www.mysite.com",
                       "The troupe's web site."}
        self.validate_page_inclusions(troupe_info, yes_strings)

    def test_single_year_display(self):
        """We should display "2010", not "2010-2010"."""
        one_year = {'start_year': "2010", 'end_year': "2010"}
        one_yes = {"2010"}
        one_no = {"2010-2010"}
        self.validate_page_inclusions(one_year, one_yes, one_no)

        two_years = {'start_year': "2010", 'end_year': "2012"}
        two_yes = {"2010-2012"}
        self.validate_page_inclusions(two_years, two_yes)

        this_year = {'start_year': "2014", 'end_year': "2014"}
        this_yes = {"2014-Present"}
        self.validate_page_inclusions(this_year, this_yes)

    def test_unicode(self):
        """The processor shouldn't choke on weird unicode strings."""

        troupe_info = {"blurb": u'La Pe\xf1a', "blurb_year": "2001"}
        self.validate_page_inclusions(troupe_info)

    def test_fixed_carriage_returns(self):
        """We should duplicate carriage returns in the blurb/deal fields."""

        troupe_info = {"blurb": "a\nb", "deal": "c\nd", "blurb_year": "2011",
                       "deal_year": "2010"}
        yes_strings = {"a\n\nb", "c\n\nd"}
        no_strings = {"a\nb", "c\nd"}
        self.validate_page_inclusions(troupe_info, yes_strings, no_strings)


if __name__ == "__main__":
    unittest.main(verbosity=2)
