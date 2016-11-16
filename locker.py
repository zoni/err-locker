import datetime
import threading
from errbot import BotPlugin, arg_botcmd, botcmd, re_botcmd


class Locker(BotPlugin):
    """
    Lock things to let people know you're using them.
    """

    def activate(self):
        super(Locker, self).activate()
        self.threadlock = threading.Lock()
        if 'locks' not in self:
            self['locks'] = {}

    def callback_message(self, message):
        """
        Triggered for every received message that isn't coming from the bot itself

        You should delete it if you're not using it to override any default behaviour
        """
        pass

    @arg_botcmd('what', type=str)
    @arg_botcmd('-m', '--message', type=str, unpack_args=False)
    def lock(self, message, args):
        """
        Lock something.
        """
        return self._lock(args.what, str(message.frm.person), args.message)

    def _lock(self, what, by, message=None):
        with self.threadlock:
            locks = self['locks']
            if message is None:
                message = "No reason specified"

            if what in locks:
                if locks[what]['by'] == by:
                    return "You already locked this"
                else:
                    return "{what} is already locked by {who} and must be unlocked first".format(
                        what=what,
                        who=locks[what]['by']
                    )

            locks[what] = {
                'by': by,
                'at': datetime.datetime.now(),
                'message': message,
            }
            self['locks'] = locks
            return "{} locked".format(what)

    @arg_botcmd('what', type=str)
    @arg_botcmd('-f', '--force', action="store_true", unpack_args=False)
    def unlock(self, message, args):
        return self._unlock(args.what, str(message.frm.person), args.force)

    def _unlock(self, what, by, force=False):
        with self.threadlock:
            locks = self['locks']
            if what not in locks:
                return "{} isn't locked".format(what)

            lock = locks[what]
            if lock['by'] == by:
                del locks[what]
                self['locks'] = locks
                return "{} unlocked".format(what)
            else:
                if not force:
                    return "{what} was locked by {who}, not unlocking without --force".format(
                        what=what,
                        who=lock['by']
                    )
                else:
                    del locks[what]
                    self['locks'] = locks
                    self.send(
                        identifier=self.build_identifier(lock['by']),
                        text="{who} just force unlocked {what}".format(
                            who=by, what=what
                        )
                    )
                    return "{} unlocked".format(what)

    @botcmd
    def locks(self, message, args):
        """
        List all locked objects.
        """
        with self.threadlock:
            if len(self['locks']) == 0:
                yield "Nothing is currently locked"
                return

            for lock, details in self['locks'].items():
                yield "{0} locked by {1[by]} on {1[at]} ({1[message]})".format(
                    lock,
                    details
                )

    @re_botcmd(pattern=r'^lock ([\w]+)( |\.)?$', prefixed=False)
    def re_lock(self, message, match):
        return self._lock(match.group(1), str(message.frm.person))

    @re_botcmd(pattern=r'^unlock ([\w]+)( |\.| --force)?$', prefixed=False)
    def re_unlock(self, message, match):
        force = '--force' in message.body
        return self._unlock(match.group(1), str(message.frm.person), force)
