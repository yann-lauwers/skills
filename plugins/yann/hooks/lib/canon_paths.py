import os
import pwd


def home():
    return os.path.realpath(os.path.expanduser("~"))


def claude_dir():
    return os.path.join(home(), ".claude")


def skills_dir(hook_tree):
    beside = os.path.join(os.path.dirname(os.path.abspath(hook_tree)), "skills")
    if os.path.isdir(beside):
        return beside
    return os.path.join(pwd.getpwuid(os.getuid()).pw_dir, ".claude", "skills")
