"""Streamlit Cloud entrypoint for the XST vs XQQ dashboard."""

import runpy

runpy.run_module("src.dashboard", run_name="__main__")
