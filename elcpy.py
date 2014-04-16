import urllib2, json, re, urllib

_BASEURL = "http://www.wsdot.wa.gov/geoservices/arcgis/rest/services/Shared/ElcRestSOE/MapServer/exts/ElcRestSoe/"
_ROUTES = "routes"
_FIND_ROUTE_LOCATIONS = urllib.quote("Find Route Locations")
_FIND_NEAREST_ROUTE_LOCATIONS = urllib.quote("Find Nearest Route Locations")

class RouteLocation(object):
    """Represents a route location object used as input and output from the ELC.
    """
    def __init__(self, id_=None,
                 route=None,
                 decrease=None,
                 arm=None,
                 srmp=None,
                 back=None,
                 reference_date=None,
                 response_date=None,
                 realignment_date=None,
                 end_arm=None,
                 end_srmp=None,
                 end_back=None,
                 end_reference_date=None,
                 end_response_date=None,
                 end_realign_date=None,
                 armcalc_return_code=None,
                 armcalc_end_return_code=None,
                 armcalc_return_message=None,
                 armcalc_end_return_message=None,
                 locating_error=None,
                 route_geometry=None,
                 event_point=None,
                 distance=None,
                 angle=None):
        """Creates a new instance of RouteLocation.

        Parameters:

        - `id_`: Value for the id_ property.
        - `route`: Value for the route property.
        - `decrease`: Value for the decrease property.
        - `arm`: Value for the arm property.
        - `srmp`: Value for the srmp property.
        - `back`: Value for the back property.
        - `reference_date`: Reference date in "MM-DD-YYYY" format.
        - `response_date`: Response date in "MM-DD-YYYY" format.
        - `realignment_date`: Value for the realignment_date property.
        - `end_arm`: Value for the end_arm property.
        - `end_srmp`: Value for the end_srmp property.
        - `end_back`: Value for the end_back property.
        - `end_reference_date`: Value for the end_reference_date property.
        - `end_response_date`: Value for the end_response_date property.
        - `end_realign_date`: Value for the end_realign_date property.
        - `armcalc_return_code`: Value for the armcalc_return_code property.
        - `armcalc_end_return_code`: Value for the armcalc_end_return_code property.
        - `armcalc_return_message`: Value for the armcalc_return_message property.
        - `armcalc_end_return_message`: Value for the armcalc_end_return_message property.
        - `locating_error`: Value for the locating_error property.
        - `route_geometry`: Value for the route_geometry property.
        - `event_point`: Value for the event_point property.
        - `distance`: Value for the distance property.
        - `angle`: Value for the angle property.
        """

        #####

        self.Id = id_
        self.Route = route
        self.Decrease = decrease

        self.Arm = arm
        self.Srmp = srmp
        self.Back = back
        self.ReferenceDate = reference_date
        self.ResponseDate = response_date
        self.RealignmentDate = realignment_date

        self.EndArm = end_arm
        self.EndSrmp = end_srmp
        self.EndBack = end_back
        self.EndReferenceDate = end_reference_date
        self.EndResponseDate = end_response_date
        self.EndRealignDate = end_realign_date

        self.ArmCalcReturnCode = armcalc_return_code
        self.ArmCalcEndReturnCode = armcalc_end_return_code
        self.ArmCalcReturnMessage = armcalc_return_message
        self.ArmCalcEndReturnMessage = armcalc_end_return_message

        self.LocatingError = locating_error
        self.RouteGeometry = route_geometry
        self.EventPoint = event_point
        self.Distance = distance
        self.Angle = angle
        return super(RouteLocation, self).__init__()

class RouteLocationEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, RouteLocation):
            return super(RouteLocationEncoder, self).default(obj)

        d = obj.__dict__
        output = {}
        for key in d:
            if d[key] is not None:
                output[key] = d[key]
        return output

def dictToRouteLocation(d):
    loc = RouteLocation()

    loc.Id = d.get("Id", None)
    loc.Route = d.get("Route", None)
    loc.Decrease = d.get("Decrease", None)

    loc.Arm = d.get("Arm", None)
    loc.Srmp = d.get("Srmp", None)
    loc.Back = d.get("Back", None)
    loc.ReferenceDate = d.get("ReferenceDate", None)
    loc.ResponseDate = d.get("ResponseDate", None)
    loc.RealignmentDate = d.get("RealignmentDate", None)

    loc.EndArm = d.get("EndArm", None)
    loc.EndSrmp = d.get("EndSrmp", None)
    loc.EndBack = d.get("EndBack", None)
    loc.EndReferenceDate = d.get("EndReferenceDate", None)
    loc.EndResponseDate = d.get("EndResponseDate", None)
    loc.EndRealignDate = d.get("EndRealignDate", None)

    loc.ArmCalcReturnCode = d.get("ArmCalcReturnCode", None)
    loc.ArmCalcEndReturnCode = d.get("ArmCalcEndReturnCode", None)
    loc.ArmCalcReturnMessage = d.get("ArmCalcReturnMessage", None)
    loc.ArmCalcEndReturnMessage = d.get("ArmCalcEndReturnMessage", None)

    loc.LocatingError = d.get("LocatingError", None)
    loc.RouteGeometry = d.get("RouteGeometry", None)
    loc.EventPoint = d.get("EventPoint", None)
    loc.Distance = d.get("Distance", None)
    loc.Angle = d.get("Angle", None)

    return loc


