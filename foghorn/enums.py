"""
Byte strings and numerics sent between server and client during message handling,
as defined in the specification.
"""
from enum import Enum, auto, unique

from .typing import typecaster


# https://docs.python.org/3.7/library/enum.html#omitting-values
class NoValueEnum(Enum):
    """Represents an enumeration with an irrelevant value."""

    def __repr__(self):
        return "<%s.%s>" % (self.__class__.__name__, self.name)


@unique
class Command(NoValueEnum):
    """All valid client and server commands defined by the protocol spec."""

    # connection
    CAP = auto()
    AUTHENTICATE = auto()
    PASS = auto()
    NICK = auto()
    USER = auto()
    OPER = auto()
    QUIT = auto()

    # operators
    JOIN = auto()
    PART = auto()
    TOPIC = auto()
    NAMES = auto()
    LIST = auto()

    # server
    MOTD = auto()
    VERSION = auto()
    ADMIN = auto()
    CONNECT = auto()
    TIME = auto()
    STATS = auto()
    INFO = auto()
    MODE = auto()

    # sending
    PRIVMSG = auto()
    NOTICE = auto()

    # miscellaneous
    USERHOST = auto()
    KILL = auto()


class NumericEnum(Enum):
    """A string enumeration that supports literal matching against its name value."""

    @property
    def numeric(self):
        return self.value[0]

    @property
    def msg(self):
        return self.value[1]


# https://modern.ircdocs.horse/index.html#rplwelcome-001
@unique
class ReplyCode(NumericEnum):
    """All reply numerics defined by the protocol spec."""

    RPL_WELCOME = (1, "Welcome to the <networkname> Network, <nick>[!<user>@<host>]")
    RPL_YOURHOST = (2, "Your host is <servername>, running version <version>")
    RPL_CREATED = (3, "This server was created <datetime>")
    RPL_MYINFO = (4, None)
    RPL_ISUPPORT = (5, "are supported by this server")

    RPL_BOUNCE = (10, None)

    RPL_UMODEIS = (221, None)

    RPL_LUSERCLIENT = (251, "There are <u> users and <i> invisible on <s> servers")
    RPL_LUSEROP = (252, "operator(s) online")
    RPL_LUSERUNKNOWN = (253, "unknown connection(s)")
    RPL_LUSERCHANNELS = (254, "channels formed")
    RPL_LUSERME = (255, "I have <c> clients and <s> servers")
    RPL_ADMINME = (256, "Administrative info")
    RPL_ADMINLOC1 = (257, "<info>")
    RPL_ADMINLOC2 = (258, "<info>")
    RPL_ADMINEMAIL = (259, "<info>")

    RPL_TRYAGAIN = (263, "Please wait a while and try again.")

    RPL_LOCALUSERS = (265, "Current local users <u>, max <m>")
    RPL_GLOBALUSERS = (266, "Current global users <u>, max <m>")

    RPL_WHOISCERTFP = (276, "has client certificate fingerprint <fingerprint>")

    RPL_NONE = (300, "Undefined format")
    RPL_AWAY = (301, None)
    RPL_USERHOST = (302, None)
    RPL_ISON = (303, "[<nickname>{ <nickname>}]")
    RPL_UNAWAY = (305, "You are no longer marked as being away")
    RPL_NOWAWAY = (306, "You have been marked as being away")

    RPL_WHOISUSER = (311, None)
    RPL_WHOISSERVER = (312, "<server info>")
    RPL_WHOISOPERATOR = (313, "is an IRC operator")
    RPL_WHOWASUSER = (314, None)

    RPL_WHOISIDLE = (317, "seconds idle, signon time")
    RPL_ENDOFWHOIS = (318, "End of /WHOIS list")
    RPL_WHOISCHANNELS = (319, None)

    RPL_LISTSTART = (321, "Users  Name")
    RPL_LIST = (322, None)
    RPL_LISTEND = (323, "End of /LIST")
    RPL_CHANNELMODEIS = (324, None)

    RPL_CREATIONTIME = (329, None)

    RPL_NOTOPIC = (331, "No topic is set")
    RPL_TOPIC = (332, None)
    RPL_TOPICWHOTIME = (333, None)

    RPL_INVITING = (341, None)

    RPL_INVITELIST = (346, None)
    RPL_ENDOFINVITELIST = (347, "End of channel invite list")
    RPL_EXCEPTLIST = (348, None)
    RPL_ENDOFEXCEPTLIST = (349, "End of channel exception list")

    RPL_VERSION = (351, None)

    RPL_NAMREPLY = (353, None)

    RPL_ENDOFNAMES = (366, "End of /NAMES list")
    RPL_BANLIST = (367, None)
    RPL_ENDOFBANLIST = (368, "End of channel ban list")
    RPL_ENDOFWHOWAS = (369, "End of WHOWAS")

    RPL_MOTDSTART = (375, "- <server> Message of the day - ")

    RPL_MOTD = (372, None)

    RPL_ENDOFMOTD = (376, "End of /MOTD command.")

    RPL_YOUREOPER = (381, "You are now an IRC operator")
    RPL_REHASHING = (382, "Rehashing")

    RPL_STARTTLS = (670, "STARTTLS successful, proceed with TLS handshake")

    RPL_LOGGEDIN = (900, "You are now logged in as <username>")
    RPL_LOGGEDOUT = (901, "You are now logged out")
    RPL_SASLSUCCESS = (903, "SASL authentication successful")
    RPL_SASLMECHS = (908, "are available SASL mechanisms")


