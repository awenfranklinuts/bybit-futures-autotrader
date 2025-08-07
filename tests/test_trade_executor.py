import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bot.signal_parser import parse_signal

# Simulated WhatsApp signal message
MOODENG_MSG = """
🆕 New position
🪙 Coin: MOODENG LONG (20 leverage cross)
📥 Entry: 0.185 - 0.187
🎯 Target 1: 0.192
🎯 Target 2: 0.198
🎯 Target 3: 0.205
🎯 Target 4: 0.21
🎯 Target 5: 0.215
🎯 Target 6: runners
🛑 Stop loss: 1 day candle close below 0.16
📝 Notes: DCA point: 1.64 - leave space to DCA 🔒 1% for entries ( 0.5% entry 1, 0.5% entry 2), 2% for DCA point
"""

BRETT_MSG = """
🆕 New position
🪙 Coin: BRETT LONG (20 leverage cross)
📥 Entry: 0.43 - 0.45
🎯 Target 1: 0.48
🎯 Target 2: 0.491
🎯 Target 3: 0.502
🎯 Target 4: 0.516
🎯 Target 5: 0.526
🎯 Target 6: runners
🛑 Stop loss: 1 day candle close below 0.33
📝 Notes: DCA point: 1.64 - leave space to DCA 🔒 1% for entries ( 0.5% entry 1, 0.5% entry 2), 2% for DCA point
"""

def test_parser():
    print("Testing MOODENG signal:")
    moodeng_data = parse_signal(MOODENG_MSG)
    print(moodeng_data)

    print("\nTesting BRETT signal:")
    brett_data = parse_signal(BRETT_MSG)
    print(brett_data)

if __name__ == "__main__":
    test_parser()
