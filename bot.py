import json
import sys
import httplib2 as httplib2
from message_responder import ChatBot

import sleekxmpp


# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input


class EchoBot(sleekxmpp.ClientXMPP):

    """
    A simple SleekXMPP bot that will greets those
    who enter the room, and acknowledge any messages
    that mentions the bot's nickname.
    """

    def __init__(self, jid, password):
        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.session_start)
        # self.add_event_handler("changed_status", self.changed_status)
        self.add_event_handler("message", self.message)

    def session_start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """

        self.send_presence()
        # Most get_*/set_* methods from plugins use Iq stanzas, which
        # can generate IqError and IqTimeout exceptions
        # try:
        #     roster = self.get_roster()
        # except IqError as err:
        #     print("IqError")
        #     self.disconnect()
        # except IqTimeout:
        #     print("Iq Timeout Error ")
        #     self.disconnect()

        self.get_roster()
        # self.send_message(mto='182037_2486194@chat.hipchat.com',
        #                   mbody="I have been built to annoy you",
        #                   mtype='chat')
        # print("Sent the message")

        # self.disconnect(wait=True)


    # def changed_status(self, presence):
    #     who = presence['from']
    #     type = presence['type']
    #     status = presence['status']
    #     name = self.client_roster['%s@%s' % (who.user, who.server)]['name']
    #     hcid = long(who.username.split('_')[1])
    #     u = get_user_by_hcid(hcid)
    #     if not u:

    def message(self, msg):
        """
        Process incoming message stanzas. Be aware that this also
        includes MUC messages and error messages. It is usually
        a good idea to check the messages's type before processing
        or sending replies.
        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.
        """

        print("In message")

        handler = ChatBot()
        if msg['type'] in ('chat', 'normal'):
            if str(msg['from']).split('/', 1)[0] in self.client_roster:
                resp, content = httplib2.Http().request("%s?format=json&auth_token=%s" %
                          ("https://api.hipchat.com/v2/user/" + str(msg['from']).split('@', 1)[0].split('_')[1],
                           "vwTlL3hAO7a4XH2TqsP991KAF0C2MYvFf0ovmlbE"))
                user = json.loads(content)
            msg.reply(handler.handle_message(msg['body'], {'user': user})).send()


if __name__ == '__main__':
    # Connect to the XMPP server and start processing XMPP stanzas.
    xmpp = EchoBot('182037_3263982@chat.hipchat.com', 'Starwars')
    # xmpp = EchoBot('182037_1550099@chat.hipchat.com', 'kF4oWDNkvBWf')
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0199',
                         {'keepalive': True,
                          'interval': 59})  # XMPP Ping
    if xmpp.connect():
        # If you do not have the dnspython library installed, you will need
        # to manually specify the name of the server if it does not match
        # the one in the JID. For example, to use Google Talk you would
        # need to use:
        #
        # if xmpp.connect(('talk.google.com', 5222)):
        #     ...
        xmpp.process(block=True)
        print("Connected")
    else:
        print("Unable to connect.")

