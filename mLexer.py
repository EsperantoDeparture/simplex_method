# Generated from /home/zetsubou/Projects/Python/metodo simplex kivy/m.g4 by ANTLR 4.7
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\17")
        buf.write("G\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write("\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r\4\16")
        buf.write("\t\16\3\2\3\2\3\3\3\3\3\4\6\4#\n\4\r\4\16\4$\3\5\6\5(")
        buf.write("\n\5\r\5\16\5)\3\5\3\5\6\5.\n\5\r\5\16\5/\3\6\3\6\3\7")
        buf.write("\3\7\3\7\3\b\3\b\3\t\3\t\3\t\3\n\3\n\3\13\3\13\3\f\3\f")
        buf.write("\3\r\3\r\3\16\3\16\3\16\3\16\2\2\17\3\3\5\4\7\5\t\6\13")
        buf.write("\7\r\b\17\t\21\n\23\13\25\f\27\r\31\16\33\17\3\2\3\5\2")
        buf.write("\13\f\17\17\"\"\2I\2\3\3\2\2\2\2\5\3\2\2\2\2\7\3\2\2\2")
        buf.write("\2\t\3\2\2\2\2\13\3\2\2\2\2\r\3\2\2\2\2\17\3\2\2\2\2\21")
        buf.write("\3\2\2\2\2\23\3\2\2\2\2\25\3\2\2\2\2\27\3\2\2\2\2\31\3")
        buf.write("\2\2\2\2\33\3\2\2\2\3\35\3\2\2\2\5\37\3\2\2\2\7\"\3\2")
        buf.write("\2\2\t\'\3\2\2\2\13\61\3\2\2\2\r\63\3\2\2\2\17\66\3\2")
        buf.write("\2\2\218\3\2\2\2\23;\3\2\2\2\25=\3\2\2\2\27?\3\2\2\2\31")
        buf.write("A\3\2\2\2\33C\3\2\2\2\35\36\7*\2\2\36\4\3\2\2\2\37 \7")
        buf.write("+\2\2 \6\3\2\2\2!#\4\62;\2\"!\3\2\2\2#$\3\2\2\2$\"\3\2")
        buf.write("\2\2$%\3\2\2\2%\b\3\2\2\2&(\4\62;\2\'&\3\2\2\2()\3\2\2")
        buf.write("\2)\'\3\2\2\2)*\3\2\2\2*+\3\2\2\2+-\7\60\2\2,.\4\62;\2")
        buf.write("-,\3\2\2\2./\3\2\2\2/-\3\2\2\2/\60\3\2\2\2\60\n\3\2\2")
        buf.write("\2\61\62\7@\2\2\62\f\3\2\2\2\63\64\7@\2\2\64\65\7?\2\2")
        buf.write("\65\16\3\2\2\2\66\67\7>\2\2\67\20\3\2\2\289\7>\2\29:\7")
        buf.write("?\2\2:\22\3\2\2\2;<\7o\2\2<\24\3\2\2\2=>\7-\2\2>\26\3")
        buf.write("\2\2\2?@\7/\2\2@\30\3\2\2\2AB\7,\2\2B\32\3\2\2\2CD\t\2")
        buf.write("\2\2DE\3\2\2\2EF\b\16\2\2F\34\3\2\2\2\6\2$)/\3\b\2\2")
        return buf.getvalue()


class mLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    T__0 = 1
    T__1 = 2
    INT = 3
    FLOAT = 4
    GT = 5
    GE = 6
    LT = 7
    LE = 8
    M = 9
    ADD = 10
    SUB = 11
    MUL = 12
    WS = 13

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'('", "')'", "'>'", "'>='", "'<'", "'<='", "'m'", "'+'", "'-'", 
            "'*'" ]

    symbolicNames = [ "<INVALID>",
            "INT", "FLOAT", "GT", "GE", "LT", "LE", "M", "ADD", "SUB", "MUL", 
            "WS" ]

    ruleNames = [ "T__0", "T__1", "INT", "FLOAT", "GT", "GE", "LT", "LE", 
                  "M", "ADD", "SUB", "MUL", "WS" ]

    grammarFileName = "m.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.7")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


