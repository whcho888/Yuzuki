# -*- coding: utf-8 -*-
import json

import redis
from twisted.web.server import Site, Session

from config import REDIS_CONNECT_ARGS
from helper.request import YuzukiRequest

r = redis.StrictRedis(**REDIS_CONNECT_ARGS)


class YuzukiSession(Session):
    sessionTimeout = 7200  # two hours

    def __init__(self, site, uid, reactor=None):
        Session.__init__(self, site, uid, reactor=None)
        self.yuzuki_session_data = dict()

    def redis_sync(self):
        r.setex(get_redis_id(self.uid), self.sessionTimeout, json.dumps(self.yuzuki_session_data))


class YuzukiSite(Site):
    def __init__(self, resource, *args, **kwargs):
        Site.__init__(self, resource, *args, **kwargs)
        self.requestFactory = YuzukiRequest
        self.sessionFactory = YuzukiSession

    def makeSession(self):
        uid = self._mkuid()
        session = self.sessions[uid] = self.sessionFactory(self, uid)
        r.setex(get_redis_id(uid), YuzukiSession.sessionTimeout, json.dumps(dict()))
        return session

    def getSession(self, uid):
        redis_session = r.get(get_redis_id(uid))
        if redis_session:
            r.expire(get_redis_id(uid), YuzukiSession.sessionTimeout)
            if uid in self.sessions:
                session = self.sessions[uid]
            else:
                session = self.sessions[uid] = self.sessionFactory(self, uid)
            session.yuzuki_session_data = json.loads(redis_session)
            return session
        else:
            raise KeyError(uid)


def get_redis_id(session_uid):
    return "yzks::%s" % session_uid