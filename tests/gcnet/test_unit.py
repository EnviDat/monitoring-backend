import unittest

from gcnet.helpers import validate_date_gcnet

class TestGcnetHelpers(unittest.TestCase):

    def test_validate_date_gcnet(self):
        try:
            result = validate_date_gcnet("2020-11-12T09:08:17+00:00", "2020-12-12T09:08:17+00:00")
            date_range = result.get('timestamp_iso__range', ())
        except:
            date_range = ()
        self.assertEqual(len(date_range), 2, "Dates should be correct")

if __name__ == '__main__':
    unittest.main()
