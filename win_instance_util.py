# Abstraction layer on top of os, os.path, and shutil to manage deleting worlds in multimc instances.

import os
import re
import shutil
from typing import Union
import tkinter.filedialog as tkFileDialog


NEW_WORLD_RE = "^New World( \\(\\d+\\))?$"
RSPEEDRUN_RE = "RandomSpeedrun #\\d+$"
SSPEEDRUN_RE = "SetSpeedrun #\\d+$"
SPEEDRUN_RE = "Speedrun #\\d+$"


def ask_for_directory(og_path: str = None):
    return tkFileDialog.askdirectory(initialdir=og_path)


def _matches_one(match_list: list, string: str):
    for match in match_list:
        if match(string):
            return True
    return False


def _get_all_matches(match_list: list, names: list):
    good_names = []
    for name in names:
        if _matches_one(match_list, name):
            good_names.append(name)
    return good_names


def delete_all_in_instance(instance_path: str, regex_list: list, except_for=0) -> int:
    count = 0
    saves_path = os.path.join(instance_path, ".minecraft", "saves")
    if os.path.isdir(saves_path):
        world_paths = [os.path.join(saves_path, world_name) for world_name in _get_all_matches(
            [re.compile(regex).match for regex in regex_list], os.listdir(saves_path))]
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


def delete_all_worlds(instances_path: str, regex_list: list, except_for=0) -> int:
    count = 0
    for instance_path in get_all_instance_paths(instances_path):
        count += delete_all_in_instance(instance_path, regex_list, except_for)
    return count


def ensure_instances_path(selected_path: str) -> Union[None, str]:
    if(is_instances_dir(selected_path)):
        return selected_path.replace("\\", "/")

    sub_path = os.path.join(selected_path, "instances")
    if(is_instances_dir(sub_path)):
        return sub_path.replace("\\", "/")

    parent_path = os.path.abspath(os.path.join(selected_path, os.pardir))
    if(is_instances_dir(parent_path)):
        return parent_path.replace("\\", "/")

    double_parent_path = os.path.abspath(os.path.join(parent_path, os.pardir))
    if(is_instances_dir(double_parent_path)):
        return double_parent_path.replace("\\", "/")

    triple_parent_path = os.path.abspath(
        os.path.join(double_parent_path, os.pardir))
    if(is_instances_dir(triple_parent_path)):
        return triple_parent_path.replace("\\", "/")

    return None


def is_instances_dir(path: str):
    return count_instances(path) > 0


def count_instances(instances_path: str) -> int:
    return len(get_all_instance_paths(instances_path))


def get_all_instance_paths(instances_path: str) -> list:
    try:
        instance_paths = []
        for instance_name in os.listdir(instances_path):
            instance_path = os.path.join(instances_path, instance_name)
            if os.path.exists(os.path.join(instance_path, "instance.cfg")):
                instance_paths.append(instance_path.replace("\\", "/"))
        return instance_paths
    except:
        return []


if __name__ == "__main__":
    import os
    os.system("python EasyMulti.pyw")
