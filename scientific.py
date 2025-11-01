import streamlit as st
import math
import ast
import operator as op

# ---------- Safe evaluator ----------
ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
    ast.Mod: op.mod,
    ast.FloorDiv: op.floordiv,
}

MATH_FUNCS = {
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    'sqrt': math.sqrt,
    'log': lambda x: math.log10(x),
    'ln': math.log,
    'log10': math.log10,
    'abs': abs,
    'fact': math.factorial,
    'factorial': math.factorial,
    'pi': math.pi,
    'e': math.e,
    'pow': pow,
}

class EvalVisitor(ast.NodeVisitor):
    def visit(self, node):
        if isinstance(node, ast.Expression):
            return self.visit(node.body)
        elif isinstance(node, ast.BinOp):
            left = self.visit(node.left)
            right = self.visit(node.right)
            op_type = type(node.op)
            if op_type in ALLOWED_OPERATORS:
                return ALLOWED_OPERATORS[op_type](left, right)
            raise ValueError(f"Operator {op_type} not allowed")
        elif isinstance(node, ast.UnaryOp):
            operand = self.visit(node.operand)
            op_type = type(node.op)
            if op_type in ALLOWED_OPERATORS:
                return ALLOWED_OPERATORS[op_type](operand)
            raise ValueError(f"Unary operator {op_type} not allowed")
        elif isinstance(node, ast.Num):
            return node.n
        elif hasattr(ast, 'Constant') and isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                name = func.id
                if name in MATH_FUNCS:
                    args = [self.visit(a) for a in node.args]
                    return MATH_FUNCS[name](*args)
            raise ValueError("Function calls are restricted")
        elif isinstance(node, ast.Name):
            if node.id in MATH_FUNCS:
                return MATH_FUNCS[node.id]
            raise ValueError(f"Name {node.id} is not allowed")
        elif isinstance(node, ast.Expr):
            return self.visit(node.value)
        else:
            raise ValueError(f"Expression element {type(node)} not allowed")

def safe_eval(expr: str):
    expr = expr.replace('^', '**')
    i = 0
    out = ''
    while i < len(expr):
        ch = expr[i]
        if ch == '!':
            j = len(out) - 1
            if j >= 0 and out[j] == ')':
                depth = 0
                k = j
                while k >= 0:
                    if out[k] == ')':
                        depth += 1
                    elif out[k] == '(':
                        depth -= 1
                        if depth == 0:
                            break
                    k -= 1
                token = out[k: j + 1]
                out = out[:k] + f'factorial{token}'
            else:
                k = j
                while k >= 0 and (out[k].isalnum() or out[k] == '.' or out[k] == '_'):
                    k -= 1
                token = out[k+1: j+1]
                out = out[:k+1] + f'factorial({token})'
            i += 1
            continue
        else:
            out += ch
        i += 1
    expr = out

    node = ast.parse(expr, mode='eval')
    visitor = EvalVisitor()
    return visitor.visit(node)

# ---------- Streamlit UI ---
