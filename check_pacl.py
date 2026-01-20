import sys
import requests
from bs4 import BeautifulSoup
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

BASE_URL = "https://www.sebipaclrefund.co.in"
STATIC_CAPTCHA = "HV9VFN"


def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    })


def main():
    cert = sys.argv[1]

    session = requests.Session()
    session.get(BASE_URL, timeout=10)

    payload = {
        "CertificateNumber": cert,
        "txtCaptcha_Value": STATIC_CAPTCHA,
        "hdf_CaptchaValue": STATIC_CAPTCHA
    }

    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Referer": BASE_URL + "/"
    }

    r = session.post(
        BASE_URL + "/Refund/GetInvestorClaimDetails",
        data=payload,
        headers=headers,
        timeout=10
    )

    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.select_one("table.ShowEnquiryDetailstbl")

    if not table:
        send_telegram("❌ No data found or invalid certificate.")
        return

    rows = table.find_all("tr")
    output = []

    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if cols:
            output.append(" ".join(cols))

    send_telegram("📄 *PACL Claim Details*\n\n" + "\n".join(output))


if __name__ == "__main__":
    main()