#class RouteLocationDecoder(json.JSONDecoder):
#    def decode(self, s, _w = WHITESPACE.match):
#        return super(RouteLocationDecoder, self).decode(s, _w)

class Elc(object):
    """This object is used to call the ELC REST SOE endpoint.

    Parameters:

    - `url`: The URL for the ELC REST SOE. You only need to override this if you don't want to use the `default value <http://www.wsdot.wa.gov/geoservices/arcgis/rest/services/Shared/ElcRestSOE/MapServer/exts/ElcRestSoe/>`_.
    """
    def __init__(self, url=_BASEURL):
        self.url = url
        # __routes will be used to store route data after the first request for it.
        self._routes = None
        return super(Elc, self).__init__()

    def get_routes(self):
        """Returns a dict. The main dict is keyed by LRS year.
        Each item in the dict is another dict.
        These dicts are keyed by route ID.

        Their values are an integer from 1 to 4 indicating the route type:

        1. Increase
        2. Decrease
        3. Increase | Decrease (Both)
        4. Ramp
        """
        if self._routes is None:
            url = self.url + _ROUTES + "?f=json"
            f = urllib2.urlopen(url)
            self._routes = json.load(f)
        return self._routes

    def find_route_locations(self, locations, reference_date=None, out_sr=None, lrs_year=None):
        """Finds the route locations.

        Parameters:

        - `locations`: A collection of RouteLocation objects
        - `reference_date`: The date that the `locations` were collected. If all of the `locations` objects have a `referenceDate` specified then this parameter is optional.
        - `out_sr`: Optional. The output spatial reference system WKID. If omitted the results will be in the LRS's spatial reference system (2927 as of this writing).
        - `lrs_year`: Optional. If you want a year other than the most current one, provide its name here. See `self.routes` for a list of routes.
        """
        url = self.url + _FIND_ROUTE_LOCATIONS
        # Convert the locations into JSON strings.
        locations_json = json.dumps(locations, cls=RouteLocationEncoder)
        paramsDict = { 
                      "f": "json", 
                      "locations": locations_json 
                    }
        if reference_date is not None:
            paramsDict["referenceDate"] = str(reference_date)
        if out_sr is not None:
            paramsDict["outSR"] = str(out_sr)
        if lrs_year is not None:
            paramsDict["lrsYear"] = lrs_year
        # Convert the parameters into a query string.
        qs = urllib.urlencode(paramsDict.items())
        url += "?" + qs
        f = urllib2.urlopen(url)
        # Cast results to RouteLocation objects.
        return json.load(f, object_hook=dictToRouteLocation)

    def find_nearest_route_locations(self, coordinates, reference_date, search_radius, in_sr, out_sr=None, lrs_year=None, route_filter=None):
        param_dict = { 
                      "f": "json",
                      "coordinates": json.dumps(coordinates), 
                      "referenceDate": reference_date,
                      "searchRadius": search_radius,
                      "inSR": in_sr
                      }
        if out_sr is not None:
            param_dict["outSR"] = out_sr
        if lrs_year is not None:
            param_dict["lrsYear"] = lrs_year
        if route_filter is not None:
            param_dict["routeFilter"] = route_filter
        url = self.url + _FIND_NEAREST_ROUTE_LOCATIONS + "?" + urllib.urlencode(param_dict.items())
        f = urllib2.urlopen(url)
        #Cast results to RouteLocation objects.
        return json.load(f, object_hook=dictToRouteLocation)

    routes = property(get_routes, doc="Gets a list of valid routes.")

if __name__ == "__main__":
    elc = Elc()
    print elc.routes
    loc = RouteLocation(arm=5, route="005")
    #print json.dumps([loc], True, cls=RouteLocationEncoder)
    print elc.find_route_locations([loc], "12/31/2013", 4326)
    print elc.find_nearest_route_locations([-122.66401420868051, 45.687177315129304], "12/31/2013", 200, 4326)
