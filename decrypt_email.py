"""
QuMail Decryption Tool (Command Line)
Decrypt a QuMail encrypted email using the encryption key.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from email_client.imap_client import IMAPClient


def main():
    print("=" * 60)
    print("🔓 QuMail Email Decryption Tool")
    print("=" * 60)
    print()
    print("Paste the encrypted email body below.")
    print("End with a line containing only 'END'")
    print()

    lines = []
    while True:
        try:
            line = input()
            if line.strip() == 'END':
                break
            lines.append(line)
        except EOFError:
            break

    email_body = '\n'.join(lines)

    if not email_body.strip():
        print("❌ No email body provided.")
        sys.exit(1)

    print()
    key_hex = input("🔑 Enter the encryption key (hex): ").strip()

    if not key_hex:
        print("❌ No key provided.")
        sys.exit(1)

    print()
    print("Decrypting...")

    imap = IMAPClient('', '')
    result = imap.decrypt_email(email_body, key_hex)

    if result['success']:
        print("=" * 60)
        print("✅ Decryption Successful!")
        print(f"   Security Level: {result.get('security_level', 'N/A')}")
        print(f"   Key ID: {result.get('key_id', 'N/A')}")
        print()
        print("📧 Decrypted Message:")
        print("-" * 60)
        print(result['plaintext'])
        print("-" * 60)
    else:
        print(f"❌ Decryption failed: {result.get('message', 'Unknown error')}")
        sys.exit(1)


if __name__ == '__main__':
    main()
