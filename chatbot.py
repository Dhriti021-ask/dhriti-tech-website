#!/usr/bin/env python3
"""
Customer support chatbot for banking and other industries.

Features:
- Intent classification (rule-based, easy to customize)
- Industry-aware responses (banking + generic)
- Escalation workflow with ticket generation
- CLI chat loop

Run:
    python chatbot.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
import random
import re
from typing import Dict, List, Optional, Tuple


@dataclass
class Ticket:
    ticket_id: str
    created_at: str
    user_message: str
    reason: str
    metadata: Dict[str, str] = field(default_factory=dict)


class SupportChatbot:
    """A simple AI-like support chatbot with intent routing."""

    def __init__(self, industry: str = "banking") -> None:
        self.industry = industry.lower().strip()
        self.context: Dict[str, str] = {}
        self.tickets: List[Ticket] = []

        self.intents: Dict[str, List[str]] = {
            "greeting": ["hi", "hello", "hey", "good morning", "good evening"],
            "balance_inquiry": ["balance", "account balance", "how much money", "available funds"],
            "card_issue": ["card blocked", "card not working", "lost card", "stolen card", "freeze card"],
            "fraud": ["fraud", "unauthorized", "suspicious transaction", "scam", "charge i did not make"],
            "loan": ["loan", "emi", "interest rate", "mortgage", "personal loan"],
            "password_reset": ["reset password", "forgot password", "cant login", "can't login", "login issue"],
            "complaint": ["complaint", "unhappy", "not satisfied", "poor service"],
            "human_agent": ["human", "agent", "representative", "talk to person", "escalate"],
            "thanks": ["thanks", "thank you", "great", "helpful"],
        }

        self.faq: Dict[str, str] = {
            "working_hours": "Our support team is available 24/7 for critical issues and 8 AM - 8 PM for general queries.",
            "kyc": "To complete KYC, upload your government ID and proof of address in the mobile/web app.",
            "international_transfer": "International transfers may take 1-3 business days depending on destination bank and compliance checks.",
        }

    def _normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.lower()).strip()

    def classify_intent(self, message: str) -> str:
        normalized = self._normalize(message)
        scores: Dict[str, int] = {}

        for intent, keywords in self.intents.items():
            score = 0
            for kw in keywords:
                if kw in normalized:
                    score += len(kw)
            if score:
                scores[intent] = score

        if not scores:
            # lightweight FAQ matching
            if any(word in normalized for word in ["hour", "open", "timing"]):
                return "faq_working_hours"
            if "kyc" in normalized:
                return "faq_kyc"
            if "international" in normalized and "transfer" in normalized:
                return "faq_international_transfer"
            return "fallback"

        return max(scores, key=scores.get)

    def _generate_ticket(self, message: str, reason: str) -> Ticket:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        suffix = random.randint(100, 999)
        ticket_id = f"TKT-{timestamp}-{suffix}"
        ticket = Ticket(
            ticket_id=ticket_id,
            created_at=datetime.utcnow().isoformat() + "Z",
            user_message=message,
            reason=reason,
            metadata={"industry": self.industry},
        )
        self.tickets.append(ticket)
        return ticket

    def _handle_banking(self, intent: str, message: str) -> str:
        if intent == "balance_inquiry":
            return (
                "For security, I can’t display live balances in this demo. "
                "In production, I would verify identity (OTP/2FA) and fetch your balance securely."
            )

        if intent == "card_issue":
            return (
                "I can help with that. Please open your app and use 'Cards → Freeze card' immediately. "
                "If the card is lost/stolen, type 'escalate' and I’ll create a high-priority ticket."
            )

        if intent == "fraud":
            ticket = self._generate_ticket(message, "Potential fraud report")
            return (
                "I’m sorry this happened. I’ve created an urgent fraud ticket: "
                f"{ticket.ticket_id}. Please temporarily lock your card and review recent transactions."
            )

        if intent == "loan":
            return (
                "Sure — I can help with loans. Please share loan type (personal/home/auto), "
                "approximate amount, and tenure preference."
            )

        if intent == "password_reset":
            return (
                "You can reset your password from the login page using 'Forgot Password'. "
                "For security, never share OTP, PIN, or passwords with anyone."
            )

        return "I can support banking queries like cards, fraud, loans, login, and account help."

    def _handle_generic_industry(self, intent: str, message: str) -> str:
        if intent in {"complaint", "human_agent"}:
            ticket = self._generate_ticket(message, "Customer requested human assistance")
            return f"I’ve created support ticket {ticket.ticket_id}. A specialist will contact you soon."

        if intent == "password_reset":
            return "Please use the 'Forgot Password' option on the sign-in page."

        return "I can help with account access, complaints, and service guidance."

    def respond(self, message: str) -> str:
        normalized = self._normalize(message)

        if normalized in {"exit", "quit", "bye"}:
            return "Thank you for contacting support. Have a safe day!"

        if normalized in {"escalate", "human", "agent"}:
            ticket = self._generate_ticket(message, "User requested escalation")
            return f"Escalation confirmed. Your ticket ID is {ticket.ticket_id}."

        intent = self.classify_intent(message)

        if intent == "greeting":
            return "Hello! I’m your virtual support assistant. How can I help you today?"
        if intent == "thanks":
            return "You’re welcome! If you need anything else, I’m here to help."
        if intent == "complaint":
            ticket = self._generate_ticket(message, "Complaint lodged")
            return f"I’m sorry for the inconvenience. I’ve logged complaint ticket {ticket.ticket_id}."
        if intent == "human_agent":
            ticket = self._generate_ticket(message, "Requested live agent")
            return f"Sure. I’ve escalated this to a live agent under ticket {ticket.ticket_id}."

        if intent.startswith("faq_"):
            faq_key = intent.replace("faq_", "")
            return self.faq.get(faq_key, "I can help you with that. Could you share more details?")

        if self.industry == "banking":
            response = self._handle_banking(intent, message)
        else:
            response = self._handle_generic_industry(intent, message)

        if intent == "fallback":
            ticket = self._generate_ticket(message, "Low confidence response")
            return (
                "I want to make sure you get accurate help. "
                f"I’ve created ticket {ticket.ticket_id} and a support specialist will follow up."
            )

        return response

    def export_tickets(self, filepath: str = "tickets.json") -> None:
        data = [ticket.__dict__ for ticket in self.tickets]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


def run_cli() -> None:
    print("=== Customer Support Chatbot ===")
    industry = input("Choose industry (banking/general) [banking]: ").strip() or "banking"

    bot = SupportChatbot(industry=industry)
    print("Type 'exit' to quit.\n")

    while True:
        user_text = input("You: ").strip()
        if not user_text:
            continue

        reply = bot.respond(user_text)
        print(f"Bot: {reply}")

        if bot._normalize(user_text) in {"exit", "quit", "bye"}:
            if bot.tickets:
                bot.export_tickets()
                print("\nSaved generated tickets to tickets.json")
            break


if __name__ == "__main__":
    run_cli()
