"""Explainable regex rules for Indian-context scam language."""
import re
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Rule:
    id: str
    label: str
    category: str
    weight: int
    patterns: tuple[str, ...]
    explanation: str
    negated_by_prefix: str = ""


RULES = (
    Rule("urgency", "Urgency pressure", "General", 12,
         (r"\b(immediately|urgent|right now|last chance|today only|jaldi|turant|aaj hi)\b",
          r"within\s+\d+\s+hours?", r"\btoday\b"), "Creates pressure to act without checking."),
    Rule("account_threat", "Account/SIM threat", "Bank/KYC", 18,
         (r"\baccount\b.{0,30}\b(block|blocked|suspend|suspended|closed|freeze)\b",
          r"\b(sim|card|upi)\b.{0,30}\b(block|blocked|suspend|suspended|closed)\b",
          r"band\s+ho\s+jayega"), "Claims an account or service may be blocked."),
    Rule("credential_request", "Sensitive credential request", "Bank/KYC", 30,
         (r"\b(share|send|enter|provide|confirm)\b.{0,20}\b(otp|pin|cvv|password|card number|aadhaar|pan|upi pin)\b",
          r"\b(otp|pin|cvv|password|card number|aadhaar|pan|upi pin)\b.{0,20}\b(share|send|enter)\b"),
         "Requests a secret that legitimate support should never ask for."),
    Rule("kyc_update", "KYC/PAN update request", "Bank/KYC", 22,
         (r"\b(kyc|pan|aadhaar)\b.{0,25}\b(update|expired|pending|verify|link)\b",
          r"\b(update|expired|pending|verify|link)\b.{0,25}\b(kyc|pan|aadhaar)\b"),
         "Pressures the user to update identity details."),
    Rule("prize", "Prize or lottery claim", "Lottery/Prize", 28,
         (r"\byou (have )?won\b", r"\blucky draw\b", r"\b(congratulations|badhai)\b.{0,30}\b(prize|reward|lottery|inaam)\b",
          r"\bclaim (your )?(prize|reward)\b"),
         "Uses a prize or reward lure."),
    Rule("advance_fee", "Advance fee request", "Other", 25,
         (r"\b(processing|customs|redelivery|registration|security)\b.{0,20}\b(fee|charges?|pay)\b",
          r"\b(pay|payment)\b.{0,20}(rs\.?|inr|to claim|to release|immediately|tonight)",
          r"\bsecurity fine\b",
          r"\bfee\b.{0,20}\b(claim|release)\b"),
         "Requests money before releasing a prize or delivery."),
    Rule("delivery", "Delivery hold or fee", "Delivery", 22,
         (r"\b(parcel|package|shipment|courier)\b.{0,30}\b(hold|stuck|undelivered|pending)\b",
          r"\b(address incomplete|confirm address|redelivery fee)\b"),
         "Uses a parcel or delivery problem to provoke payment."),
    Rule("utility", "Utility disconnection threat", "Electricity/Utility", 28,
         (r"\b(electricity|bijli)\b.{0,25}\b(bill|bills)\b.{0,25}\b(unpaid|pending|disconnect)\b",
          r"\belectricity.{0,20}(disconnect|cut off)\b",
          r"\bbijli\b.{0,30}\b(final notice|urgent message|office|fine|cut)\b",
          r"\b(electricity|bijli)\b.{0,25}\b(00000[- ]?00000|\d{10}|fine|fee)\b"),
         "Claims an electricity service will be disconnected."),
    Rule("government", "Government or tax impersonation", "Government", 20,
         (r"\b(income tax|itr refund|e-challan|traffic fine|pm kisan|subsidy|gst notice)\b",),
         "Impersonates a government or tax authority."),
    Rule("job", "Work-from-home job lure", "Job/Work-from-home", 28,
         (r"\b(work from home|ghar baithe)\b", r"\bearn (rs\.?|inr|\d+)\b.{0,20}\b(per day|daily)\b",
          r"\b(part.?time job|like and earn|hiring on telegram|no experience needed)\b"),
         "Promises easy earnings or a low-effort job."),
    Rule("investment", "Investment or guaranteed return lure", "Investment", 26,
         (r"\b(guaranteed returns?|double your money|stock tips?|crypto profit)\b",
          r"\bvip group\b", r"\b\d+% (per )?day\b"),
         "Promotes unrealistic investment profits."),
    Rule("upi", "UPI collect or QR request", "UPI/Payment", 35,
         (r"\b(collect request|accept request)\b", r"\bsent (it )?by mistake\b",
          r"\b(scan qr|return my money|qr.{0,20}scan|scan.{0,20}qr|return.{0,20}money)\b",
          r"\b(paise|money).{0,30}\b(return|bhejo|waapas)\b"),
         "Tries to trigger a UPI payment while posing as a refund."),
    Rule("digital_arrest", "Digital arrest threat", "Digital Arrest", 35,
         (r"\bdigital arrest\b", r"\b(arrest warrant|money laundering|narcotics parcel)\b",
          r"\bstay on (a )?video call\b", r"\bdo not tell anyone\b", r"\b(cbi|ncb) notice\b"),
         "Uses police or investigation fear to isolate the user."),
    Rule("apk", "Remote-access/APK request", "Other", 30,
         (r"\b(anydesk|teamviewer|quicksupport)\b", r"\b\.apk\b", r"\bdownload (the )?app from (a )?link\b"),
         "Requests installation or remote-access software."),
    Rule("relative", "Familiar-person impersonation", "Impersonation", 30,
         (r"\bhi mum\b.{0,30}\b(new number|lost my phone)\b",),
         "Pretends to be a relative from a new number."),
    Rule("money_request", "Direct money request", "Impersonation", 15,
         (r"\bsend me (money|rs\.?\s*\d+|inr\s*\d+)\b",
          r"\bmujhe\s+(?:rs\.?\s*)?\d+.{0,20}\b(bhejo|send)\b",
          r"\bsend\s+(?:me\s+)?(?:rs\.?\s*)?\d+\b",
          r"\b(salary|money|cash|payment)\b.{0,20}\b(advance|bhejo|send|transfer)\b"),
         "Asks the user to send money directly."),
    Rule("move_to_chat", "Move conversation to private chat", "Other", 18,
         (r"\b(join|contact|message)\b.{0,20}\b(telegram|whatsapp)\b",
          r"\bt\.me/[a-z0-9_]+\b"),
         "Moves the conversation away from a trusted platform."),
    Rule("call_number", "Mobile number call request", "Other", 12,
         (r"\b(call|whatsapp|contact)\b.{0,15}\b\d{10}\b",
          r"\b\d{10}\b.{0,15}\bpar call\b"),
         "Provides a mobile number for further contact."),
)