# https://modern.ircdocs.horse/index.html#errunknownerror-400
@unique
class ErrorCode(NumericEnum):
    """All standardized error status codes with their default messages."""

    ERR_UNKNOWNERROR = (400, None)
    ERR_NOSUCHNICK = (401, "No such nick/channel.")
    ERR_NOSUCHSERVER = (402, "No such server.")
    ERR_NOSUCHCHANNEL = (403, "No such channel.")
    ERR_CANNOTSENDTOCHAN = (404, "Cannot send to channel.")
    ERR_TOOMANYCHANNELS = (405, "You have joined too many channels.")

    ERR_INVALIDCAPCMD = (410, "Invalid CAP command.")

    ERR_INPUTTOOLONG = (417, "Input line was too long.")

    ERR_UNKNOWNCOMMAND = (421, "Unknown command.")
    ERR_NOMOTD = (422, "No MOTD has been set.")

    ERR_NONICKNAMEGIVEN = (431, "No nickname was supplied.")
    ERR_ERRONEUSNICKNAME = (432, "Erroneus nickname.")
    ERR_NICKNAMEINUSE = (433, "Nickname is already in use.")

    ERR_USERNOTINCHANNEL = (441, "They aren't on that channel.")
    ERR_NOTONCHANNEL = (442, "You're not on that channel.")
    ERR_USERONCHANNEL = (443, "is already on channel.")

    ERR_NOTREGISTERED = (451, "You have not registered.")

    ERR_NEEDMOREPARAMS = (461, "Not enough parameters.")
    ERR_ALREADYREGISTERED = (462, "You may not reregister.")

    ERR_PASSWDMISMATCH = (464, "Password incorrect.")
    ERR_YOUREBANNEDCREEP = (465, "You are banned from this server.")

    ERR_CHANNELISFULL = (471, "Cannot join channel (+l)")
    ERR_UNKNOWNMODE = (472, "is unknown mode char to me")
    ERR_INVITEONLYCHAN = (473, "Cannot join channel (+i)")
    ERR_BANNEDFROMCHAN = (474, "Cannot join channel (+b)")
    ERR_BADCHANNELKEY = (475, "Cannot join channel (+k)")

    ERR_NOPRIVILEGES = (481, "Permission denied.")
    ERR_CHANOPRIVSNEEDED = (482, "You're not channel operator.")
    ERR_CANTKILLSERVER = (483, "You cant kill a server!")

    ERR_NOOPERHOST = (491, "No O-lines for your host.")

    ERR_UMODEUNKNOWNFLAG = (501, "Unknown MODE flag")
    ERR_USERSDONTMATCH = (502, "Cant change mode for other users.")

    ERR_STARTTLS = (691, "STARTTLS failed (Wrong moon phase).")

    ERR_NOPRIVS = (723, "Insufficient oper privileges.")

    ERR_NICKLOCKED = (902, "You must use a nick assigned to you.")

    ERR_SASLFAIL = (904, "SASL authentication failed.")
    ERR_SASLTOOLONG = (905, "SASL message too long.")
    ERR_SASLABORTED = (906, "SASL authentication aborted.")
    ERR_SASLALREADY = (907, "You have already authenticated using SASL.")


class NamedComparisonEnum(Enum):
    """A string enumeration that supports literal matching against its name value."""

    def __eq__(self, obj):
        return self.name == obj


class CapSubCommand(NamedComparisonEnum):
    """Capability negotiation subcommands with their client-sent expected parameters."""

    LS = [typecaster(int, optional=True)]
    LIST = None
    REQ = [typecaster(str, many=True)]
    ACK = None
    NAK = None
    END = None
    # NEW = None
    # DEL = None


@unique
class ClientStatus(str, NamedComparisonEnum):
    UNREGISTERED = "unregistered"
    NEGOTIATING = "negotiating"
    REGISTERED = "registered"


@unique
class Capabilities(str, Enum):
    """Implemented IRC v3 capabilities for this server. https://ircv3.net/irc/"""

    MESSAGE_TAGS = "message-tags"
    # TYPING = "typing"
    # AWAY_NOTIFY = "away-notify"
    # STRICT_TRANSPORT_SECURITY = "sts"
    # BATCH = "batch"
    # SERVER_TIME = "server-time"
    # CHAT_HISTORY = "draft/chathistory"
