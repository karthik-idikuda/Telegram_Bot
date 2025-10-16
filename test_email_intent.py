"""
Quick test for email intent detection
"""

from ai_intent_recognizer import ai_intent

# Test messages
test_messages = [
    "send hi in mail",
    "send an email with hello",
    "email me test message",
    "send hello world to email",
    "set a reminder for 1 min",
    "set reminder for 5 minutes",
    "remind me to call mom tomorrow"
]

print("🧪 Testing AI Intent Recognition (Pattern-Based Fallback)\n")
print("=" * 60)

for msg in test_messages:
    result = ai_intent.analyze_intent(msg)
    print(f"\n📝 Message: '{msg}'")
    print(f"🎯 Intent: {result['intent']}")
    print(f"📊 Confidence: {result['confidence']}")
    print(f"🔧 Parameters: {result['parameters']}")
    if result.get('natural_response'):
        print(f"💬 Response: {result['natural_response']}")
    print("-" * 60)
