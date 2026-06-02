#!/usr/bin/env python3
"""Backward-compatible CLI shim — use `k8s-chaos` or `python -m k8s_chaos.cli`."""
from k8s_chaos.cli import main

if __name__ == "__main__":
    main()
