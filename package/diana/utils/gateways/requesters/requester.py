import os, logging, json as _json
import requests
import attr
from ..exceptions import GatewayConnectionError
from ...smart_json import SmartJSONEncoder


@attr.s
class Requester(object):

    name = attr.ib(default="Requester")

    protocol = attr.ib(default="http")
    host = attr.ib(default="localhost")
    port = attr.ib(default=80)
    path = attr.ib(default=None)

    user = attr.ib(default="diana")
    password = attr.ib(default="passw0rd!")

    base_url = attr.ib(init=False, repr=False)
    auth = attr.ib(init=False, default=None)

    # Can't use attr.s defaults here b/c the derived classes don't see the vars yet
    def __attrs_post_init__(self):
        base_url = "{protocol}://{host}:{port}/".format(
            protocol = self.protocol,
            host = self.host,
            port = self.port )
        if self.path:
            base_url = os.path.join( base_url, self.path )
        self.base_url = base_url
        if self.user:
            self.auth = (self.user, self.password)

    def make_url(self, resource):
        return "{}/{}".format( self.base_url, resource )

    def handle_result(self, result):
        if result.status_code > 299 or result.status_code < 200:
            result.raise_for_status()

        # logging.debug(result.headers)

        if 'application/json' in result.headers.get('Content-type'):
            if result.json():
                return result.json()
        return result.content

    def _get(self, resource, params=None, headers=None):
        logger = logging.getLogger(self.name)
        logger.debug("Calling get")
        url = self.make_url(resource)
        try:
            result = requests.get(url, params=params, headers=headers, auth=self.auth)
            return self.handle_result(result)

        except (requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError) as e:
            raise GatewayConnectionError(e)

    def _put(self, resource, json=None, data=None, headers=None):
        logger = logging.getLogger(self.name)
        logger.debug("Calling put")
        url = self.make_url(resource)
        if json:
            data = _json.dumps(json, cls=SmartJSONEncoder)
        try:
            result = requests.put(url, data=data, headers=headers, auth=self.auth)
        except requests.exceptions.ConnectionError as e:
            raise GatewayConnectionError(e)
        return self.handle_result(result)

    def _post(self, resource, json=None, data=None, headers=None):
        logger = logging.getLogger(self.name)
        logger.debug("Calling post")
        url = self.make_url(resource)
        if json:
            data = _json.dumps(json, cls=SmartJSONEncoder)
        try:
            result = requests.post(url, data=data, headers=headers, auth=self.auth)
        except requests.exceptions.ConnectionError as e:
            raise GatewayConnectionError(e)
        return self.handle_result(result)

    def _delete(self, resource, headers=None):
        logger = logging.getLogger(self.name)
        logger.debug("Calling delete")
        url = self.make_url(resource)
        try:
            result = requests.get(url, headers=headers, auth=self.auth)
        except requests.exceptions.ConnectionError as e:
            raise GatewayConnectionError(e)
        return self.handle_result(result)