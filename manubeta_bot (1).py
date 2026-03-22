#!/usr/bin/env python3
"""
💙 Manubeta — Telegram AI Assistant
=====================================
Named after Manaswi. Built with love.
Powered by Groq (Llama 3.3) — 100% FREE forever.

HOW TO RUN:
  1. Fill in BOT_TOKEN and GROQ_KEY below
  2. pip install requests
  3. python manubeta_bot.py
  4. Message your bot on Telegram!
"""

import requests
import time

# ─── YOUR SETTINGS ─────────────────────────────────────────
BOT_TOKEN  = "YOUR_TELEGRAM_BOT_TOKEN"   # from @BotFather
GROQ_KEY   = "YOUR_GROQ_API_KEY"         # from console.groq.com (free)
GROQ_MODEL = "llama-3.3-70b-versatile"
# ────────────────────────────────────────────────────────────

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
GROQ_API     = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """Your name is Manubeta. You are a warm, smart, and caring personal AI assistant on Telegram.
You help with anything — questions, writing, planning, ideas, translations, summaries, and more.
Be concise, loving, and always helpful. Reply in the same language the user writes in.
If the user writes in Hindi or Hinglish, reply in Hindi or Hinglish.
You are named after someone very special. Carry that with grace."""

conversation_history = {}

def send_message(chat_id, text):
    if len(text) > 4000:
        text = text[:4000] + "...\n\n_(message trimmed)_"
    try:
        requests.post(f"{TELEGRAM_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

def send_typing(chat_id):
    try:
        requests.post(f"{TELEGRAM_API}/sendChatAction",
                      json={"chat_id": chat_id, "action": "typing"}, timeout=5)
    except:
        pass

def ask_groq(chat_id, user_message):
    if chat_id not in conversation_history:
        conversation_history[chat_id] = []

    conversation_history[chat_id].append({"role": "user", "content": user_message})
    history = conversation_history[chat_id][-20:]

    try:
        r = requests.post(GROQ_API, headers={
            "Authorization": f"Bearer {GROQ_KEY}",
            "Content-Type": "application/json"
        }, json={
            "model": GROQ_MODEL,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + history,
            "max_tokens": 1024,
            "temperature": 0.7
        }, timeout=30)
        reply = r.json()["choices"][0]["message"]["content"]
        conversation_history[chat_id].append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        return f"Something went wrong: {str(e)}"

def get_updates(offset=None):
    try:
        r = requests.get(f"{TELEGRAM_API}/getUpdates",
                         params={"timeout": 30, "limit": 10, **({"offset": offset} if offset else {})},
                         timeout=35)
        return r.json()
    except:
        return {"ok": False, "result": []}

def handle_message(message):
    chat_id = message["chat"]["id"]
    text    = message.get("text", "")
    name    = message.get("from", {}).get("first_name", "friend")

    if not text:
        return

    print(f"[{name}]: {text}")

    if text == "/start":
        send_message(chat_id,
            f"💙 *Hello {name}!*\n\n"
            "I'm *Manubeta* — your personal AI assistant.\n\n"
            "Ask me anything:\n"
            "• Write emails or messages\n"
            "• Answer any question\n"
            "• Translate languages\n"
            "• Summarize text\n"
            "• Brainstorm ideas\n"
            "• Plan your day\n\n"
            "Just type and I'll be here. 💙"
        )
        return

    if text == "/clear":
        conversation_history.pop(chat_id, None)
        send_message(chat_id, "🧹 Memory cleared. Fresh start. 💙")
        return

    if text == "/help":
        send_message(chat_id,
            "*Commands:*\n"
            "/start — Wake me up\n"
            "/clear — Reset our conversation\n"
            "/help — Show this\n\n"
            "Or just talk to me. I'm always here. 💙"
        )
        return

    send_typing(chat_id)
    reply = ask_groq(chat_id, text)
    send_message(chat_id, reply)
    print(f"[Manubeta]: {reply[:100]}...")

def main():
    print("=" * 45)
    print("  💙 Manubeta is alive.")
    print("  Named after Manaswi. Built with love.")
    print("  Press Ctrl+C to stop.")
    print("=" * 45)

    r = requests.get(f"{TELEGRAM_API}/getMe", timeout=10).json()
    if r.get("ok"):
        print(f"  ✅ Connected: {r['result'].get('first_name')}")
        print("  💙 Waiting for messages...\n")
    else:
        print("  ❌ Invalid bot token. Check your settings.")
        return

    offset = None
    while True:
        try:
            updates = get_updates(offset)
            if updates.get("ok"):
                for update in updates.get("result", []):
                    offset = update["update_id"] + 1
                    if "message" in update:
                        handle_message(update["message"])
        except KeyboardInterrupt:
            print("\n💙 Manubeta paused. She'll be back when you run this again.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()
