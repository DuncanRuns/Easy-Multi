import platform

system_type = platform.system()

if system_type == "":
    print("System type cannot be determined!")
    raise
elif system_type == "Windows":
    print("Running Easy Multi on Windows")
    from win_window import *
    from win_key_util import *
    from win_constants import *
elif system_type == "Linux":
    print("Running Easy Multi on Linux")
    from lin_window import *
    from lin_key_util import *
    from lin_constants import *
else:
    print("Unsupported system type!")
    raise


class EasyMulti:
    pass
