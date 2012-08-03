from .. import message

message_factory = message.MessageFactory()
get_servers = message_factory.register('get_servers')
register = message_factory.register('register', (
    'name',
    'address',
    'port'
))
servers_list = chat_msg = message_factory.register('servers_list', (
    'servers'
))
