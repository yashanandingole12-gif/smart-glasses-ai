import ast
import math
import operator
import re
from fractions import Fraction
from typing import Optional, Dict, Any, Tuple, Union, List

# Supported AST Operators for safe evaluation
_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def _safe_eval_ast_with_vars(node: ast.AST, var_values: Dict[str, Union[float, Fraction]]) -> Union[float, Fraction]:
    """Recursively evaluate an AST expression safely with variable substitutions."""
    if isinstance(node, ast.Expression):
        return _safe_eval_ast_with_vars(node.body, var_values)
    elif isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return Fraction(node.value) if isinstance(node.value, int) else float(node.value)
        raise ValueError(f"Unsupported constant type: {type(node.value)}")
    elif isinstance(node, ast.Name):
        var_name = node.id.lower()
        if var_name in var_values:
            return var_values[var_name]
        raise ValueError(f"Unknown variable in expression: {node.id}")
    elif isinstance(node, ast.BinOp):
        left = _safe_eval_ast_with_vars(node.left, var_values)
        right = _safe_eval_ast_with_vars(node.right, var_values)
        op_type = type(node.op)
        if op_type not in _SAFE_OPERATORS:
            raise ValueError(f"Unsupported operator: {op_type}")
        if op_type in (ast.Div, ast.FloorDiv) and right == 0:
            raise ZeroDivisionError("Division by zero is undefined.")
        if op_type == ast.Pow:
            if abs(float(right)) > 1000 or abs(float(left)) > 10000:
                raise OverflowError("Exponentiation exceeds safe compute limit.")
            return float(left) ** float(right)
        return _SAFE_OPERATORS[op_type](left, right)
    elif isinstance(node, ast.UnaryOp):
        operand = _safe_eval_ast_with_vars(node.operand, var_values)
        op_type = type(node.op)
        if op_type not in _SAFE_OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type}")
        return _SAFE_OPERATORS[op_type](operand)
    else:
        raise ValueError(f"Unsupported AST node: {type(node)}")


