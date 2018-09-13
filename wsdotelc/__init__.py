"""elcpy
This module is designed for accessing the WSDOT ELC REST SOE at https://data.wsdot.wa.gov/arcgis/rest/services/Shared/ElcRestSOE/MapServer/exts/ElcRestSoe/
"""
from __future__ import print_function, absolute_import, division, unicode_literals
import datetime
import json
from dataclasses import dataclass
import requests
from requests.utils import quote

_BASEURL = "https://data.wsdot.wa.gov/arcgis/rest/services/Shared/ElcRestSOE/MapServer/exts/ElcRestSoe/"
_ROUTES = "routes"
_FIND_ROUTE_LOCATIONS = quote("Find Route Locations")
_FIND_NEAREST_ROUTE_LOCATIONS = quote("Find Nearest Route Locations")


class ElcError(Exception):
    def __init__(self, error_message):
        self.message = error_message
        super(ElcError, self).__init__()


@dataclass
class RouteLocation(object):
    """Represents a route location object used as input and output from the ELC.
    """

    Id: int = None
    Route: str = None
    Decrease: bool = None
    Arm: float = None
    Srmp: float = None
    Back: bool = None
    ReferenceDate: datetime.date = None
    ResponseDate: datetime.date = None
    EndArm: float = None
    EndSrmp: float = None
    EndBack: bool = None
    EndReferenceDate: datetime.date = None
    EndResponseDate: datetime.date = None
    RealignmentDate: datetime.date = None
    EndRealignmentDate: datetime.date = None
    ArmCalcReturnCode: float = None
    ArmCalcEndReturnCode: float = None
    ArmCalcReturnMessage: str = None
    ArmCalcEndReturnMessage: str = None
    LocatingError: str = None
    RouteGeometry: dict = None
    EventPoint: dict = None
    Distance: float = None
    Angle: float = None


def dict_contains_any_of_these_keys(d, *args):
    for a in args:
        if a in d:
            return True
    return False


class RouteLocationEncoder(json.JSONEncoder):
    """This class is used for converting a `RouteLocation` into JSON.
    """

    def default(self, o):
        """Converts the input object into a `dict`.

        Parameters:

        - `o`: The object that is being converted to JSON.
        """
        if isinstance(o, RouteLocation):
            return o.__dict__

        return super().default(o)

def dict_to_route_location(dct):
    if "error" in dct:
        return ElcError(dct["error"]["message"])
    if "Route" in dct:
        return RouteLocation(**dct)
    return dct

class Elc(object):
    """This object is used to call the ELC REST SOE endpoint.

    Parameters:

    - `url`: The URL for the ELC REST SOE. You only need to override this if you don't want to use the `default value <https://data.wsdot.wa.gov/arcgis/rest/services/Shared/ElcRestSOE/MapServer/exts/ElcRestSoe/>`_.
    """

    def __init__(self, url=_BASEURL):
        self.url = url
        # __routes will be used to store route data after the first request for it.
        self._routes = None
        super().__init__()

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
            response = requests.get(url)  # urllib2.urlopen(url)
            self._routes = response.json()
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
        params_dict = {
            "f": "json",
            "locations": locations_json
        }
        if reference_date is not None:
            params_dict["referenceDate"] = str(reference_date)
        if out_sr is not None:
            params_dict["outSR"] = str(out_sr)
        if lrs_year is not None:
            params_dict["lrsYear"] = lrs_year
        # Convert the parameters into a query string.
        # qs = requests. .urlencode(paramsDict.items())
        # url += "?" + qs
        # f = urllib2.urlopen(url)
        f = requests.get(url, params_dict)
        # Cast results to RouteLocation objects.
        # output = json.load(f, object_hook=dict_to_route_location)
        output = f.json(object_hook=dict_to_route_location)
        if isinstance(output, Exception):
            raise output
        return output

    def find_nearest_route_locations(self, coordinates, reference_date, search_radius, in_sr, out_sr=None, lrs_year=None, route_filter=None):
        """Finds the route locations nearest to the input coordinates.

        Parameters:

        - `coordinates`: E.g.:

            - `[1087403.28714286, 136623.00728571415]`
            - `[[1087403.28714286, 136623.00728571415],[1087403.28714286, 136623.00728571415]]`
        - `reference_date`: The date that the coordinates were collected.
        - `search_radius`: The search radius in inches.
        - `in_sr`: The coordinate system WKID of the input `coordinates`.
        - `out_sr`: The cooordinate system to use for the output. Defaults to the LRS's coordinates system if omitted.
        - `lrs_year`: The LRS year. See `self.routes` for a list of valid LRS years.
        - `route_filter`: A partial SQL query that can be used to limit which routes are searched.  E.g., "LIKE '005%'" or "'005'".
        """
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
        # url = self.url + _FIND_NEAREST_ROUTE_LOCATIONS + "?" + urllib.urlencode(param_dict.items())
        # f = urllib2.urlopen(url)
        url = self.url + _FIND_NEAREST_ROUTE_LOCATIONS
        f = requests.get(url, param_dict)

        # Cast results to RouteLocation objects.
        output = f.json(object_hook=dict_to_route_location)
        if isinstance(output, Exception):
            raise output
        return output

    routes = property(get_routes, doc="Gets a list of valid routes.")
