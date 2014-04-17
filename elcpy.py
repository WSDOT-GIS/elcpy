"""elcpy
This module is designed for accessing the WSDOT ELC REST SOE at http://www.wsdot.wa.gov/geoservices/arcgis/rest/services/Shared/ElcRestSOE/MapServer/exts/ElcRestSoe/
"""
import urllib2, json, re, urllib

_BASEURL = "http://www.wsdot.wa.gov/geoservices/arcgis/rest/services/Shared/ElcRestSOE/MapServer/exts/ElcRestSoe/"
_ROUTES = "routes"
_FIND_ROUTE_LOCATIONS = urllib.quote("Find Route Locations")
_FIND_NEAREST_ROUTE_LOCATIONS = urllib.quote("Find Nearest Route Locations")

def _flip_dict_keys_and_values(d):
    """Switches the keys and values of a dictionary. The input dicitonary is not modified.

    Output:
        dict
    """
    output = {}
    for key, value in d.items():
        output[value] = key
    return output

_PROP_NAME_TO_JSON_NAME_DICT = {
    "id_": "Id",
    "route": "Route",
    "decrease": "Decrease",

    "arm": "Arm",
    "srmp": "Srmp",
    "back": "Back",
    "reference_date": "ReferenceDate",
    "response_date": "ResponseDate",
    "realignment_date": "RealignmentDate",

    "end_arm": "EndArm",
    "end_srmp": "EndSrmp",
    "end_back": "EndBack",
    "end_reference_date": "EndReferenceDate",
    "end_response_date": "EndResponseDate",
    "end_realign_date": "EndRealignDate",

    "armcalc_return_code": "ArmCalcReturnCode",
    "armcalc_end_return_code": "ArmCalcEndReturnCode",
    "armcalc_return_message": "ArmCalcReturnMessage",
    "armcalc_end_return_message": "ArmCalcEndReturnMessage",

    "locating_error": "LocatingError",
    "route_geometry": "RouteGeometry",
    "event_point": "EventPoint",
    "distance": "Distance",
    "angle": "Angle"
}

_JSON_NAME_TO_PROP_NAME_DICT = _flip_dict_keys_and_values(_PROP_NAME_TO_JSON_NAME_DICT)

class ElcError(Exception):
    def __init__(self, error_message):
        self.message = error_message
        return super(ElcError, self).__init__()

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

        self.id_ = id_
        self.route = route
        self.decrease = decrease

        self.arm = arm
        self.srmp = srmp
        self.back = back
        self.reference_date = reference_date
        self.response_date = response_date
        self.realignment_date = realignment_date

        self.end_arm = end_arm
        self.end_srmp = end_srmp
        self.end_back = end_back
        self.end_reference_date = end_reference_date
        self.end_response_date = end_response_date
        self.end_realign_date = end_realign_date

        self.armcalc_return_code = armcalc_return_code
        self.armcalc_end_return_code = armcalc_end_return_code
        self.armcalc_return_message = armcalc_return_message
        self.armcalc_end_return_message = armcalc_end_return_message

        self.locating_error = locating_error
        self.route_geometry = route_geometry
        self.event_point = event_point
        self.distance = distance
        self.angle = angle
        return super(RouteLocation, self).__init__()

    def __str__(self):
        return json.dumps(self, cls=RouteLocationEncoder) #self.__dict__.__str__()

    def __repr__(self):
        d = self.__dict__
        output = "RouteLocation("
        for key in d:
            value = d[key]
            if value is not None:
                output += key + "=" + value.__repr__() + ","
        output = output.rstrip(",")
        output += ")"
        return output #super(RouteLocation, self).__repr__()

def dict_contains_any_of_these_keys(d, *args):
    for a in args:
        if d.has_key(a):
            return True
    return False

def dict_to_route_location(d):
    """Converts a dicitonary of route location data into a RouteLocation.
    Indented for use with JSON deserialization.

    Parameters:

    - `d`: A dictionary.
    """
    if d.has_key("error"):
        return ElcError(*d)
    if dict_contains_any_of_these_keys(d, *_JSON_NAME_TO_PROP_NAME_DICT.keys()):
        loc = RouteLocation()

        loc.id_ = d.get("Id", None)
        loc.route = d.get("Route", None)
        loc.decrease = d.get("Decrease", None)

        loc.arm = d.get("Arm", None)
        loc.srmp = d.get("Srmp", None)
        loc.back = d.get("Back", None)
        loc.reference_date = d.get("ReferenceDate", None)
        loc.response_date = d.get("ResponseDate", None)
        loc.realignment_date = d.get("RealignmentDate", None)

        loc.end_arm = d.get("EndArm", None)
        loc.end_srmp = d.get("EndSrmp", None)
        loc.end_back = d.get("EndBack", None)
        loc.end_reference_date = d.get("EndReferenceDate", None)
        loc.end_response_date = d.get("EndResponseDate", None)
        loc.end_realign_date = d.get("EndRealignDate", None)

        loc.armcalc_return_code = d.get("ArmCalcReturnCode", None)
        loc.armcalc_end_return_code = d.get("ArmCalcEndReturnCode", None)
        loc.armcalc_return_message = d.get("ArmCalcReturnMessage", None)
        loc.armcalc_end_return_message = d.get("ArmCalcEndReturnMessage", None)

        loc.locating_error = d.get("LocatingError", None)
        loc.route_geometry = d.get("RouteGeometry", None)
        loc.event_point = d.get("EventPoint", None)
        loc.distance = d.get("Distance", None)
        loc.angle = d.get("Angle", None)

        return loc
    else:
        return d

class RouteLocationEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, RouteLocation):
            return super(RouteLocationEncoder, self).default(obj)

        d = obj.__dict__
        output = {}
        for key in d:
            if d[key] is not None:
                output[_PROP_NAME_TO_JSON_NAME_DICT[key]] = d[key]
        return output

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
        output = json.load(f, object_hook=dict_to_route_location)
        if isinstance(output, Exception):
            raise output
        return output

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
        output = json.load(f, object_hook=dict_to_route_location)
        if isinstance(output, Exception):
            raise output
        return output

    routes = property(get_routes, doc="Gets a list of valid routes.")

if __name__ == "__main__":
    print __doc__