class DeterministicMathEngine:
    """
    Authoritative, Safe Deterministic Math Engine for Smart Glasses Assistant.
    Supports:
    - Spoken language normalization (parentheses, verbal operators, decimals, fractions)
    - Linear algebraic equation solving (ax + b = cx + d)
    - Step-by-step breakdown generation
    - Zero-LaTeX clean spoken formatting for Smart Glass TTS
    """

    def normalize_query(self, query: str) -> str:
        """
        Convert spoken and typed natural math expressions into a canonical algebraic string.
        Unified pipeline for Talk mode (STT) and text input.
        """
        q = query.strip().lower()

        # Remove polite prefixes & solver prompts
        q = re.sub(r"^(?:what\s+is\s+(?:the\s+value\s+of\s+)?[a-zA-Z]\s+(?:if|in)|what\s+is|what\'s|calculate|compute|solve\s+for\s+[a-zA-Z]|solve\s+for|solve|find\s+[a-zA-Z]\s+in|find\s+[a-zA-Z]|evaluate|eval|bhai|batao|kya\s+hai)\s+", "", q)
        q = re.sub(r"(?:\s+(?:kitna\s+hota\s+hai|kitna\s+hoga|kitna\s+hai|batao|please|for\s+me))?[\s\?\.!]*$", "", q)

        # 1. Spoken Parentheses & Brackets Normalization
        q = re.sub(r"\b(?:open\s+bracket|open\s+parenthesis|start\s+bracket|bracket\s+open)\b", " ( ", q)
        q = re.sub(r"\b(?:close\s+bracket|close\s+parenthesis|end\s+bracket|bracket\s+close)\b", " ) ", q)
        q = re.sub(r"\bbracket\s+([a-z0-9\s+\-*/.]+?)\s+bracket\b", r" ( \1 ) ", q)

        # 2. Verbal Operators Normalization
        q = re.sub(r"\bmultiplied\s+by\b", " * ", q)
        q = re.sub(r"\bdivided\s+by\b", " / ", q)
        q = re.sub(r"\bplus\b", " + ", q)
        q = re.sub(r"\bminus\b", " - ", q)
        q = re.sub(r"\binto\b", " * ", q)
        q = re.sub(r"\btimes\b", " * ", q)
        q = re.sub(r"\bover\b", " / ", q)
        q = re.sub(r"\b(?:is\s+equal\s+to|equals|equal\s+to|gives)\b", " = ", q)
        q = re.sub(r"\b(?:to\s+the\s+power\s+of|raised\s+to|power)\b", " ^ ", q)

        # 3. Spoken Digits / Common Number Words Normalization
        word_numbers = {
            r"\bzero\b": "0",
            r"\bone\b": "1",
            r"\btwo\b": "2",
            r"\bthree\b": "3",
            r"\bfour\b": "4",
            r"\bfive\b": "5",
            r"\bsix\b": "6",
            r"\bseven\b": "7",
            r"\beight\b": "8",
            r"\bnine\b": "9",
            r"\bten\b": "10"
        }
        for pattern, replacement in word_numbers.items():
            q = re.sub(pattern, replacement, q)

        # Powers shorthand
        q = re.sub(r"([a-z0-9.]+)\s+squared\b", r"\1 ^ 2", q)
        q = re.sub(r"([a-z0-9.]+)\s+cubed\b", r"\1 ^ 3", q)

        # Unicode symbols
        q = q.replace("×", " * ").replace("÷", " / ").replace("−", " - ").replace("–", " - ")

        # 4. Implicit Multiplication (e.g. 2x -> 2 * x, 45.2 x -> 45.2 * x, 3(x+1) -> 3 * (x+1))
        q = re.sub(r"(\d+(?:\.\d+)?)\s*([a-zA-Z])", r"\1 * \2", q)
        q = re.sub(r"(\d+(?:\.\d+)?)\s*\(", r"\1 * (", q)
        q = re.sub(r"\)\s*(\d+(?:\.\d+)?)", r") * \1", q)
        q = re.sub(r"\)\s*\(", r") * (", q)
        q = re.sub(r"\)\s*([a-zA-Z])", r") * \1", q)

        return re.sub(r"\s+", " ", q).strip()

    def evaluate(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Evaluate natural language mathematical query, linear equation, or quadratic equation.
        Returns Dict with result, spoken response, steps, and operation metadata.
        """
        norm_q = self.normalize_query(query)
        if not norm_q:
            return None

        # 1. Algebraic Equations (Linear ax + b = 0 & Quadratic ax^2 + bx + c = 0)
        if "=" in norm_q and any(c.isalpha() for c in norm_q):
            # Check quadratic first if powers or squared terms present, or general polynomial
            quad_res = self._solve_quadratic_equation(norm_q, original_query=query)
            if quad_res is not None:
                return quad_res
            eq_res = self._solve_linear_equation(norm_q, original_query=query)
            if eq_res is not None:
                return eq_res

        # 2. Multiplication Tables (e.g. "table of 7", "7 times table")
        table_match = self._match_table_query(norm_q)
        if table_match is not None:
            num = table_match
            table_lines = [f"{num} × {i} = {num * i}" for i in range(1, 11)]
            values_str = ", ".join(str(num * i) for i in range(1, 11))
            formatted_text = f"Table of {num}:\n" + "\n".join(table_lines)
            speech_text = f"The table of {num} is {values_str}."
            return {
                "operation": "table",
                "number": num,
                "table": table_lines,
                "text_response": speech_text,
                "formatted": formatted_text,
                "result": num * 10,
                "steps": [f"Multiply {num} sequentially from 1 to 10."]
            }

        # 3. Reciprocal Queries (e.g. "reciprocal of 5", "reciprocal of 8")
        recip_res = self._match_reciprocal(norm_q)
        if recip_res is not None:
            return recip_res

        # 4. Percentage Queries (e.g. "15% of 800", "increase 500 by 12%")
        pct_res = self._match_percentage_query(norm_q)
        if pct_res is not None:
            return pct_res

        # 5. Powers & Roots (e.g. "square root of 144", "cube root of 27", "2^10")
        power_root_res = self._match_powers_and_roots(norm_q)
        if power_root_res is not None:
            return power_root_res

        # 6. Fraction Arithmetic (e.g. "3/4 + 1/2")
        frac_res = self._match_fraction_arithmetic(norm_q)
        if frac_res is not None:
            return frac_res

        # 7. General Arithmetic with Parentheses & Order of Operations
        arith_res = self._match_arithmetic_expression(norm_q)
        if arith_res is not None:
            return arith_res

        return None

    def _solve_quadratic_equation(self, eq_str: str, original_query: str = "") -> Optional[Dict[str, Any]]:
        """
        Deterministically solves a single-variable quadratic equation: ax^2 + bx + c = 0
        Computes exact real or complex roots via quadratic formula (-b +- sqrt(D)) / (2a).
        Generates step-by-step mathematical breakdown and clean speech formatting (Zero LaTeX).
        """
        parts = eq_str.split("=")
        if len(parts) != 2:
            return None

        lhs_str, rhs_str = parts[0].strip(), parts[1].strip()
        var_chars = set(re.findall(r"[a-zA-Z]", eq_str))
        if len(var_chars) != 1:
            return None
        var_name = list(var_chars)[0]

        lhs_expr = lhs_str.replace("^", "**")
        rhs_expr = rhs_str.replace("^", "**")

        try:
            lhs_ast = ast.parse(lhs_expr, mode="eval")
            rhs_ast = ast.parse(rhs_expr, mode="eval")

            def eval_diff(x_val: float) -> float:
                v = {var_name: x_val}
                l = float(_safe_eval_ast_with_vars(lhs_ast, v))
                r = float(_safe_eval_ast_with_vars(rhs_ast, v))
                return l - r

            f0 = eval_diff(0.0)
            f1 = eval_diff(1.0)
            f_neg1 = eval_diff(-1.0)
            f2 = eval_diff(2.0)
            f_neg2 = eval_diff(-2.0)

            c = f0
            a = (f1 + f_neg1 - 2.0 * c) / 2.0
            b = (f1 - f_neg1) / 2.0

            # Quadratic / polynomial verification
            expected_f2 = 4.0 * a + 2.0 * b + c
            expected_f_neg2 = 4.0 * a - 2.0 * b + c
            if abs(f2 - expected_f2) > 1e-3 or abs(f_neg2 - expected_f_neg2) > 1e-3:
                return None  # Higher degree polynomial or non-polynomial

            # If a is near 0, this is a linear equation
            if abs(a) < 1e-6:
                return None  # Handled by _solve_linear_equation

            # Discriminant D = b^2 - 4ac
            disc = b * b - 4.0 * a * c

            def _fmt(val: float) -> str:
                if abs(val - round(val)) < 1e-8:
                    return str(int(round(val)))
                return f"{val:.4f}".rstrip("0").rstrip(".")

            steps = [
                f"Equation: {lhs_str} = {rhs_str}",
                f"Standard Form: {_fmt(a)}{var_name}^2 + {_fmt(b)}{var_name} + {_fmt(c)} = 0",
                f"Coefficients: a = {_fmt(a)}, b = {_fmt(b)}, c = {_fmt(c)}",
                f"Discriminant D = b^2 - 4ac = ({_fmt(b)})^2 - 4*({_fmt(a)})*({_fmt(c)}) = {_fmt(disc)}"
            ]

            if abs(disc) < 1e-9:
                root = -b / (2.0 * a)
                root_disp = _fmt(root)
                speech = f"The equation has a single repeated solution: {var_name} equals {root_disp}."
                steps.append(f"Repeated Root: {var_name} = -b / (2a) = {_fmt(-b)} / {_fmt(2*a)} = {root_disp}")
                return {
                    "operation": "quadratic_equation",
                    "variable": var_name,
                    "equation": eq_str,
                    "discriminant": disc,
                    "roots": [root],
                    "root_type": "repeated_real",
                    "solution_display": f"{var_name} = {root_disp}",
                    "text_response": speech,
                    "steps": steps
                }
            elif disc > 0:
                sqrt_d = math.sqrt(disc)
                r1 = (-b + sqrt_d) / (2.0 * a)
                r2 = (-b - sqrt_d) / (2.0 * a)
                if r1 > r2:
                    r1, r2 = r2, r1
                r1_disp = _fmt(r1)
                r2_disp = _fmt(r2)
                speech = f"The quadratic equation has two real solutions: {var_name} equals {r1_disp} and {var_name} equals {r2_disp}."
                steps.append(f"Apply Quadratic Formula: {var_name} = (-b ± √D) / (2a)")
                steps.append(f"Root 1: {var_name} = ({_fmt(-b)} + {_fmt(sqrt_d)}) / {_fmt(2*a)} = {r1_disp}")
                steps.append(f"Root 2: {var_name} = ({_fmt(-b)} - {_fmt(sqrt_d)}) / {_fmt(2*a)} = {r2_disp}")
                return {
                    "operation": "quadratic_equation",
                    "variable": var_name,
                    "equation": eq_str,
                    "discriminant": disc,
                    "roots": [r1, r2],
                    "root_type": "two_real",
                    "solution_display": f"{var_name} = {r1_disp}, {var_name} = {r2_disp}",
                    "text_response": speech,
                    "steps": steps
                }
            else:
                real_part = -b / (2.0 * a)
                imag_part = math.sqrt(-disc) / (2.0 * abs(a))
                real_disp = _fmt(real_part)
                imag_disp = _fmt(imag_part)
                speech = f"The equation has two complex solutions: {var_name} equals {real_disp} plus {imag_disp} i, and {var_name} equals {real_disp} minus {imag_disp} i."
                steps.append(f"Discriminant is negative (D = {_fmt(disc)}), giving complex roots.")
                steps.append(f"Root 1: {var_name} = {real_disp} + {imag_disp}i")
                steps.append(f"Root 2: {var_name} = {real_disp} - {imag_disp}i")
                return {
                    "operation": "quadratic_equation",
                    "variable": var_name,
                    "equation": eq_str,
                    "discriminant": disc,
                    "roots": [f"{real_disp} + {imag_disp}i", f"{real_disp} - {imag_disp}i"],
                    "root_type": "complex",
                    "solution_display": f"{var_name} = {real_disp} ± {imag_disp}i",
                    "text_response": speech,
                    "steps": steps
                }
        except Exception:
            return None

    def _solve_linear_equation(self, eq_str: str, original_query: str = "") -> Optional[Dict[str, Any]]:
        """
        Deterministically solves a single-variable linear equation (e.g. ax + b = cx + d).
        Computes exact fractional and decimal solution, verifies linearity, and outputs spoken steps.
        """
        parts = eq_str.split("=")
        if len(parts) != 2:
            return None

        lhs_str, rhs_str = parts[0].strip(), parts[1].strip()
        # Find variable name
        var_chars = set(re.findall(r"[a-zA-Z]", eq_str))
        if len(var_chars) != 1:
            return None
        var_name = list(var_chars)[0]

        # Prepare AST expressions
        lhs_expr = lhs_str.replace("^", "**")
        rhs_expr = rhs_str.replace("^", "**")

        try:
            lhs_ast = ast.parse(lhs_expr, mode="eval")
            rhs_ast = ast.parse(rhs_expr, mode="eval")

            def eval_diff(x_val: float) -> float:
                v = {var_name: x_val}
                l = float(_safe_eval_ast_with_vars(lhs_ast, v))
                r = float(_safe_eval_ast_with_vars(rhs_ast, v))
                return l - r

            # Check values at x=0, x=1, x=2 to derive linear coefficients f(x) = ax + b = 0
            f0 = eval_diff(0.0)
            f1 = eval_diff(1.0)
            f2 = eval_diff(2.0)

            # Linear check: slope must be constant
            a = f1 - f0
            b = f0
            if abs((f2 - f1) - a) > 1e-4:
                return None  # Non-linear equation

            if abs(a) < 1e-12:
                if abs(b) < 1e-12:
                    return {
                        "operation": "linear_equation",
                        "variable": var_name,
                        "equation": eq_str,
                        "text_response": f"The equation has infinitely many solutions.",
                        "steps": ["The expression is an identity valid for all real numbers."]
                    }
                else:
                    return {
                        "operation": "linear_equation",
                        "variable": var_name,
                        "equation": eq_str,
                        "text_response": f"The equation has no solution.",
                        "steps": ["The terms simplify to an inconsistent statement."]
                    }

            # Solve x = -b / a
            sol_val = -b / a
            sol_rounded = round(sol_val, 4)

            def _fmt(val: float) -> str:
                if abs(val - round(val)) < 1e-8:
                    return str(int(round(val)))
                return f"{val:.4f}".rstrip("0").rstrip(".")

            # Speech formatting (Zero LaTeX, clean numbers)
            if abs(sol_val - round(sol_val)) < 1e-8:
                sol_display = f"{int(round(sol_val))}"
                speech_ans = f"{var_name} equals {sol_display}."
            else:
                sol_display = f"{sol_val:.4f}".rstrip("0").rstrip(".") if abs(sol_val) < 1e6 else f"{sol_val:g}"
                speech_ans = f"{var_name} is approximately {sol_display}."

            steps = [
                f"Equation: {lhs_str} = {rhs_str}",
                f"Group variable terms: {_fmt(a)} * {var_name} = {_fmt(-b)}",
                f"Divide by coefficient: {var_name} = {_fmt(-b)} / {_fmt(a)}",
                f"Final solution: {var_name} = {sol_display}"
            ]

            return {
                "operation": "linear_equation",
                "variable": var_name,
                "equation": eq_str,
                "result": sol_val,
                "approx_result": sol_rounded,
                "solution_display": sol_display,
                "text_response": speech_ans,
                "steps": steps
            }
        except Exception:
            return None

    def _match_table_query(self, q: str) -> Optional[int]:
        patterns = [
            r"table\s+of\s+(\d+)",
            r"(\d+)\s+times\s+table",
            r"(\d+)\s*(?:\*\s*)?(?:ka|cha|ke)\s+table",
            r"table\s+(\d+)",
            r"(\d+)\s*(?:\*\s*)?ka\s+pahada"
        ]
        for p in patterns:
            m = re.search(p, q)
            if m:
                try:
                    num = int(m.group(1))
                    if 1 <= num <= 1000:
                        return num
                except Exception:
                    pass
        return None

    def _match_reciprocal(self, q: str) -> Optional[Dict[str, Any]]:
        # Reciprocal of X or 1/X
        recip_m = re.search(r"reciprocal\s+of\s+([\d,.]+)", q)
        if recip_m:
            val = float(recip_m.group(1).replace(",", ""))
            if val == 0:
                return {"operation": "reciprocal", "error": "Division by zero", "text_response": "Reciprocal of zero is undefined."}
            ans = 1.0 / val
            ans_fmt = f"{ans:g}"
            return {
                "operation": "reciprocal",
                "result": ans,
                "text_response": f"The reciprocal of {recip_m.group(1)} is {ans_fmt}.",
                "steps": [f"Compute 1 / {recip_m.group(1)} = {ans_fmt}"]
            }
        return None

    def _match_percentage_query(self, q: str) -> Optional[Dict[str, Any]]:
        # 1. "increase X by Y%" or "decrease X by Y%"
        inc_match = re.search(r"(increase|decrease)\s+([\d,.]+)\s*(?:\*\s*)?by\s+([\d,.]+)\s*(?:%|percent)", q)
        if inc_match:
            action, base_str, pct_str = inc_match.groups()
            base = float(base_str.replace(",", ""))
            pct = float(pct_str.replace(",", ""))
            delta = base * (pct / 100.0)
            final_val = base + delta if action == "increase" else base - delta
            final_fmt = f"{final_val:g}"
            return {
                "operation": "percentage_adjustment",
                "result": final_val,
                "text_response": f"{base_str} {action}d by {pct_str}% is {final_fmt}.",
                "steps": [
                    f"Calculate {pct_str}% of {base_str}: {delta:g}",
                    f"{'Add to' if action == 'increase' else 'Subtract from'} base value: {final_fmt}"
                ]
            }

        # 2. "X% of Y" or "X percent of Y"
        pct_patterns = [
            r"([\d,.]+)\s*(?:\*\s*)?(?:%|percent)\s+of\s+([\d,.]+)",
            r"([\d,.]+)\s*(?:\*?\s*ka|\*?\s*cha|\*?\s*ke)\s+([\d,.]+)\s*(?:%|percent)"
        ]
        for p in pct_patterns:
            m = re.search(p, q)
            if m:
                pct_val = float(m.group(1).replace(",", ""))
                base_val = float(m.group(2).replace(",", ""))
                ans = base_val * (pct_val / 100.0)
                ans_fmt = f"{ans:g}"
                return {
                    "operation": "percentage",
                    "result": ans,
                    "text_response": f"{pct_val:g}% of {base_val:g} is {ans_fmt}.",
                    "steps": [f"Multiply {base_val:g} by {pct_val:g} and divide by 100 to get {ans_fmt}."]
                }
        return None

    def _match_powers_and_roots(self, q: str) -> Optional[Dict[str, Any]]:
        # Cube root
        cbrt_m = re.search(r"(?:cube\s+root\s+of|cbrt)\s*\(?\s*([\d,.]+)\s*\)?", q)
        if cbrt_m:
            val = float(cbrt_m.group(1).replace(",", ""))
            ans = round(val ** (1.0 / 3.0), 6)
            if abs(ans - round(ans)) < 1e-5:
                ans = int(round(ans))
            ans_fmt = f"{ans:g}"
            return {
                "operation": "cube_root",
                "result": ans,
                "text_response": f"Cube root of {val:g} is {ans_fmt}.",
                "steps": [f"Compute principal cube root of {val:g} = {ans_fmt}"]
            }

        # Square root
        sqrt_m = re.search(r"(?:square\s+root\s+of|sqrt)\s*\(?\s*([\d,.]+)\s*\)?", q)
        if sqrt_m:
            val = float(sqrt_m.group(1).replace(",", ""))
            if val < 0:
                return {"operation": "sqrt", "error": "Negative root", "text_response": "Square root of a negative number is not a real number."}
            ans = math.isqrt(int(val)) if val.is_integer() and math.isqrt(int(val)) ** 2 == int(val) else math.sqrt(val)
            ans_fmt = f"{ans:g}"
            return {
                "operation": "square_root",
                "result": ans,
                "text_response": f"Square root of {val:g} is {ans_fmt}.",
                "steps": [f"Compute principal square root of {val:g} = {ans_fmt}"]
            }

        # Powers: "2^10" or "X ^ Y"
        pow_m = re.search(r"([\d,.]+)\s*\^\s*([\d,.]+)", q)
        if pow_m:
            base = float(pow_m.group(1).replace(",", ""))
            exp = float(pow_m.group(2).replace(",", ""))
            if abs(exp) > 1000 or abs(base) > 10000:
                return {"operation": "power", "error": "Overflow", "text_response": "Number is too large to calculate."}
            ans = base ** exp
            if ans.is_integer() and abs(ans) < 1e15:
                ans_fmt = str(int(ans))
            else:
                ans_fmt = f"{ans:g}"
            return {
                "operation": "power",
                "result": ans,
                "text_response": f"{base:g} to the power of {exp:g} is {ans_fmt}.",
                "steps": [f"Raise {base:g} to the exponent {exp:g} = {ans_fmt}"]
            }
        return None

    def _match_fraction_arithmetic(self, q: str) -> Optional[Dict[str, Any]]:
        frac_pattern = r"(\d+\s*/\s*\d+)\s*([+\-*x×/])\s*(\d+\s*/\s*\d+)"
        m = re.search(frac_pattern, q)
        if m:
            try:
                f1_str, op, f2_str = m.groups()
                f1 = Fraction(f1_str.replace(" ", ""))
                f2 = Fraction(f2_str.replace(" ", ""))
                if op == "+":
                    res = f1 + f2
                elif op == "-":
                    res = f1 - f2
                elif op in ["*", "x", "×"]:
                    res = f1 * f2
                elif op == "/":
                    if f2 == 0:
                        return {"operation": "fraction", "error": "Division by zero", "text_response": "Division by zero is undefined."}
                    res = f1 / f2
                else:
                    return None

                dec_val = float(res)
                dec_fmt = f"{dec_val:g}"
                text_ans = f"{f1_str} {op} {f2_str} is {res} or {dec_fmt}."
                return {
                    "operation": "fraction_arithmetic",
                    "result": dec_val,
                    "fraction_result": str(res),
                    "text_response": text_ans,
                    "steps": [f"Compute {f1} {op} {f2} = {res} ({dec_fmt})"]
                }
            except Exception:
                pass
        return None

    def _match_arithmetic_expression(self, q: str) -> Optional[Dict[str, Any]]:
        # Check if digits and operators are present
        if not re.search(r"\d", q) or not re.search(r"[+\-*/%^()]", q):
            return None

        # Sanitize allowed characters for AST evaluation
        if not re.fullmatch(r"[\d\s+\-*/%^().,]+", q):
            return None

        expr_str = q.replace("^", "**").replace(",", "")

        try:
            parsed_ast = ast.parse(expr_str, mode="eval")
            result = _safe_eval_ast_with_vars(parsed_ast, {})
            res_val = float(result)

            if res_val.is_integer() and abs(res_val) < 1e15:
                formatted_num = f"{int(res_val):,}"
            else:
                formatted_num = f"{res_val:g}"

            spoken_expr = q.replace("*", " times ").replace("/", " divided by ").replace("+", " plus ").replace("-", " minus ").replace("^", " to the power of ")
            spoken_expr = re.sub(r"\s+", " ", spoken_expr).strip()

            text_response = f"{spoken_expr} is {formatted_num}."

            return {
                "operation": "arithmetic",
                "expression": q,
                "result": res_val,
                "text_response": text_response,
                "steps": [f"Evaluate: {q} = {formatted_num}"]
            }
        except ZeroDivisionError:
            return {
                "operation": "arithmetic",
                "error": "Division by zero",
                "text_response": "Division by zero is undefined."
            }
        except Exception:
            return None


math_engine = DeterministicMathEngine()
