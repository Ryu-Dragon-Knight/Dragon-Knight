from ryu.controller import event

class EventAppListRequst(event.EventRequestBase):

    def __init__(self):
        super(EventAppListRequst, self).__init__()
        self.dst = 'DynamicLoader'

class EventAppListReply(event.EventReplyBase):
    def __init__(self, dst, app_list):
        super(EventAppListReply, self).__init__(dst)
        self.app_list = app_list

class EventAppInstall(event.EventBase):

    def __init__(self, app_id):
        super(EventAppInstall, self).__init__()
        self.app_id = app_id

class EventAppUninstall(event.EventBase):

    def __init__(self, app_id):
        super(EventAppUninstall, self).__init__()
        self.app_id = app_id

