import sys
import os
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

BASE_URL = "https://www.sebipaclrefund.co.in"
CAPTCHA = "HV9VFN"


def send(msg):
    print("[+] Sending Telegram message...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": msg
        },
        timeout=10
    )
    print("[+] Telegram API response:", r.text)


def main():
    # 🔹 HARD TEST MESSAGE (CONFIRMS TELEGRAM WORKS)
    send("✅ PACL Bot is running. Telegram connectivity OK.")

    # 🔹 Validate input
    if len(sys.argv) < 2 or not sys.argv[1]:
        send("❌ Certificate number missing.")
        return

    cert = sys.argv[1].strip().upper()
    print("[+] Certificate received:", cert)

    # 🔹 Start session
    session = requests.Session()
    session.get(BASE_URL, timeout=10)

    # 🔹 Submit PACL request
    payload = {
        "CertificateNumber": cert,
        "txtCaptcha_Value": CAPTCHA,
        "hdf_CaptchaValue": CAPTCHA
    }

    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Referer": BASE_URL + "/"
    }

    response = session.post(
        BASE_URL + "/Refund/GetInvestorClaimDetails",
        data=payload,
        headers=headers,
        timeout=10
    )

    print("[+] PACL HTTP status:", response.status_code)

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.select_one("table.ShowEnquiryDetailstbl")

    if not table:
        send("❌ No PACL data found or site response changed.")
        return

    rows = table.find_all("tr")
    output_lines = []

    for row in rows:
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if cols:
            output_lines.append(" ".join(cols))

    final_message = (
        "📄 PACL Claim Details\n\n" +
        "\n".join(output_lines)
    )

    send(final_message)


if __name__ == "__main__":
    main()
