# -*- coding: utf-8 -*-

from .. import message

message_factory = message.MessageFactory()
# server messages
register = message_factory.register('register', (
    'name',
    'host',
    'port'
))
get_servers = message_factory.register('get_servers', (
    'list_step'
))
next_servers = message_factory.register('next_servers', (
    'current'
))
servers_list = message_factory.register('servers_list', (
    'servers'
))
ping = message_factory.register('ping', (
    'sid'
))
error = message_factory.register('error', (
    'type'
))
ack = message_factory.register('ack', (
    'value'
))


class Errors(object):
    TIMEOUT = 1
