import urllib2, json, re, urllib

_BASEURL = "http://www.wsdot.wa.gov/geoservices/arcgis/rest/services/Shared/ElcRestSOE/MapServer/exts/ElcRestSoe/"
_ROUTES = "routes"
_FIND_ROUTE_LOCATIONS = urllib.quote("Find Route Locations")
_FIND_NEAREST_ROUTE_LOCATIONS = urllib.quote("Find Nearest Route Locations")

class RouteLocation(object):
    """Represents a route location object used as input and output from the ELC.
    """
    def __init__(self, Id=None,
                 Route=None,
                 Decrease=None,
                 Arm=None,
                 Srmp=None,
                 Back=None,
                 ReferenceDate=None,
                 ResponseDate=None,
                 RealignmentDate=None,
                 EndArm=None,
                 EndSrmp=None,
                 EndBack=None,
                 EndReferenceDate=None,
                 EndResponseDate=None,
                 EndRealignDate=None,
                 ArmCalcReturnCode=None,
                 ArmCalcEndReturnCode=None,
                 ArmCalcReturnMessage=None,
                 ArmCalcEndReturnMessage=None,
                 LocatingError=None,
                 RouteGeometry=None,
                 EventPoint=None,
                 Distance=None,
                 Angle=None):
        """Creates a new instance of RouteLocation.

        Parameters:
        - `Id`: Value for the Id property.
        - `Route`: Value for the Route property.
        - `Decrease`: Value for the Decrease property.
        - `Arm`: Value for the Arm property.
        - `Srmp`: Value for the Srmp property.
        - `Back`: Value for the Back property.
        - `ReferenceDate`: Value for the ReferenceDate property.
        - `ResponseDate`: Value for the ResponseDate property.
        - `RealignmentDate`: Value for the RealignmentDate property.
        - `EndArm`: Value for the EndArm property.
        - `EndSrmp`: Value for the EndSrmp property.
        - `EndBack`: Value for the EndBack property.
        - `EndReferenceDate`: Value for the EndReferenceDate property.
        - `EndResponseDate`: Value for the EndResponseDate property.
        - `EndRealignDate`: Value for the EndRealignDate property.
        - `ArmCalcReturnCode`: Value for the ArmCalcReturnCode property.
        - `ArmCalcEndReturnCode`: Value for the ArmCalcEndReturnCode property.
        - `ArmCalcReturnMessage`: Value for the ArmCalcReturnMessage property.
        - `ArmCalcEndReturnMessage`: Value for the ArmCalcEndReturnMessage property.
        - `LocatingError`: Value for the LocatingError property.
        - `RouteGeometry`: Value for the RouteGeometry property.
        - `EventPoint`: Value for the EventPoint property.
        - `Distance`: Value for the Distance property.
        - `Angle`: Value for the Angle property.

        """

        #####

        self.Id = Id
        self.Route = Route
        self.Decrease = Decrease

        self.Arm = Arm
        self.Srmp = Srmp
        self.Back = Back
        self.ReferenceDate = ReferenceDate
        self.ResponseDate = ResponseDate
        self.RealignmentDate = RealignmentDate

        self.EndArm = EndArm
        self.EndSrmp = EndSrmp
        self.EndBack = EndBack
        self.EndReferenceDate = EndReferenceDate
        self.EndResponseDate = EndResponseDate
        self.EndRealignDate = EndRealignDate

        self.ArmCalcReturnCode = ArmCalcReturnCode
        self.ArmCalcEndReturnCode = ArmCalcEndReturnCode
        self.ArmCalcReturnMessage = ArmCalcReturnMessage
        self.ArmCalcEndReturnMessage = ArmCalcEndReturnMessage

        self.LocatingError = LocatingError
        self.RouteGeometry = RouteGeometry
        self.EventPoint = EventPoint
        self.Distance = Distance
        self.Angle = Angle
        return super(RouteLocation, self).__init__()

class RouteLocationEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, RouteLocation):
            d = obj.__dict__
            output = {}
            for key in d:
                if d[key] is not None:
                    output[key] = d[key]
            return output
        else:
            return super(RouteLocationEncoder, self).default(obj)


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

    def findroutelocations(self, locations, referenceDate=None, outSR=None, lrsYear=None):
        """Finds the route locations.

        Parameters:

        - `locations`: A collection of RouteLocation objects
        - `referenceDate`: The date that the `locations` were collected. If all of the `locations` objects have a `referenceDate` specified then this parameter is optional.
        - `outSR`: Optional. The output spatial reference system WKID. If omitted the results will be in the LRS's spatial reference system (2927 as of this writing).
        - `lrsYear`: Optional. If you want a year other than the most current one, provide its name here. See `self.routes` for a list of routes.
        """
        url = self.url + _FIND_ROUTE_LOCATIONS
        # Convert the locations into JSON strings.
        locations_json = json.dumps(locations, cls=RouteLocationEncoder)
        paramsDict = { 
                      "f": "json", 
                      "locations": locations_json 
                    }
        if referenceDate is not None:
            paramsDict["referenceDate"] = str(referenceDate)
        if outSR is not None:
            paramsDict["outSR"] = str(outSR)
        if lrsYear is not None:
            paramsDict["lrsYear"] = lrsYear
        # Convert the parameters into a query string.
        qs = urllib.urlencode(paramsDict.items())
        url += "?" + qs
        f = urllib2.urlopen(url)
        # TODO: Cast results to RouteLocation objects.
        return json.load(f)

    def findnearestroutelocations(self, coordinates, referenceDate, searchRadius, inSR, outSR=None, lrsYear=None, routeFilter=None):
        param_dict = { 
                      "f": "json",
                      "coordinates": json.dumps(coordinates), 
                      "referenceDate": referenceDate,
                      "searchRadius": searchRadius,
                      "inSR": inSR
                      }
        if outSR is not None:
            param_dict["outSR"] = outSR
        if lrsYear is not None:
            param_dict["lrsYear"] = lrsYear
        if routeFilter is not None:
            param_dict["routeFilter"] = routeFilter
        url = self.url + _FIND_NEAREST_ROUTE_LOCATIONS + "?" + urllib.urlencode(param_dict.items())
        f = urllib2.urlopen(url)
        #TODO: Cast results to RouteLocation objects.
        return json.load(f)

    routes = property(get_routes, doc="Gets a list of valid routes.")

if __name__ == "__main__":
    elc = Elc()
    #print elc.routes
    loc = RouteLocation(Arm=5, Route="005")
    #print json.dumps([loc], True, cls=RouteLocationEncoder)
    print elc.findroutelocations([loc], "12/31/2013", 4326)
    print elc.findnearestroutelocations([-122.66401420868051, 45.687177315129304], "12/31/2013", 200, 4326)
