"""Compatibility entrypoint for Streamlit deployments."""

import runpy

runpy.run_module("src.dashboard", run_name="__main__")
