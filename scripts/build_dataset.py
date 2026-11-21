import csv
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)


SCAM_TEMPLATES = [
    ("Bank/KYC", "sms", "Account blocked, update KYC immediately and share OTP."),
    ("Bank/KYC", "sms", "Aapka account band ho jayega, turant KYC verify karein."),
    ("Delivery", "sms", "Parcel on hold. Confirm address and pay the redelivery fee."),
    ("Delivery", "whatsapp", "Courier package stuck. Aapka address update karo aur fee pay karo."),
    ("Government", "sms", "Income tax refund pending. Verify PAN and Aadhaar immediately."),
    ("Government", "whatsapp", "Income tax notice mila hai. Turant PAN link karein."),
    ("Lottery/Prize", "sms", "Congratulations, you won a lucky draw prize. Pay a claim fee."),
    ("Lottery/Prize", "sms", "Inaam jeete hain. Claim reward ke liye security fee bhejein."),
    ("Job/Work-from-home", "whatsapp", "Work from home and earn Rs <num> daily. Join Telegram."),
    ("Job/Work-from-home", "whatsapp", "Ghar baithe videos like karke paise kamaayein. Registration fee pay karein."),
    ("UPI/Payment", "sms", "UPI collect request received. Accept to receive money."),
    ("UPI/Payment", "whatsapp", "Galti se paise aa gaye. QR scan karke return karein aur PIN mat banaayein."),
    ("Electricity/Utility", "sms", "Electricity bill pending. Connection will disconnect tonight."),
    ("Electricity/Utility", "sms", "Bijli bill unpaid hai. Aaj raat connection cut ho jayega."),
    ("Investment", "whatsapp", "Guaranteed returns, double money in 30 days. Join VIP group."),
    ("Investment", "whatsapp", "Stock tips aur crypto profit ke liye VIP group join karein."),
    ("Digital Arrest", "whatsapp", "You are under digital arrest. Stay on video call and do not tell anyone."),
    ("Digital Arrest", "whatsapp", "CBI notice mila hai. Digital arrest se bachne ke liye turant call karein."),
    ("Impersonation", "sms", "Hi Mum, new number. Please send me money urgently."),
    ("Impersonation", "whatsapp", "Hi, this is my new number. Mujhe Rs <num> bhejo."),
]


GENUINE_TEMPLATES = [
    ("Bank/KYC", "sms", "Do not share this OTP. Your bank never asks for it."),
    ("Bank/KYC", "sms", "Rs <num> debited from account. Available balance is Rs <num>."),
    ("Delivery", "sms", "Your order has been shipped and will arrive tomorrow."),
    ("Delivery", "whatsapp", "Package delivered successfully. Track the update in the official app."),
    ("Government", "sms", "Income tax acknowledgement received. No payment is required."),
    ("Government", "sms", "Traffic challan can be checked on the official government portal."),
    ("Lottery/Prize", "sms", "This is not a prize message. No fee or reward claim is pending."),
    ("Lottery/Prize", "whatsapp", "Normal family chat: did you receive the anniversary gift?"),
    ("Job/Work-from-home", "whatsapp", "Interview confirmed for Tuesday. The employer will not ask for a fee."),
    ("Job/Work-from-home", "sms", "Interview location and time are confirmed. Bring your resume."),
    ("UPI/Payment", "sms", "UPI payment successful. You do not need to share your PIN."),
    ("UPI/Payment", "whatsapp", "Money received in bank account. No action is required."),
    ("Electricity/Utility", "sms", "Your electricity bill is due on the printed due date."),
    ("Electricity/Utility", "sms", "Bijli bill payment reminder. Pay through the official electricity app."),
    ("Investment", "sms", "Investment account update. Review returns in the official app."),
    ("Investment", "whatsapp", "Please discuss investments with a registered adviser."),
    ("Digital Arrest", "sms", "No official agency asks for payment or secrecy during a video call."),
    ("Digital Arrest", "whatsapp", "Lunch tomorrow? I have a normal meeting after office."),
    ("Impersonation", "sms", "Call me tomorrow from the number saved in your contacts."),
    ("Impersonation", "whatsapp", "Hi, are we meeting at 6 pm? Please reply here."),
]


def build_rows():
    rows = []
    for index in range(110):
        category, channel, template = SCAM_TEMPLATES[index % len(SCAM_TEMPLATES)]
        lang = "hinglish" if index < 40 else "en"
        text = template.replace("<num>", str(1000 + (index * 137) % 9000))
        if lang == "hinglish" and "Aapka" not in text and "Ghar" not in text and "Bijli" not in text:
            text = "Aapke " + text[0].lower() + text[1:] if text else text
        rows.append({
            "text": text,
            "label": "scam",
            "category": category,
            "channel": channel,
            "lang": lang,
        })
    for index in range(90):
        category, channel, template = GENUINE_TEMPLATES[index % len(GENUINE_TEMPLATES)]
        lang = "hinglish" if index % 11 == 0 else "en"
        text = template.replace("<num>", str(100 + (index * 53) % 2000))
        if lang == "hinglish" and category in {"Electricity/Utility", "Bank/KYC"}:
            text = "Yaad rahe: " + text
        rows.append({
            "text": text,
            "label": "genuine",
            "category": category,
            "channel": channel,
            "lang": lang,
        })
    return rows


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["text", "label", "category", "channel", "lang"])
        writer.writeheader()
        writer.writerows(rows)


def split_rows(rows, seed=20260314, train_ratio=0.7):
    groups = {"scam": [], "genuine": []}
    for row in rows:
        groups[row["label"]].append(row)
    train = []
    test = []
    for label in ("scam", "genuine"):
        shuffled = list(groups[label])
        random.Random(seed + sum(ord(ch) for ch in label)).shuffle(shuffled)
        train_count = int(round(len(shuffled) * train_ratio))
        train.extend(shuffled[:train_count])
        test.extend(shuffled[train_count:])
    random.Random(seed).shuffle(train)
    random.Random(seed).shuffle(test)
    return train, test


if __name__ == "__main__":
    all_rows = build_rows()
    write_csv(DATA / "dataset.csv", all_rows)
    train_rows, test_rows = split_rows(all_rows)
    write_csv(DATA / "dataset_train.csv", train_rows)
    write_csv(DATA / "dataset_test.csv", test_rows)
    print(f"dataset={len(all_rows)} train={len(train_rows)} test={len(test_rows)}")
