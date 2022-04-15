# Abstraction layer on top of xdotool

import subprocess, keyboard

# NOTE(wurgo): No, I did not misspell win, WID stands for Window Identifier OMEGA


def run_cmd(cmd: str):
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    response = output.communicate()
    try:
        return response[0].decode()[:-1]
    except Exception:
        return response[0].decode()


def get_pid(wid: str):
    response = run_cmd("xdotool getwindowpid {}".format(wid))
    try:
        int(response)
        return response
    except:
        return None


def get_current_wid():
    return run_cmd("xdotool getactivewindow")


def get_win_title(wid: str):
    return run_cmd("xdotool getwindowname {}".format(wid))


def get_all_mc_wids():
    try:
        response = run_cmd("xdotool search --class minecraft").split("\n")
        return [] if response == [""] else response
    except Exception:
        return []


def set_win_title(wid: str, title: str):
    return run_cmd("xdotool set_window --name '{}' {}".format(title, wid))


def activate_win(wid: str):
    keyboard.press_and_release("shift+5")
    return run_cmd("xdotool windowactivate --sync " + wid)


def suspend_win(wid: str):
    pid = get_pid(wid)
    return run_cmd("kill -SIGSTOP " + pid)


def resume_win(wid: str):
    pid = get_pid(wid)
    return run_cmd("kill -SIGCONT " + pid)


def win_exists(wid: str):
    return get_pid(wid) is not None
