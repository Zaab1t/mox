MoxWiki
=======

MoxWiki is a MOX agent with the purpose of migrating documents from the
LoRA system to an external MediaWiki service running the SeMaWi plugin.
The documents will be read from the OIO Rest interface, converted to a
format that SeMaWi understands, and sent to the MediaWiki service.

Operation details
-----------------

On service startup, MoxWiki queries the OIO Rest interface for items
with registrations since the last run, or all items in case the MoxWiki
service has never run before. These items are returned as a list of
UUIDs. These objects are then iterated over, performing an update for
each item.

When the update method is run, the relevant item is fetched from the
Rest interface and put in a local cache (or fetched from cache if it is
present there). A text string is created from the relevant template
(based on object type), specifying the format expected by SeMaWi. This
includes references to other items, which are therefore also fetched and
cached.

The MediaWiki page corresponding to the item is then fetched and
compared to the generated text string, and in case of a mismatch, the
generated text string is uploaded to the MediaWiki service as a
replacement. If the page does not already exist in MediaWiki, the page
is created with the generated text string.

When an item update notification is received from the AMQP server,
specifying that an item has been updated in the OIO database, the update
method is run on the item, fetching and updating the cache (disregarding
any existing cache item), and updating the MediaWiki page. In case the
notification specifies that the item is deleted, however, the
correcponding MediaWiki page is also deleted.

When an effect update notification is received, specifying that an item
changes effective value due to effect period beginning or ending, the
update method is again run as above.

Configuration
-------------

The MoxWiki agent reads the following configuration values:

:moxwiki.wiki.host:
    Address of the MediaWiki server, e.g. https://en.wikipedia.org
:moxwiki.wiki.username:
    Username for the MediaWiki server, to access the MediaWiki API
:moxwiki.wiki.password: Password for the MediaWiki server
:moxwiki.amqp.host:
    AMQP server to listen for messages on, e.g. moxdev.magenta-aps.dk
:moxwiki.amqp.username: Username for the AMQP server
:moxwiki.amqp.password: Password for the AMQP server
:moxwiki.amqp.exchange:
    AMQP exchange name to bind to. A queue will be set up
    and bound to this exchange
:moxwiki.rest.host: OIO Rest host, e.g. https://moxdev.magenta-aps.dk
:moxwiki.rest.username: Username for the OIO Rest server
:moxwiki.rest.password: Password for the OIO Rest server
