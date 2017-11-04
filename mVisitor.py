# Generated from /home/zetsubou/Projects/Python/metodo simplex kivy/m.g4 by ANTLR 4.7
from antlr4 import *
from antlr4.tree.Tree import TerminalNodeImpl

if __name__ is not None and "." in __name__:
    from .mParser import mParser
else:
    from mParser import mParser


# This class defines a complete generic visitor for a parse tree produced by mParser.

class mVisitor(ParseTreeVisitor):
    # Visit a parse tree produced by mParser#expression.
    def visitExpression(self, ctx: mParser.ExpressionContext):
        first_iter = True
        data = None
        operator = None
        for x in ctx.getChildren():
            if first_iter:
                first_iter = False
                data = self.visitOp_add(x)
            else:
                if isinstance(x, TerminalNodeImpl):
                    operator = x.getText()
                else:
                    new_data = self.visitOp_add(x)
                    if operator == ">":
                        if data["m_coefficient"] == new_data["m_coefficient"]:
                            return float(data["rhs"]) > float(new_data["rhs"])
                        else:
                            return float(data["m_coefficient"]) > float(new_data["m_coefficient"])
                    elif operator == ">=":
                        if data["m_coefficient"] == new_data["m_coefficient"]:
                            return float(data["rhs"]) >= float(new_data["rhs"])
                        else:
                            return float(data["m_coefficient"]) >= float(new_data["m_coefficient"])
                    elif operator == "<":
                        if data["m_coefficient"] == new_data["m_coefficient"]:
                            return float(data["rhs"]) < float(new_data["rhs"])
                        else:
                            return float(data["m_coefficient"]) < float(new_data["m_coefficient"])
                    else:  # operator = <=
                        if data["m_coefficient"] == new_data["m_coefficient"]:
                            return float(data["rhs"]) <= float(new_data["rhs"])
                        else:
                            return float(data["m_coefficient"]) <= float(new_data["m_coefficient"])
        return data

    # Visit a parse tree produced by mParser#op_add.
    def visitOp_add(self, ctx: mParser.Op_addContext):
        first_iter = True
        data = None
        operator = None
        for x in ctx.getChildren():
            if first_iter:
                first_iter = False
                data = self.visitOp_mul(x)
            else:
                if isinstance(x, TerminalNodeImpl):
                    operator = x.getText()
                else:
                    new_data = self.visitOp_mul(x)
                    if operator == "+":
                        data["rhs"] = str(float(data["rhs"]) + float(new_data["rhs"]))
                        data["m_coefficient"] = str(float(data["m_coefficient"]) + float(new_data["m_coefficient"]))
                    else:
                        data["rhs"] = str(float(data["rhs"]) - float(new_data["rhs"]))
                        data["m_coefficient"] = str(float(data["m_coefficient"]) - float(new_data["m_coefficient"]))
        return data

    # Visit a parse tree produced by mParser#op_mul.
    def visitOp_mul(self, ctx: mParser.Op_mulContext):
        first_iter = True
        data = None
        for x in ctx.getChildren():
            if first_iter:
                first_iter = False
                data = self.visitAtom(x)
            else:
                if isinstance(x, TerminalNodeImpl):
                    pass
                else:
                    new_data = self.visitAtom(x)
                    if data["m_coefficient"] != "0.0" and new_data["m_coefficient"] != "0.0":
                        raise ValueError  # Unexpected input
                    else:
                        if data["m_coefficient"] == "0.0" and new_data["m_coefficient"] == "0.0":
                            data["rhs"] = str(float(data["rhs"]) * float(new_data["rhs"]))
                        elif data["m_coefficient"] == "0.0":
                            data["m_coefficient"] = str(float(data["rhs"]) * float(new_data["m_coefficient"]))
                            data["rhs"] = "0.0"
                        else:
                            data["m_coefficient"] = str(float(data["m_coefficient"]) * float(new_data["rhs"]))
        return data

    def visitDummy_unary_add(self, ctx: mParser.Dummy_unary_addContext):
        return [x.getText() for x in ctx.getChildren()].count("-") % 2 != 0

    # Visit a parse tree produced by mParser#atom.
    def visitAtom(self, ctx: mParser.AtomContext):
        if ctx.i:  # int
            data = {"m_coefficient": "0.0", "rhs": ctx.i.text}
            if self.visitDummy_unary_add(ctx.p):
                data["rhs"] = "-" + ctx.i.text + ".0"

            return data
        elif ctx.f:  # float
            data = {"m_coefficient": "0.0", "rhs": ctx.f.text}
            if self.visitDummy_unary_add(ctx.p):
                data["rhs"] = "-" + ctx.f.text

            return data
        elif ctx.m:  # m|-m
            data = {"m_coefficient": "1", "rhs": "0.0"}
            if self.visitDummy_unary_add(ctx.p):
                data["m_coefficient"] = "-1"

            return data
        elif ctx.e:  # Parenthesized expression
            data = self.visitExpression(ctx.e)
            if self.visitDummy_unary_add(ctx.p):
                data["m_coefficient"] = "-" + (ctx.c.text if "." in ctx.c.text else ctx.c.text + ".0")
            return data
        else:  # 2m, 3m etc...
            data = {"m_coefficient": ctx.c.text, "rhs": "0.0"}
            if self.visitDummy_unary_add(ctx.p):
                data["m_coefficient"] = "-" + (ctx.c.text if "." in ctx.c.text else ctx.c.text + ".0")

            return data

    # Visit a parse tree produced by mParser#start_rule.
    def visitStart_rule(self, ctx: mParser.Start_ruleContext):
        return self.visitChildren(ctx)


del mParser
