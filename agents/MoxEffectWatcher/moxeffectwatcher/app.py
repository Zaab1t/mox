#!/usr/bin/python
# -*- coding: utf-8 -*-

from agent.amqpclient import MessageListener, MessageSender
from agent.message import NotificationMessage, EffectUpdateMessage
from agent.config import read_properties_files, MissingConfigKeyError
from PyLoRA import Lora
from PyOIO.OIOCommon.exceptions import InvalidOIOException
from PyOIO.organisation import Bruger, Interessefaellesskab, ItSystem, Organisation, OrganisationEnhed, OrganisationFunktion
from PyOIO.klassifikation import Facet, Klasse, Klassifikation
from datetime import datetime
import pytz
import os
import sqlalchemy
from tables import Base, EffectBorder, Synchronization
import threading


DIR = os.path.dirname(os.path.realpath(__file__))

configfile = DIR + "/settings.conf"
config = read_properties_files("/srv/mox/mox.conf", configfile)

class MoxEffectWatcher(object):

    EFFECT_START = EffectUpdateMessage.TYPE_BEGIN
    EFFECT_END = EffectUpdateMessage.TYPE_END
    EFFECT_BOTH = EffectUpdateMessage.TYPE_BOTH

    emitter_thread = None
    session = None
    closing = False
    notify_unsynced = False # When we start up, do we emit messages that should have been sent while we were down?

    def __init__(self):

        try:
            amqp_host = config['moxeffectwatcher.amqp.host']
            amqp_username = config['moxeffectwatcher.amqp.username']
            amqp_password = config['moxeffectwatcher.amqp.password']
            amqp_queue_in = config['moxeffectwatcher.amqp.queue_in']
            amqp_queue_out = config['moxeffectwatcher.amqp.queue_out']

            rest_host = config['moxeffectwatcher.rest.host']
            rest_username = config['moxeffectwatcher.rest.username']
            rest_password = config['moxeffectwatcher.rest.password']

        except KeyError as e:
            raise MissingConfigKeyError(str(e))

        self.accepted_object_types = ['bruger', 'interessefaellesskab', 'itsystem', 'organisation', 'organisationenhed', 'organisationfunktion' ,'klasse', 'klassifikation', 'facet']

        self.notification_listener = MessageListener(amqp_username, amqp_password, amqp_host, amqp_queue_in, queue_parameters={'durable': True})
        self.notification_listener.callback = self.handle_message

        self.notification_sender = MessageSender(amqp_username, amqp_password, amqp_host, amqp_queue_out, queue_parameters={'durable': True})

        self.lora = Lora(rest_host, rest_username, rest_password)

        self.db = sqlalchemy.create_engine('sqlite:///effects.db')

    def start(self):
        try:
            self.db.connect()
            self.sessionclass = sqlalchemy.orm.sessionmaker(bind=self.db)
            self.initial_sync()
            self.emitter = Emitter(self.sessionclass, self.notification_sender)
            self.emitter.start(True)
            if self.notification_listener:
                self.notification_listener.run()
        except:
            self.end_session()
            try:
                self.emitter.stop()
            except:
                pass
            raise


    def begin_session(self):
        if self.session is None:
            self.session = self.sessionclass()

    def end_session(self):
        if self.session is not None:
            self.session.close()
            self.session = None

    def initial_sync(self):
        self.begin_session()
        Base.metadata.create_all(self.db)

        lastsync = self.session.query(Synchronization).filter_by(host=self.lora.host).order_by(sqlalchemy.desc(Synchronization.time)).first()
        if lastsync:
            print "Last synchronization with %s was %s" % (self.lora.host, lastsync.time.strftime('%Y-%m-%d %H:%M:%S'))
            print "Getting latest changes from REST server"
        else:
            print "Has never synchronized before"
            print "Getting all objects from REST server"

        uuids = {}
        newsync = datetime.now(pytz.utc)
        for type in [Bruger, Interessefaellesskab, ItSystem, Organisation, OrganisationEnhed, OrganisationFunktion, Facet, Klasse, Klassifikation]:
            # for type in [Bruger, Interessefaellesskab, ItSystem, Organisation, OrganisationEnhed, OrganisationFunktion]:
            uuids[type.ENTITY_CLASS] = self.lora.get_uuids_of_type(type, lastsync.time if lastsync else None)
        for entity_class, type_uuids in uuids.items():
            for uuid in type_uuids:
                item = self.lora.get_object(uuid, entity_class, force_refresh=True)
                self.update(item)

        self.session.add(Synchronization(host=self.lora.host, time=newsync))
        self.session.commit()
        self.end_session()


    def handle_message(self, channel, method, properties, body):
        message = NotificationMessage.parse(properties.headers, body)
        if message:
            print "Got a NotificationMessage"
            if message.objecttype.lower() in self.accepted_object_types:
                print "Object type '%s' accepted" % message.objecttype
                self.begin_session()
                try:
                    item = self.lora.get_object(message.objectid, message.objecttype, force_refresh=True)
                    if message.lifecyclecode == 'Slettet':
                        print "lifecyclecode is '%s', performing delete" % message.lifecyclecode
                        self.delete(item)
                    else:
                        print "lifecyclecode is '%s', performing update" % message.lifecyclecode
                        self.update(item)
                except InvalidOIOException as e:
                    print e
                self.end_session()
                self.emitter.restart()
            else:
                print "Object type '%s' rejected" % message.objecttype

    def delete(self, item):
        self.session.query(EffectBorder).filter_by(uuid=item.id).delete()
        self.session.commit()

    def update(self, item):
        changed = False
        object_type = item.ENTITY_CLASS
        # self.session.query(EffectBorder).filter_by(object_type=object_type, uuid=item.id).delete()
        db_objects = self.session.query(EffectBorder).filter_by(object_type=object_type, uuid=item.id).all()
        if len(db_objects) > 0:
            for db_object in db_objects:
                self.session.delete(db_object)
            changed = True

        effects = self.get_effects(item)
        start_times = [effect.from_time for effect in effects if self.accept_time(effect.from_time)]
        end_times = [effect.to_time for effect in effects if self.accept_time(effect.to_time)]
        for time in start_times:
            effect_type = self.EFFECT_START
            if time in end_times:
                effect_type = self.EFFECT_BOTH
            if self.store(object_type, item.id, time, effect_type):
                changed = True
        for time in end_times:
            if time in start_times:
                continue
            if self.store(object_type, item.id, time, self.EFFECT_END):
                changed = True
        if changed:
            self.session.commit()
        return changed

    def store(self, objecttype, uuid, time, effect_type):
        time = time.astimezone(pytz.utc)
        print "%s %s updates at %s" % (objecttype, uuid, time)
        obj = self.session.query(EffectBorder).filter_by(object_type=objecttype, uuid=uuid, time=time).first()
        if obj:
            if obj.effect_type != effect_type:
                obj.effect_type = effect_type
                self.session.add(obj)
                return True
        else:
            obj = EffectBorder(object_type=objecttype, uuid=uuid, time=time, effect_type=effect_type)
            self.session.add(obj)
            return True

    def get_effects(self, item, merge=True):
        effects = []
        for registrering in item.registreringer:
            if hasattr(registrering, 'gyldigheder') and registrering.gyldigheder:
                for gyldighed in registrering.gyldigheder:
                    effects.append(gyldighed.virkning)
            if hasattr(registrering, 'publiceringer') and registrering.publiceringer:
                for publicering in registrering.publiceringer:
                    effects.append(publicering.virkning)
            if registrering.egenskaber:
                for egenskab in registrering.egenskaber:
                    effects.append(egenskab.virkning)
            if registrering.relationer:
                for type,relations in registrering.relationer.items.iteritems():
                    for relation in relations:
                        effects.append(relation.virkning)
        if merge and len(effects) > 1:
            merged = [effects[0]]
            for item in effects:
                match = False
                for existing in merged:
                    if existing.compare_time(item):
                        match = True
                        break
                if not match:
                    merged.append(item)
            return merged
        else:
            return effects

    def accept_time(self, time):
        if time.year > 3000:
            return False
        if time < datetime.now(pytz.utc):
            return False
        return True


