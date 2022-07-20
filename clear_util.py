# Abstraction layer on top of os, os.path, and shutil to manage deleting worlds in game directories.

import os, re, shutil
from typing import Callable, List


_rspeedrun_match = re.compile(r"^RandomSpeedrun #\d+$").match
_sspeedrun_match = re.compile(r"^SetSpeedrun #\d+$").match
_nworld_match = re.compile(r"^New World( \(\d+\))?$").match

_world_match_list = [_rspeedrun_match, _sspeedrun_match, _nworld_match]


def _matches_one(match_list: List[Callable], string: str) -> bool:
    for match in match_list:
        if match(string):
            return True
    return False


def _get_all_matches(match_list: List[Callable], names: List[str]) -> List[str]:
    good_names = []
    for name in names:
        if _matches_one(match_list, name):
            good_names.append(name)
    return good_names


def delete_all_in_minecraft(minecraft_path: str, except_for=0) -> int:
    count = 0
    saves_path = os.path.join(minecraft_path, "saves")
    if os.path.isdir(saves_path):
        world_paths = [os.path.join(saves_path, world_name) for world_name in _get_all_matches(
            _world_match_list, os.listdir(saves_path))]
        world_paths.sort(key=lambda x: os.path.getmtime(x))
        while except_for > 0 and len(world_paths) > 0:
            world_paths.pop()
            except_for -= 1
        for world_path in world_paths:
            count += 1
            try:
                shutil.rmtree(world_path)
            except:
                pass
    return count


if __name__ == "__main__":
    import os
    os.system("python EasyMulti.pyw")
