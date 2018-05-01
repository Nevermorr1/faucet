"""RyuApp base class for FAUCET/Gauge."""

# Copyright (C) 2013 Nippon Telegraph and Telephone Corporation.
# Copyright (C) 2015 Brad Cowie, Christopher Lorier and Joe Stringer.
# Copyright (C) 2015 Research and Education Advanced Network New Zealand Ltd.
# Copyright (C) 2015--2017 The Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import random
import signal
import sys

from ryu.base import app_manager
from ryu.controller import dpset, event
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub

from faucet import valve_of
from faucet.valve_util import dpid_log, get_logger, get_setting


class EventReconfigure(event.EventBase):
    """Event sent to controller to cause config reload."""

    pass


class RyuAppBase(app_manager.RyuApp):
    """RyuApp base class for FAUCET/Gauge."""

    OFP_VERSIONS = valve_of.OFP_VERSIONS
    _CONTEXTS = {
        'dpset': dpset.DPSet,
    }
    logname = ''
    exc_logname = ''

    def __init__(self, *args, **kwargs):
        super(RyuAppBase, self).__init__(*args, **kwargs)
        self.dpset = kwargs['dpset']
        self._reg = kwargs.get('reg', None)
        self.config_file = self.get_setting('CONFIG', True)
        self.stat_reload = self.get_setting('CONFIG_STAT_RELOAD')
        loglevel = self.get_setting('LOG_LEVEL')
        logfile = self.get_setting('LOG')
        exc_logfile = self.get_setting('EXCEPTION_LOG')
        self.logger = get_logger(
            self.logname, logfile, loglevel, 0)
        self.exc_logger = get_logger(
            self.exc_logname, exc_logfile, logging.DEBUG, 1)

    @staticmethod
    def _thread_jitter(period, jitter=2):
        """Reschedule another thread with a random jitter."""
        hub.sleep(period + random.randint(0, jitter))

    def _thread_reschedule(self, ryu_event, period, jitter=2):
        """Trigger Ryu events periodically with a jitter.

        Args:
            ryu_event (ryu.controller.event.EventReplyBase): event to trigger.
            period (int): how often to trigger.
        """
        while True:
            self.send_event(self.__class__.__name__, ryu_event)
            self._thread_jitter(period, jitter)

    def get_setting(self, setting, path_eval=False):
        """Return config setting prefaced with logname."""
        return get_setting('_'.join((self.logname.upper(), setting)), path_eval)

    def signal_handler(self, sigid, _):
        """Handle signals.

        Args:
            sigid (int): signal received.
        """
        if sigid == signal.SIGINT:
            self.close()
            sys.exit(0)
        if sigid == signal.SIGHUP:
            self.send_event(self.__class__.__name__, EventReconfigure())

    def _config_files_changed(self):
        """Return True if config files changed."""
        return False

    def _config_file_stat(self):
        """Periodically stat config files for any changes."""
        while True:
            if self._config_files_changed():
                if self.stat_reload:
                    self.send_event(self.__class__.__name__, EventReconfigure())
            self._thread_jitter(3)

    def start(self):
        """Start controller."""
        super(RyuAppBase, self).start()
        if self.stat_reload:
            self.logger.info('will automatically reload new config on changes')
        self.reload_config(None)
        signal.signal(signal.SIGHUP, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)

    def reload_config(self, _ryu_event):
        self.logger.info('Reloading configuration')

    def _get_datapath_obj(self, handler_name, datapath_objs, ryu_event):
        """Get datapath object to response to an event.

        Args:
            handler_name (string): handler name to log if datapath unknown.
            datapath_objs (dict): datapath objects indexed by DP ID.
            ryu_event (ryu.controller.event.Event): event.
        Returns:
            valve, ryu_dp, msg: tuple of Nones, or datapath object, Ryu datapath, and Ryu msg (if any)
        """
        datapath_obj = None
        msg = None
        if hasattr(ryu_event, 'msg'):
            msg = ryu_event.msg
            ryu_dp = msg.datapath
        else:
            ryu_dp = ryu_event.dp
        dp_id = ryu_dp.id
        if dp_id in datapath_objs:
            datapath_obj = datapath_objs[dp_id]
        else:
            ryu_dp.close()
            self.logger.error('%s: unknown datapath %s', handler_name, dpid_log(dp_id))
        return (datapath_obj, ryu_dp, msg)

    def _datapath_connect(self, ryu_event):
        return

    def _datapath_disconnect(self, ryu_event):
        return

    @set_ev_cls(dpset.EventDP, dpset.DPSET_EV_DISPATCHER)
    def connect_or_disconnect_handler(self, ryu_event):
        """Handle connection or disconnection of a datapath.

        Args:
            ryu_event (ryu.controller.dpset.EventDP): trigger.
        """
        if ryu_event.enter:
            self._datapath_connect(ryu_event)
        else:
            self._datapath_disconnect(ryu_event)

    @set_ev_cls(dpset.EventDPReconnected, dpset.DPSET_EV_DISPATCHER)
    def reconnect_handler(self, ryu_event):
        """Handle reconnection of a datapath.

        Args:
            ryu_event (ryu.controller.dpset.EventDPReconnected): trigger.
        """
        self._datapath_connect(ryu_event)
