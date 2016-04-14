err-locker
----------

This is a plugin for [errbot](http://errbot.io/) which helps you
keep track of whom is using what.

It lets you lock something, for example "production" with `!lock production`.
If anyone else tries to lock it while you have it locked, their request will
be denied.

Once you're done, you can unlock your resource again with `!unlock production`
at which point other people can lock it.

A lock can be force-unlocked by someone else using `!unlock` as well, but a
message will be sent to the person who originally locked it letting them know
their resource was unlocked by force.


Installation
------------

Install this plugin using `!repos install https://github.com/zoni/err-locker.git`
