import ast
import math
import operator
import re
from fractions import Fraction
from typing import Optional, Dict, Any, Tuple, Union

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

def _safe_eval_ast(node: ast.AST) -> Union[int, float, Fraction]:
    """Recursively evaluate an AST expression safely without arbitrary code execution."""
    if isinstance(node, ast.Expression):
        return _safe_eval_ast(node.body)
    elif isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value)}")
    elif isinstance(node, ast.BinOp):
        left = _safe_eval_ast(node.left)
        right = _safe_eval_ast(node.right)
        op_type = type(node.op)
        if op_type not in _SAFE_OPERATORS:
            raise ValueError(f"Unsupported operator: {op_type}")
        if op_type in (ast.Div, ast.FloorDiv) and right == 0:
            raise ZeroDivisionError("Division by zero is undefined.")
        if op_type == ast.Pow and (abs(right) > 1000 or abs(left) > 10000):
            raise OverflowError("Exponentiation exceeds safe compute limit.")
        return _SAFE_OPERATORS[op_type](left, right)
    elif isinstance(node, ast.UnaryOp):
        operand = _safe_eval_ast(node.operand)
        op_type = type(node.op)
        if op_type not in _SAFE_OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type}")
        return _SAFE_OPERATORS[op_type](operand)
    else:
        raise ValueError(f"Unsupported AST node: {type(node)}")


