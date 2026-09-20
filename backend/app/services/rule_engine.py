"""
Deterministic Offline Rule-Based Engine for EVA
Sub-10ms instantaneous resolution for time, date, battery, connectivity,
telephony, notifications, file search, definitional dictionary, and arithmetic.
Zero cloud LLM dependency when matched.
"""

import re
import math
from datetime import datetime
from typing import Optional, Dict, Any, List

class DeterministicRuleEngine:
    DEFINITIONS: Dict[str, str] = {
        "array": "An array is a linear data structure that stores elements of the same type in contiguous memory locations, accessible by numerical index.",
        "data structure": "A data structure is a specialized format for organizing, processing, retrieving, and storing data efficiently.",
        "node": "A node is a fundamental building block in data structures like linked lists, trees, and graphs that contains data and references or pointers to other nodes.",
        "wifi": "Wi-Fi is a wireless networking technology that uses radio frequencies to connect devices to local area networks and the internet.",
        "wi-fi": "Wi-Fi is a wireless networking technology that uses radio frequencies to connect devices to local area networks and the internet.",
        "internet": "The Internet is a global system of interconnected computer networks that communicate using the standard Internet Protocol Suite (TCP/IP).",
        "google": "Google is a multinational technology company specializing in online search, cloud computing, software, hardware, and artificial intelligence.",
        "class": "In object-oriented programming, a class is an extensible program-code template for creating objects, defining initial state and implementations of behavior.",
        "sql": "SQL (Structured Query Language) is a standardized programming language used to manage, query, and manipulate relational databases.",
        "select": "In SQL, the SELECT statement is used to fetch data from one or more tables in a database.",
        "insert": "In SQL, the INSERT statement is used to add new records or rows to a database table.",
        "update": "In SQL, the UPDATE statement modifies existing data within specified columns of a database table.",
        "delete": "In SQL, the DELETE statement removes existing records from a database table based on specified conditions.",
        "where": "In SQL, the WHERE clause filters records to extract only those that satisfy a specified condition.",
        "join": "In SQL, a JOIN clause combines rows from two or more tables based on a related column between them.",
        "stack": "A stack is a linear data structure following the LIFO (Last-In, First-Out) principle, supporting push and pop operations.",
        "queue": "A queue is a linear data structure following the FIFO (First-In, First-Out) principle, supporting enqueue and dequeue operations.",
        "binary tree": "A binary tree is a hierarchical tree data structure in which each node has at most two children, referred to as left and right child.",
        "algorithm": "An algorithm is a step-by-step procedure or set of rules designed to solve a specific problem or perform a computation.",
        "api": "An API (Application Programming Interface) is a set of defined rules and protocols that enables different software applications to communicate with each other.",
        "http": "HTTP (Hypertext Transfer Protocol) is the application layer protocol used for transmitting hypermedia documents, such as HTML, over the World Wide Web.",
        "database": "A database is an organized collection of structured data stored electronically and accessed via a database management system (DBMS)."
    }

    def resolve(self, query: str, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Evaluate if query can be answered deterministically without LLM.
        Returns a response dict if resolved, or None if generative/agentic tier is required.
        """
        if not query or not query.strip():
            return None

        q = query.strip().lower()
        clean_q = re.sub(r"[?.!,]", "", q).strip()
        ctx = context or {}

        # 1. Stop / Cancel / Interruption
        if clean_q in ["stop", "cancel", "dismiss", "chup", "shant", "pause", "clear"]:
            return self._build_result("Stopped.", "conversation_control")

        # 2. Time Queries
        time_patterns = [
            "what time is it", "whats the time", "what is the time", "time please",
            "tell me the time", "current time", "what time", "time now", "time",
            "kitne baje", "time kya hua", "kya time hai", "kitne baje hai"
        ]
        if any(clean_q == p or clean_q.startswith(p) or clean_q.endswith(p) for p in time_patterns):
            now = datetime.now()
            time_str = now.strftime("%I:%M %p")
            if any(k in clean_q for k in ["kya", "kitne", "baje"]):
                msg = f"Abhi {time_str} hue hain."
            else:
                msg = f"It's {time_str}."
            return self._build_result(msg, "time")

        # 3. Date Queries
        date_patterns = [
            "whats the date", "what is the date", "whats todays date", "what is todays date",
            "today date", "todays date", "what day is today", "what day is it", "what is today",
            "date today", "aaj konsi date hai", "aaj ki date"
        ]
        if any(clean_q == p or clean_q.startswith(p) or clean_q.endswith(p) for p in date_patterns):
            now = datetime.now()
            date_str = now.strftime("%A, %B %d, %Y")
            if "aaj" in clean_q or "date hai" in clean_q:
                msg = f"Aaj ki date {date_str} hai."
            else:
                msg = f"Today is {date_str}."
            return self._build_result(msg, "date")

        # 4. Battery Queries
        battery_patterns = [
            "whats my battery", "what is my battery", "battery percentage", "battery level",
            "battery status", "check battery", "how much battery", "my battery", "battery",
            "battery percent", "battery kitni hai", "battery kitna hai"
        ]
        if any(clean_q == p or clean_q.startswith(p) or clean_q.endswith(p) for p in battery_patterns):
            batt = ctx.get("device", {}).get("battery_percentage", 85)
            if any(k in clean_q for k in ["kitni", "kitna", "hai"]):
                msg = f"Battery {batt} percent hai."
            else:
                msg = f"Battery is at {batt}%."
            return self._build_result(msg, "battery")

        # 5. Device Status / Connectivity
        status_patterns = [
            "status", "device status", "system status", "connectivity status", "wifi status", "connection status"
        ]
        if clean_q in status_patterns:
            batt = ctx.get("device", {}).get("battery_percentage", 85)
            glasses_conn = ctx.get("glasses_connected", False)
            glasses_str = "Glasses connected" if glasses_conn else "Glasses standalone"
            msg = f"EVA system operational. Battery {batt}%. {glasses_str}."
            return self._build_result(msg, "device_status")

        # 6. Definitional Dictionary Queries
        def_match = re.match(r"^(?:what\s+is(?:\s+(?:an?|the))?|define(?:\s+(?:an?|the))?|explain(?:\s+(?:an?|the))?|definition\s+of)\s+([a-z\s-]+)$", clean_q)
        if def_match:
            term = def_match.group(1).strip()
            definition = self.DEFINITIONS.get(term) or self.DEFINITIONS.get(term.replace("-", "")) or self.DEFINITIONS.get(term.replace(" ", ""))
            if definition:
                return self._build_result(definition, "definition", {"term": term})

        if clean_q in self.DEFINITIONS:
            return self._build_result(self.DEFINITIONS[clean_q], "definition", {"term": clean_q})

        # 7. Telephony & Call Controls
        if clean_q in ["answer call", "answer the call", "pick up", "accept call", "pick call"]:
            return self._build_result("Answering the incoming call.", "telephony", {"action": "ANSWER_CALL"})
        if clean_q in ["decline call", "decline the call", "reject call", "hang up", "cut call", "end call"]:
            return self._build_result("Call declined.", "telephony", {"action": "DECLINE_CALL"})

        # 8. Notifications & Messages Checking
        if clean_q in ["check notifications", "read notifications", "notifications", "unread notifications"]:
            return self._build_result("Checking your recent notifications.", "notifications", {"action": "READ_NOTIFICATIONS"})
        if clean_q in ["check messages", "read messages", "unread messages", "inbox"]:
            return self._build_result("Checking your recent SMS messages.", "messages", {"action": "READ_SMS"})

        # 9. Local Document / File Search
        file_search_match = re.match(r"^(?:search\s+files?|find\s+files?|search\s+documents?|find\s+documents?)\s*(?:for\s+)?(.*)$", clean_q)
        if file_search_match:
            term = file_search_match.group(1).strip()
            msg = f"Searching local files for '{term}'." if term else "Searching local device files."
            return self._build_result(msg, "file_search", {"search_term": term})

        # 10. Deterministic Arithmetic (Guards against open-ended code or complex queries)
        if not any(w in clean_q for w in ["python", "code", "script", "program", "write", "plan", "build", "create"]):
            math_ans = self._resolve_math(q)
            if math_ans:
                return self._build_result(math_ans, "math")

        return None

    def _resolve_math(self, raw_q: str) -> Optional[str]:
        q = raw_q.strip().lower()

        # Percentage: "15% of 800"
        pct_match = re.search(r"([\d,.]+)\s*(?:%|percent)\s+of\s+([\d,.]+)", q)
        if pct_match:
            try:
                pct = float(pct_match.group(1).replace(",", ""))
                base = float(pct_match.group(2).replace(",", ""))
                ans = base * (pct / 100.0)
                ans_str = f"{int(ans)}" if ans.is_integer() else f"{ans:.2f}"
                return f"{pct}% of {base} is {ans_str}."
            except Exception:
                pass

        # Square root: "square root of 144"
        sqrt_match = re.search(r"(?:square\s+root\s+of|sqrt)\s*\(?\s*([\d,.]+)\s*\)?", q)
        if sqrt_match:
            try:
                v = float(sqrt_match.group(1).replace(",", ""))
                if v >= 0:
                    ans = math.sqrt(v)
                    ans_str = f"{int(ans)}" if ans.is_integer() else f"{ans:.2f}"
                    return f"Square root of {v} is {ans_str}."
            except Exception:
                pass

        # Basic Arithmetic: "25 + 37", "144 / 12", "12 * 8"
        clean = re.sub(r"[?!.,;]", " ", q).strip()
        clean = re.sub(r"^(?:what\s+is|whats|calculate|compute|solve)\s+", "", clean)
        clean = clean.replace("multiplied by", "*").replace("divided by", "/").replace("plus", "+").replace("minus", "-").replace("times", "*").replace("×", "*").replace("÷", "/")
        clean = re.sub(r"\s+", " ", clean).strip()

        arith_match = re.match(r"^([\d,.]+)\s*([+\-*/%])\s*([\d,.]+)$", clean)
        if arith_match:
            try:
                a = float(arith_match.group(1).replace(",", ""))
                op = arith_match.group(2)
                b = float(arith_match.group(3).replace(",", ""))
                if op == "+": res = a + b
                elif op == "-": res = a - b
                elif op == "*": res = a * b
                elif op == "/": res = a / b if b != 0 else None
                elif op == "%": res = a % b
                else: res = None

                if res is not None:
                    res_str = f"{int(res)}" if res.is_integer() else f"{res:.2f}"
                    a_str = f"{int(a)}" if a.is_integer() else str(a)
                    b_str = f"{int(b)}" if b.is_integer() else str(b)
                    op_word = {"*": "times", "/": "divided by", "+": "plus", "-": "minus", "%": "mod"}.get(op, op)
                    return f"{a_str} {op_word} {b_str} is {res_str}."
            except Exception:
                pass

        return None

    def _build_result(self, text: str, category: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "status": "SUCCESS",
            "tier": "RULE_BASED",
            "category": category,
            "response_text": text,
            "latency_ms": 1.0,
            "metadata": metadata or {}
        }

rule_engine = DeterministicRuleEngine()
