# -*- coding: utf-8 -*-
import abc
import os


class Notifier(object):
    """Base notification class to check if git repo has uncommited changes"""

    __metaclass__ = abc.ABCMeta

    def __init__(self, interval, path):
        self.interval = interval
        self.dirs = list(self.get_dirs(*path.split(',')))

    @staticmethod
    def get_dirs(*dirs):
        for repo in dirs:
            if not os.path.isdir(repo):
                print("Directory doesn't exist, skipping: %s" % repo)
            else:
                yield repo

    @abc.abstractmethod
    def start(self):
        """Start monitoring the changes & aply notification actions"""
        pass

    @abc.abstractmethod
    def notify(self):
        """Send notification with modified directory."""
        pass