NEGATIVE_RULES = (
    Rule("otp_warning", "OTP sharing warning", "Safety", -25,
         (r"\b(do not|never|don't)\b.{0,20}\bshare\b.{0,20}\botp\b",
          r"\bbank\b.{0,20}\bnever\b.{0,20}\bask\b.{0,20}\botp\b"),
         "Explicitly warns against sharing an OTP."),
    Rule("txn_alert", "Legitimate transaction alert", "Bank/KYC", -12,
         (r"\b(debited|credited)\b.{0,30}\b(a/c|account|avl bal|available balance)\b",),
         "Resembles a bank transaction notification."),
    Rule("order_notice", "Legitimate order notice", "Delivery", -10,
         (r"\b(order)\b.{0,30}\b(shipped|delivered)\b",
          r"\b(parcel|package)\b.{0,20}\b(shipped|delivered)\b"),
         "Resembles an order status notification."),
    Rule("upi_warning", "UPI safety notice", "UPI/Payment", -30,
         (r"\bupi\b.{0,40}\b(no action|nahi hona|not required|reject|safe|PIN nahi)\b",
          r"\bcollect request ya qr\b.{0,30}\b(kuch nahi hona|not required|reject)\b"),
         "Explicitly explains that UPI collect requests or QR scans do not require action."),
    Rule("delivery_no_fee", "Delivery no-fee notice", "Delivery", -30,
         (r"\b(no redelivery fee|no extra (delivery|customs|duty) fee|no (fee|payment) is due)\b",),
         "States explicitly that no extra delivery payment is due."),
)


def find_rule_matches(text: str, rule: Rule) -> list[dict]:
    matches = []
    for pattern in rule.patterns:
        for match in re.finditer(pattern, text, re.I):
            matches.append({"start": match.start(), "end": match.end(), "text": text[match.start():match.end()]})
    unique = {(m["start"], m["end"]): m for m in matches}
    return list(unique.values())
