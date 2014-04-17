"""Unit test for the elcpy module.
"""
import sys, unittest, elcpy

class Test_unittest(unittest.TestCase):
    def setUp(self):
        self.elc = elcpy.Elc()

    def test_routes(self):
        """Test the retrieval of `elcpy.Elc.routes`.
        """
        routes = self.elc.routes
        self.assertTrue(isinstance(routes, dict), "Returned routes object is a dict.")
        self.assertTrue(isinstance(self.elc._routes, dict), "Route dict has been cached.")

    def test_find_route_locations(self):
        """Test the `elcpy.Elc.find_route_locations` function.
        """
        #locations = (elcpy.RouteLocation(route="005", arm=5, reference_date="12/31/2013"))
        # Create a set of locations.
        locations = (elcpy.RouteLocation(route="005", arm=5),)
        out_locations = self.elc.find_route_locations(locations, "12/31/2013")
        self.assertEqual(len(out_locations), 1, "Result has single element.")
        self.assertIsInstance(out_locations[0], elcpy.RouteLocation, "The first element in the returned array is an `elcpy.RouteLocation`.")

    #def test_A(self):
    #    self.fail("Not implemented")

if __name__ == '__main__':
    unittest.main()
    sys.exit(0)
    #suite = unittest.TestLoader().loadTestsFromTestCase(Test_unittest)
    #unittest.TextTestRunner(verbosity=2).run(suite)