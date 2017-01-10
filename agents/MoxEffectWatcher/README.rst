MoxEffectWatcher Documentation
==============================

MoxEffectWatcher is a Mox agent with the purpose to record effect transitions
in item values, and emit notification messages when these transitions are
reached.

For example, an item (id=1234) has the property foo=2, effective from
2016-01-01 00:00:00 to 2016-01-05 14:00:00. These transitions are stored by
MoxEffectWatcher, which emits a notification at 2016-01-01 00:00:00, telling
that item 1234 has reached a transition where a value comes into effect, and a
notification at 2016-01-05 14:00:00, telling that item 1234 has reached a
transition where a value comes out of effect. If the property has another value
coming into effect at the same time as the old value going out, the
notification is that the transition is both an end and a beginning.

Operation details
-----------------

When the agent starts, it fetches items that have seen registrations since the
last agent run, finds the effect transition times in the item data, and stores
them in an sqlite database.

When an update notification is received, stating that an item is updated in the
OIO database, the item in question is fetched, parsed, and the transition times
updated in the database.

A thread is run, finding the next transition time, and waits until that time.
A notification message is then emitted for each item that undergoes transition
at this time. Then the process repeats with the next transition time being
found. This thread (whose duty cycle primarily consists of waiting) is stopped
and restarted when an item update occurs (in response to a notification
message).

Configuration
-------------

The MoxEffectWatcher agent reads the following configuration values:

:moxeffectwatcher.amqp.host:
    AMQP server to receive and send messages on, e.g. moxdev.magenta-aps.dk
:moxeffectwatcher.amqp.username: Username for the AMQP server
:moxeffectwatcher.amqp.password: Password for the AMQP server
:moxeffectwatcher.amqp.exchange_in: AMQP exchange name to bind to, for
    receiving messages. A queue will be set up and bound to this exchange.
:moxeffectwatcher.amqp.exchange_out:
    AMQP exchange name to bind to, for sending messages.
    The exchange will created if it does not exist.
:moxeffectwatcher.rest.host: OIO Rest host, e.g. https://moxdev.magenta-aps.dk
:moxeffectwatcher.rest.username: Username for the OIO Rest server
:moxeffectwatcher.rest.password: Password for the OIO Rest server
