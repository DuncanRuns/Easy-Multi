import lin_util

class Window:
    def __init__(self, wid):
        self._wid = wid
        self._original_title = lin_util.get_win_title(self._wid)

    def get_original_title(self):
        return self._original_title
    
    def revert_title(self):
        self.set_title(self._original_title)
    
    def set_title(self, title: str):
        lin_util.set_win_title(self._wid, title)
    
    def get_title(self):
        return lin_util.get_win_title(self._wid)
    
    def activate(self):
        self.resume()
        lin_util.activate_win(self._wid)
    
    def suspend(self):
        lin_util.suspend_win(self._wid)
    
    def resume(self):
        lin_util.resume_win(self._wid)
    
    def get_wid(self):
        return self._wid
    
    def __eq__(self, __o: object):
        return self._wid == __o.get_wid()

def get_all_mc_windows():
    wids = lin_util.get_all_mc_wids()
    windows = []
    for wid in wids:
        windows.append(Window(wid))
    return windows

def get_current_window():
    return Window(lin_util.get_current_wid())
