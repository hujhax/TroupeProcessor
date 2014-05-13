import ProcessTroupeData
import unittest


class SimpleValidDatabases(unittest.TestCase):

    def oneRowDatabase(self):
        """ProcessTroupeData should convert a one-row database to a tuple."""
        troupe_dict = ProcessTroupeData.processTroupeData("test/OneRow.ods")
        desired_fields = [
            "site1", "cast1", "blurb1", "deal1", "photo1", "video1"]
        desired_result = ProcessTroupeData.TroupeFields._make(desired_fields)
        self.assertEqual(troupe_dict["name1"], desired_result)
