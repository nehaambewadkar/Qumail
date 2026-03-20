# 🔓 QuMail Decryption Guide

## Method 1: Web Interface (Easiest)

1. Open **http://127.0.0.1:5000**
2. Click the **"Decrypt Email"** tab
3. Open your Gmail inbox → find the QuMail email
4. Copy the entire email body (from `--- QuMail Encrypted Message ---` to `--- End QuMail Message ---`)
5. Paste into the **"Encrypted Email Body"** box
6. Enter your **64-character hex encryption key** (from the sender's confirmation)
7. Click **"Decrypt Message"**

## Method 2: Command Line

```bash
python decrypt_email.py
```

Follow the prompts:
1. Paste the email body, then type `END` on a new line
2. Enter your hex encryption key

## Where to find the Encryption Key

When you send an email, QuMail shows:
```
🔑 Encryption Key (save this!): [64-character hex string]
```

The **sender must share this key securely** with the recipient (e.g., via Signal, WhatsApp, or in person). Without the key, decryption is impossible.

## Security Notes

- Keys are **one-time use** — never reuse
- The key is **never sent in the email** — it's out-of-band
- AES-256-GCM provides **authenticated encryption** (tampering detected)
- Forward secrecy: even if future keys are compromised, past emails remain secure
