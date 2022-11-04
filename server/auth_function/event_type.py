from typing import List, Dict, TypedDict, Any, Union


class CallerContext(TypedDict):
    awsSdkVersion: str
    clientId: str


class Region(TypedDict):
    region: str


class Request(TypedDict):
    groupConfiguration: Dict[str, List[str]]
    iamRolesToOverride: List[Any]


class Response(TypedDict):
    claimsOverrideDetails: Any


class Event(TypedDict):
    callerContext: CallerContext
    region: str
    request: Request
    userAttributes: Dict[str, Union[str, List[Any]]]
    response: Response
    triggerSource: str
    userName: str
    userPoolId: str
    version: str
