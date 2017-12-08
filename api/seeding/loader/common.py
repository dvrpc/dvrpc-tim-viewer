class Sponge:
    def __init__(self, **kwds):
        for k, v in kwds.iteritems():
            setattr(self, k, v)
    def __contains__(self, key):
        return hasattr(self, key)