#!/usr/bin/env python3
import sys
from SsnakeAgent import SsnakeAgent

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ssnake <user_prompt> [--verbose]")
        sys.exit(1)

    user_prompt = sys.argv[1]
    verbose = False
    if len(sys.argv) > 2 and sys.argv[2] == '--verbose':
        verbose = True
    global agent
    agent = SsnakeAgent(user_prompt, verbose)
    agent.run()