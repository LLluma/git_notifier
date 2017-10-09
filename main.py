#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser
from wx_notifier import WxNotifier


config = ConfigParser.ConfigParser()
config.readfp(open('config.cfg'))

REPOSITORY_PATH = config.get('main', 'repository_path')
REPEAT_EVERY = config.getfloat('main', 'repeat_every')

if __name__ == '__main__':
    # TODO get path & interval from the CLI
    notifier = WxNotifier(REPEAT_EVERY, REPOSITORY_PATH)
    notifier.start()