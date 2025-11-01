# Casio fx-991-like Scientific Calculator — Streamlit app

This document contains a ready-to-run Streamlit single-file app (`app.py`) that implements a scientific calculator styled to *look and behave* similarly to a Casio fx-991. It also includes a short README with instructions for running locally and for pushing to GitHub.

---

## Files in this single-file deliverable

* `app.py` — the Streamlit application. Copy this into a GitHub repository (or paste into a file locally) and run with `streamlit run app.py`.

---

## Features implemented

* Numeric buttons (0–9), decimal point, parentheses
* Basic arithmetic: `+ - * /`
* Power `^` (exponent), `x^2`, `x^3`
* Root: `sqrt()`
* Factorial `!`
* Trigonometry: `sin`, `cos`, `tan` with DEG/RAD mode toggle
* Inverse trig (`asin`, `acos`, `atan`)
* Logarithms: `log10`, `ln`
* Constants: `pi`, `e`
* Memory (M+, M-, MR, MC)
* Clear (C), All Clear (AC), Backspace
* Expression input box and history of calculations
* Safe expression evaluator using Python `ast` with a whitelist of functions/operators

---

## `app.py` (Streamlit app)

```python
# app.py
import streamlit as st
import math
import ast
import operator as op

# ---------- Safe evaluator ----------
# Allowed operators mapping
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

# Allowed functions and constants
MATH_FUNCS = {
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    'sqrt': math.sqrt,
    'log': lambda x: math.log10(x),  # log base 10
    'ln': math.log,
    'log10': math.log10,
    'abs': abs,
    'fact': math.factorial,
    'factorial': math.factorial,
    'pi': math.pi,
    'e': math.e,
    'pow': pow,
}

# Safe eval using ast
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
    """Evaluate a math expression safely (supports functions listed in MATH_FUNCS)."""
    # preprocessing: replace '^' with '**', allow the factorial notation '!'
    expr = expr.replace('^', '**')
    # handle factorial (n!) -> fact(n)
    # simple approach: replace occurrences of number! or close-paren!
    # We'll convert `number!` or `)!(maybe)` patterns to fact(number)
    # Note: this is a minimal parser for factorial notation.
    i = 0
    out = ''
    while i < len(expr):
        ch = expr[i]
        if ch == '!':
            # find previous expression token to wrap
            # backtrack to find the token start
            j = len(out) - 1
            # If expression ends with ')', find matching '('
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
                # number or name: capture digits, dot, letters
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

    try:
        node = ast.parse(expr, mode='eval')
        visitor = EvalVisitor()
        return visitor.visit(node)
    except Exception as e:
        raise

# ---------- Streamlit UI ----------

st.set_page_config(page_title='Casio fx-991 — Streamlit', layout='centered')

# Simple CSS to approximate Casio look
st.markdown("""
<style>
body {background-color: #e9ecf0}
.calculator-container {background:#2f3640; padding: 12px; border-radius:12px; max-width:420px; margin:auto}
.display {background:#ffffff; color:#000; padding:10px; border-radius:8px; font-size:24px;}
.small-btn {width:60px; height:48px; margin:4px; border-radius:8px; border: none; font-weight:600}
.op-btn {background:#ffb86b}
.func-btn {background:#6cb6ff}
.num-btn {background:#f0f0f0}
.mode {background:#ffd166}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="calculator-container">', unsafe_allow_html=True)

if 'expr' not in st.session_state:
    st.session_state.expr = ''
if 'history' not in st.session_state:
    st.session_state.history = []
if 'memory' not in st.session_state:
    st.session_state.memory = 0.0
if 'angle' not in st.session_state:
    st.session_state.angle = 'DEG'  # or 'RAD'

# Header
st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center; color:white; padding:6px;'>"
            f"<div style='font-weight:700'>fx-991 · Streamlit</div>"
            f"<div style='font-size:12px'>Mode: {st.session_state.angle}</div>"
            f"</div>", unsafe_allow_html=True)

# Display area
st.text_input('Expression', key='expr_input', value=st.session_state.expr, on_change=lambda: st.session_state.update({'expr': st.session_state.expr_input}))
st.markdown(f"<div class=\"display\">{st.session_state.expr}</div>", unsafe_allow_html=True)

# Buttons grid helpers
def btn(label, key=None, style='num-btn'):
    if key is None:
        key = label
    clicked = st.button(label, key=key)
    if clicked:
        st.session_state.expr += label

col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])

with col1:
    if st.button('AC'):
        st.session_state.expr = ''
    if st.button('('):
        st.session_state.expr += '('
    if st.button(')'):
        st.session_state.expr += ')'
    if st.button('MC'):
        st.session_state.memory = 0.0

with col2:
    if st.button('C'):
        st.session_state.expr = ''
    if st.button('7'):
        st.session_state.expr += '7'
    if st.button('8'):
        st.session_state.expr += '8'
    if st.button('9'):
        st.session_state.expr += '9'

with col3:
    if st.button('⌫'):
        st.session_state.expr = st.session_state.expr[:-1]
    if st.button('4'):
        st.session_state.expr += '4'
    if st.button('5'):
        st.session_state.expr += '5'
    if st.button('6'):
        st.session_state.expr += '6'

with col4:
    if st.button('%'):
```
