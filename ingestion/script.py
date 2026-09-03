import os
raw = os.getenv("GITHUB_PRIVATE_KEY")
if raw is None:
    print("GITHUB_PRIVATE_KEY is not set in this session")
else:
    print("length:", len(raw))
    print("first 60:", repr(raw[:60]))
    print("last 60:", repr(raw[-60:]))