"""
Byte strings and numerics sent between server and client during message handling,
as defined in the specification.
"""
from enum import Enum, IntEnum, auto, unique

from utils import typecaster


# https://docs.python.org/3.7/library/enum.html#omitting-values
class NoValueEnum(Enum):
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


# https://modern.ircdocs.horse/index.html#rplwelcome-001
@unique
class ReplyCode(IntEnum):
    """All reply numerics defined by the protocol spec."""

    RPL_WELCOME = 1
    RPL_YOURHOST = 2
    RPL_CREATED = 3
    RPL_MYINFO = 4
    RPL_ISUPPORT = 5

    RPL_BOUNCE = 10

    RPL_UMODEIS = 221

    RPL_LUSERCLIENT = 251
    RPL_LUSEROP = 252
    RPL_LUSERUNKNOWN = 253
    RPL_LUSERCHANNELS = 254
    RPL_LUSERME = 255
    RPL_ADMINME = 256
    RPL_ADMINLOC1 = 257
    RPL_ADMINLOC2 = 258
    RPL_ADMINEMAIL = 259

    RPL_TRYAGAIN = 263

    RPL_LOCALUSERS = 265
    RPL_GLOBALUSERS = 266

    RPL_WHOISCERTFP = 276

    RPL_NONE = 300
    RPL_AWAY = 301

    RPL_USERHOST = 302
    RPL_ISON = 303

    RPL_UNAWAY = 305
    RPL_NOWAWAY = 306

    RPL_WHOISUSER = 311
    RPL_WHOISSERVER = 312
    RPL_WHOISOPERATOR = 313
    RPL_WHOWASUSER = 314

    RPL_WHOISIDLE = 317
    RPL_ENDOFWHOIS = 318
    RPL_WHOISCHANNELS = 319

    RPL_LISTSTART = 321
    RPL_LIST = 322
    RPL_LISTEND = 323
    RPL_CHANNELMODEIS = 324

    RPL_CREATIONTIME = 329

    RPL_NOTOPIC = 331
    RPL_TOPIC = 332
    RPL_TOPICWHOTIME = 333

    RPL_INVITING = 341

    RPL_INVITELIST = 346
    RPL_ENDOFINVITELIST = 347
    RPL_EXCEPTLIST = 348
    RPL_ENDOFEXCEPTLIST = 349

    RPL_VERSION = 351

    RPL_NAMREPLY = 353

    RPL_ENDOFNAMES = 366
    RPL_BANLIST = 367
    RPL_ENDOFBANLIST = 368
    RPL_ENDOFWHOWAS = 369

    RPL_MOTDSTART = 375
    RPL_MOTD = 372
    RPL_ENDOFMOTD = 376

    RPL_YOUREOPER = 381
    RPL_REHASHING = 382

    RPL_STARTTLS = 670

    RPL_LOGGEDIN = 900
    RPL_LOGGEDOUT = 901
    RPL_SASLSUCCESS = 903
    RPL_SASLMECHS = 908


# https://modern.ircdocs.horse/index.html#errunknownerror-400
@unique
class ErrorCode(IntEnum):
    """All error status codes defined by the protocol spec."""

    ERR_UNKNOWNERROR = 400
    ERR_NOSUCHNICK = 401
    ERR_NOSUCHSERVER = 402
    ERR_NOSUCHCHANNEL = 403
    ERR_CANNOTSENDTOCHAN = 404
    ERR_TOOMANYCHANNELS = 405

    ERR_INVALIDCAPCMD = 410

    ERR_INPUTTOOLONG = 417
    ERR_UNKNOWNCOMMAND = 421
    ERR_NOMOTD = 422

    ERR_ERRONEUSNICKNAME = 432
    ERR_NICKNAMEINUSE = 433

    ERR_USERNOTINCHANNEL = 441
    ERR_NOTONCHANNEL = 442
    ERR_USERONCHANNEL = 443

    ERR_NOTREGISTERED = 451

    ERR_NEEDMOREPARAMS = 461
    ERR_ALREADYREGISTERED = 462

    ERR_PASSWDMISMATCH = 464
    ERR_YOUREBANNEDCREEP = 465

    ERR_CHANNELISFULL = 471
    ERR_UNKNOWNMODE = 472
    ERR_INVITEONLYCHAN = 473
    ERR_BANNEDFROMCHAN = 474
    ERR_BADCHANNELKEY = 475

    ERR_NOPRIVILEGES = 481
    ERR_CHANOPRIVSNEEDED = 482
    ERR_CANTKILLSERVER = 483

    ERR_NOOPERHOST = 491

    ERR_UMODEUNKNOWNFLAG = 501
    ERR_USERSDONTMATCH = 502

    ERR_STARTTLS = 691

    ERR_NOPRIVS = 723

    ERR_NICKLOCKED = 902
    ERR_SASLFAIL = 904
    ERR_SASLTOOLONG = 905
    ERR_SASLABORTED = 906
    ERR_SASLALREADY = 907


class CapSubCommand(Enum):
    """Capability negotiation subcommands with their client-sent expected parameters."""

    LS = [typecaster(int)]
    LIST = None
    REQ = [typecaster(str, many=True)]
    ACK = None
    NAK = None
    END = None
    # NEW = None
    # DEL = None


@unique
class ClientStatus(Enum):
    UNREGISTERED = "unregistered"
    NEGOTIATING = "negotiating"
    REGISTERED = "registered"


@unique
class Capabilities(Enum):
    """Implemented IRC v3 capabilities for this server. https://ircv3.net/irc/"""

    MESSAGE_TAGS = "message-tags"
    # TYPING = "typing"
    # AWAY_NOTIFY = "away-notify"
    # STRICT_TRANSPORT_SECURITY = "sts"
    # BATCH = "batch"
    # SERVER_TIME = "server-time"
    # CHAT_HISTORY = "draft/chathistory"
