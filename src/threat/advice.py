ADVICE = {
    "Bank/KYC": (
        ["Call the number printed on your bank card", "Check KYC status in the official bank app"],
        ["Do not share OTP, PIN, CVV or Aadhaar/PAN numbers", "Do not install screen-sharing apps"],
    ),
    "Delivery": (
        ["Track using the official retailer or courier app", "Verify the domain before paying"],
        ["Do not pay a redelivery fee through an unknown link", "Do not share address or OTP"],
    ),
    "Government": (
        ["Open government websites by typing the official address yourself", "Use cybercrime.gov.in for official reporting"],
        ["Do not pay on a WhatsApp or SMS link", "Do not join video calls claiming to be police or CBI"],
    ),
    "UPI/Payment": (
        ["Use only your bank or UPI app for actual payments", "Remember: receiving money does not require a PIN"],
        ["Do not accept collect requests or scan QR codes to receive money", "Do not share UPI PIN"],
    ),
}
HELPLINES = ["1930", "cybercrime.gov.in", "Forward spam SMS to 1909"]


def get_advice(category: str):
    do, dont = ADVICE.get(category, (
        ["Verify the sender through an official website or app", "Call 1930 if money or data may be at risk"],
        ["Do not click unknown links", "Do not share OTP, PIN or passwords"],
    ))
    return {"do": do, "dont": dont, "helplines": HELPLINES}