class DeterministicMathEngine:
    """
    Authoritative, Safe Deterministic Math Engine for Smart Glasses Assistant.
    Bypasses LLMs entirely for arithmetic, tables, percentages, powers, roots, and fractions.
    """

    def evaluate(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Evaluate natural language mathematical query.
        Returns Dict with `result`, `text_response`, `operation` if recognized, else None.
        """
        q = query.strip().lower()
        if not q:
            return None

        # 1. Multiplication Table Queries
        table_match = self._match_table_query(q)
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
                "result": num * 10
            }

        # 2. Percentage Queries (e.g., "15% of 800", "increase 500 by 12%", "decrease 200 by 10%")
        pct_res = self._match_percentage_query(q)
        if pct_res is not None:
            return pct_res

        # 3. Reciprocal Queries (e.g., "reciprocal of 5", "reciprocal of 8", "reciprocal of 2.5")
        recip_res = self._match_reciprocal_query(q)
        if recip_res is not None:
            return recip_res

        # 4. Powers & Roots (e.g., "square root of 144", "sqrt 144", "cube root of 27", "2 squared", "5 cubed", "2^10")
        power_root_res = self._match_powers_and_roots(q)
        if power_root_res is not None:
            return power_root_res

        # 5. Fraction Arithmetic (e.g., "3/4 + 1/2", "2/3 * 3/4")
        frac_res = self._match_fraction_arithmetic(q)
        if frac_res is not None:
            return frac_res

        # 6. General Arithmetic (e.g., "27 × 38", "125 multiplied by 16", "144 / 12", "25 + 37", "100 - 43", "kitna hota hai")
        arith_res = self._match_arithmetic_expression(q)
        if arith_res is not None:
            return arith_res

        return None

    def _match_table_query(self, q: str) -> Optional[int]:
        # Examples: "table of 7", "7 times table", "table of 12", "7 ka table", "7 cha table", "table 9"
        patterns = [
            r"table\s+of\s+(\d+)",
            r"(\d+)\s+times\s+table",
            r"(\d+)\s*(?:ka|cha|ke)\s+table",
            r"table\s+(\d+)",
            r"(\d+)\s+ka\s+pahada"
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

    def _match_percentage_query(self, q: str) -> Optional[Dict[str, Any]]:
        # 1. "increase X by Y%" or "decrease X by Y%"
        inc_match = re.search(r"(increase|decrease)\s+([\d,.]+)\s+by\s+([\d,.]+)\s*%", q)
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
                "text_response": f"{base_str} {action}d by {pct_str}% is {final_fmt}."
            }

        # 2. "X% of Y" or "X percent of Y" or "Y ka X%"
        pct_patterns = [
            r"([\d,.]+)\s*(?:%|percent)\s+of\s+([\d,.]+)",
            r"([\d,.]+)\s+ka\s+([\d,.]+)\s*(?:%|percent)"
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
                    "text_response": f"{pct_val:g}% of {base_val:g} is {ans_fmt}."
                }
        return None

    def _match_reciprocal_query(self, q: str) -> Optional[Dict[str, Any]]:
        # "reciprocal of 5", "reciprocal of 2.5", "1/8"
        m = re.search(r"reciprocal\s+of\s+([\d,.]+)", q)
        if m:
            val = float(m.group(1).replace(",", ""))
            if val == 0:
                return {"operation": "reciprocal", "error": "Division by zero", "text_response": "The reciprocal of zero is undefined."}
            ans = 1.0 / val
            return {
                "operation": "reciprocal",
                "result": ans,
                "text_response": f"The reciprocal of {val:g} is {ans:g}."
            }

        # standalone fraction like "1/8" or "1 / 8"
        frac_m = re.fullmatch(r"1\s*/\s*([\d,.]+)", q)
        if frac_m:
            val = float(frac_m.group(1).replace(",", ""))
            if val == 0:
                return {"operation": "reciprocal", "error": "Division by zero", "text_response": "1 divided by zero is undefined."}
            ans = 1.0 / val
            return {
                "operation": "reciprocal",
                "result": ans,
                "text_response": f"1 divided by {val:g} is {ans:g}."
            }
        return None

    def _match_powers_and_roots(self, q: str) -> Optional[Dict[str, Any]]:
        # 1. Square root: "square root of 144", "sqrt 144", "sqrt(144)"
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
                "text_response": f"Square root of {val:g} is {ans_fmt}."
            }

        # 2. Cube root: "cube root of 27", "cbrt 27"
        cbrt_m = re.search(r"(?:cube\s+root\s+of|cbrt)\s*\(?\s*([\d,.]+)\s*\)?", q)
        if cbrt_m:
            val = float(cbrt_m.group(1).replace(",", ""))
            ans = math.cbrt(val) if hasattr(math, "cbrt") else (val ** (1.0 / 3.0))
            if round(ans) ** 3 == int(val):
                ans = round(ans)
            ans_fmt = f"{ans:g}"
            return {
                "operation": "cube_root",
                "result": ans,
                "text_response": f"Cube root of {val:g} is {ans_fmt}."
            }

        # 3. Squared: "X squared"
        sq_m = re.search(r"([\d,.]+)\s+squared", q)
        if sq_m:
            val = float(sq_m.group(1).replace(",", ""))
            ans = val ** 2
            ans_fmt = f"{ans:g}"
            return {
                "operation": "square",
                "result": ans,
                "text_response": f"{val:g} squared is {ans_fmt}."
            }

        # 4. Cubed: "X cubed"
        cb_m = re.search(r"([\d,.]+)\s+cubed", q)
        if cb_m:
            val = float(cb_m.group(1).replace(",", ""))
            ans = val ** 3
            ans_fmt = f"{ans:g}"
            return {
                "operation": "cube",
                "result": ans,
                "text_response": f"{val:g} cubed is {ans_fmt}."
            }

        # 5. Powers: "2^10", "2 raised to 10", "2 to the power 10", "2 to the power of 10"
        pow_m = re.search(r"([\d,.]+)\s*(?:\^|\*\*|\braised\s+to\s+(?:the\s+power\s+(?:of\s+)?)?|\bto\s+the\s+power\s+(?:of\s+)?)\s*([\d,.]+)", q)
        if pow_m:
            base = float(pow_m.group(1).replace(",", ""))
            exp = float(pow_m.group(2).replace(",", ""))
            if abs(exp) > 1000 or abs(base) > 10000:
                return {"operation": "power", "error": "Overflow", "text_response": "Number is too large to calculate."}
            ans = base ** exp
            ans_fmt = f"{ans:g}"
            return {
                "operation": "power",
                "result": ans,
                "text_response": f"{base:g} to the power of {exp:g} is {ans_fmt}."
            }
        return None

    def _match_fraction_arithmetic(self, q: str) -> Optional[Dict[str, Any]]:
        # Match fractions like "3/4 + 1/2" or "1/3 * 2/5"
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
                text_ans = f"{f1_str} {op} {f2_str} is {res} (or {dec_val:g})."
                return {
                    "operation": "fraction_arithmetic",
                    "result": dec_val,
                    "fraction_result": str(res),
                    "text_response": text_ans
                }
            except Exception:
                pass
        return None

    def _match_arithmetic_expression(self, q: str) -> Optional[Dict[str, Any]]:
        # Clean query of common natural language filler and Hinglish math prefixes
        # e.g. "what is 27 × 38", "calculate 125 multiplied by 16", "27 into 38 kitna hota hai", "bhai 100 - 43 kitna hoga"
        cleaned = q.strip()
        cleaned = re.sub(r"^(?:what\s+is|what\'s|calculate|compute|solve|eval|bhai|batao|kya\s+hai)\s+", "", cleaned)
        cleaned = re.sub(r"(?:\s+(?:kitna\s+hota\s+hai|kitna\s+hoga|kitna\s+hai|batao|please))?[\s\?\.!]*$", "", cleaned)

        # Map verbal operator words to symbols
        cleaned = re.sub(r"\bmultiplied\s+by\b", "*", cleaned)
        cleaned = re.sub(r"\bdivided\s+by\b", "/", cleaned)
        cleaned = re.sub(r"\bplus\b", "+", cleaned)
        cleaned = re.sub(r"\bminus\b", "-", cleaned)
        cleaned = re.sub(r"\binto\b", "*", cleaned)
        cleaned = re.sub(r"\btimes\b", "*", cleaned)
        cleaned = cleaned.replace("×", "*").replace("÷", "/")

        # Match arithmetic structure containing digits and operator
        if not re.search(r"\d", cleaned) or not re.search(r"[+\-*/%^]", cleaned):
            return None

        # Sanitize allowed characters for AST parsing
        if not re.fullmatch(r"[\d\s+\-*/%^().,]+", cleaned):
            return None

        expr_str = cleaned.replace("^", "**").replace(",", "")

        try:
            parsed_ast = ast.parse(expr_str, mode="eval")
            result = _safe_eval_ast(parsed_ast)
            res_val = float(result) if isinstance(result, (int, float, Fraction)) else float(result)

            # Format result nicely
            if res_val.is_integer() and abs(res_val) < 1e15:
                formatted_num = f"{int(res_val):,}"
                ans_str = f"{int(res_val)}"
            else:
                formatted_num = f"{res_val:g}"
                ans_str = f"{res_val:g}"

            # Make human-friendly verbal response
            spoken_expr = expr_str.replace("**", " to the power of ").replace("*", " times ").replace("/", " divided by ").replace("+", " plus ").replace("-", " minus ")
            spoken_expr = re.sub(r"\s+", " ", spoken_expr).strip()

            text_response = f"{spoken_expr} is {formatted_num}."

            return {
                "operation": "arithmetic",
                "expression": expr_str,
                "result": res_val,
                "text_response": text_response
            }
        except ZeroDivisionError:
            return {
                "operation": "arithmetic",
                "error": "Division by zero",
                "text_response": "Division by zero is undefined."
            }
        except (OverflowError, ValueError):
            return None
        except Exception:
            return None

math_engine = DeterministicMathEngine()
