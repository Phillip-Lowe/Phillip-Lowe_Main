#!/usr/bin/env python3
import requests

# Image URL (full URL from browser)
img_url = "https://s16-kling.klingai.com/kimg/EMXN1y8qngEKBnVwbG9hZBIOeWxhYi1zdHVudC1zZ3AagwFLbGluZ0FJX0tvbG9yc19EaVRfSDgwMF8xX0tvbG9ycy12Ml82LXQyaS1vbW5pLXJlZmluZXItdjNfU0dQX1BST0RfYWlfd2ViXzMxMjU1Mjg5ODMwMzcyN181NzdlNDhjNjE1ZmRkOTQyYmZhNmM0Y2JlY2Y1NjJhN3o4czhqLnBuZw:720x956.webp?x-kcdn-pid=112372"

# Cookies from browser session
cookies = {
    "kGateway-identity": "kGateway-53cf564e-195801392",
    "did": "web_c7eumd6g61s0iraszg1h1frnxlwmqnipg1z8",
    "_gcl_au": "1.1.1469582142.1780577962",
    "_ga": "GA1.1.2055928209.1780577962",
    "__risk_web_device_id": "64f0f0b91780577962686f61",
    "kwpsecproductname": "kling-web-sgp",
    "accept-language": "en-001",
    "history-locale": "en",
    "wid": "66977293457050871",
    "userId": "40702873",
    "ksi18n.ai.portal_ph": "09d6bbd3f873db010ca69def70bffa1abf9e",
    "teamId": "",
    "ktrace-context": "1|MS44Nzg0NzI0NTc4Nzk2ODY5LjQ2Mzk0Mjk2LjE3ODA1Nzk0Njg1MjguMzUwMTM1MA==|MS44Nzg0NzI0NTc4Nzk2ODY5Ljg3ODI3Njc4LjE3ODA1Nzk0Njg1MjguMzUwMTM1MQ==|0|webservice-user-growth-node|webservice|true|src-Js",
    "_ga_MWG30LDQKZ": "GS2.1.s1780577962$o1$g1$t1780581795$j54$l0$h1856304093",
    "g_state": '{"i_l":0,"i_ll":1780581795953,"i_b":"OSv/3Xek7br76RG7Ljjqv30dw43q/YRKJGNijahBpMg","i_e":{"enable_itp_optimization":0},"i_et":1780577963135}',
    "kwfv1": "+/PIG9bS+90zD8/40D8eZA8nPIPn8Y+0cEGf8f+e8f8n+fG/pS+fcAwe+jPBcF+BrhG04S8npS8Bbj8epfPezY+0GI+9PUP/WhP9LEPn+f+Apf+/q7G040PeZl80Sfw/pYP0Ph8BQf+eSYPAmD+9L78nHI+0WAweGh8/QYP0rl+0W=",
    "kwssectoken": "uBXQAQ5V3wZCbSzpku8P8I2sQwu/kUVlZnh7J6KsYlPpb/ZiAH5nG+PTPcGB9azixm5Cgh+E8zzi3CHQuuy+WA==",
    "kwscode": "933f4035f7715a5bd619333317306be85211bb1c7aafb83e9a7c35189ce05e1d"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Referer": "https://kling.ai/app/image/new",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8"
}

response = requests.get(img_url, cookies=cookies, headers=headers, allow_redirects=True)
print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
print(f"Content-Length: {len(response.content)} bytes")

if response.status_code == 200 and len(response.content) > 1000:
    output_path = "systack-site/brand/social/systack-logo-profile.png"
    with open(output_path, "wb") as f:
        f.write(response.content)
    print(f"Saved to: {output_path}")
else:
    print(f"Failed or too small. Content: {response.content[:200]}")
