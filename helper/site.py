# -*- coding: utf-8 -*-
from twisted.web.server import Site, Session

from helper.request import YuzukiRequest


class YuzukiSession(Session):
    sessionTimeout = 7200  # two hours

    def __init__(self, site, uid, reactor=None):
        Session.__init__(self, site, uid, reactor=None)
        self.yuzuki_session_data = dict()

    def redis_sync(self):
        pass


class YuzukiSite(Site):
    def __init__(self, resource, *args, **kwargs):
        Site.__init__(self, resource, *args, **kwargs)
        self.requestFactory = YuzukiRequest
        self.sessionFactory = YuzukiSession