class Emitter:

    running = None
    sleeper = None

    def __init__(self, sessionclass, notification_sender, notify_unsynced=False):
        self.sessionclass = sessionclass
        self.notification_sender = notification_sender
        self.notify_unsynced = notify_unsynced

    def handle_effectborders(self, effectborders, session, send=True):
        messages = []
        for effectborder in effectborders:
            if send:
                messages.append(EffectUpdateMessage(effectborder.uuid, effectborder.object_type, effectborder.effect_type, effectborder.time))
            session.delete(effectborder)
        if len(messages) == 1:
            print "Emitting an EffectUpdateMessage"
        else:
            print "Emitting %d EffectUpdateMessages" % len(messages)
        for message in messages:
            self.notification_sender.send(message)

    def run(self, initialrun=False):
        if self.running:
            raise Exception("Already running")
        self.running = threading.Event()
        self.sleeper = None
        session = self.sessionclass()
        next_effectborder = session.query(EffectBorder).order_by(EffectBorder.time).first()
        effectborders = session.query(EffectBorder).filter_by(time=next_effectborder.time).all()

        if len(effectborders) > 0:
            time = pytz.utc.localize(effectborders[0].time).astimezone(pytz.utc)
            timediff = time - datetime.now(pytz.utc)
            seconds = timediff.total_seconds()
            if seconds < 0:
                self.handle_effectborders(effectborders, session, not initialrun or self.notify_unsynced)
            elif seconds == 0:
                self.handle_effectborders(effectborders, session)
            else:
                print "waiting for %d seconds" % seconds
                self.sleeper = threading.Timer(seconds, self.run)
                self.sleeper.start()
        session.commit()
        session.close()
        self.running.set()
        self.running = None

    def stop(self):
        if self.running is not None:
            if self.sleeper:
                self.sleeper.cancel()
                self.running = None
            else:
                self.running.wait()

    def start(self, initial=True):
        self.run(initial)

    def restart(self):
        self.stop()
        self.run()



main = MoxEffectWatcher()
main.start()