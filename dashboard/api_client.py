"""Thin client that the Streamlit pages use to talk to the Django API.

The JWT access token is kept in Streamlit's per-session state, so each browser
session authenticates independently (session-based auth on the dashboard side).
"""
import os

import requests
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://localhost:8000/api")


def _headers():
    token = st.session_state.get("access_token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def register(username, email, password, name):
    return requests.post(f"{API_BASE}/auth/register/", json={
        "username": username, "email": email, "password": password, "name": name,
    }, timeout=20)


def login(username, password):
    resp = requests.post(f"{API_BASE}/auth/login/", json={
        "username": username, "password": password,
    }, timeout=20)
    if resp.status_code == 200:
        st.session_state["access_token"] = resp.json()["access"]
        st.session_state["username"] = username
    return resp


def logout():
    for key in ("access_token", "username"):
        st.session_state.pop(key, None)


def is_authenticated():
    return bool(st.session_state.get("access_token"))


def get(path):
    return requests.get(f"{API_BASE}{path}", headers=_headers(), timeout=30)


def post(path, payload=None):
    return requests.post(f"{API_BASE}{path}", json=payload or {},
                         headers=_headers(), timeout=30)


def patch(path, payload):
    return requests.patch(f"{API_BASE}{path}", json=payload,
                          headers=_headers(), timeout=30)


def delete(path):
    return requests.delete(f"{API_BASE}{path}", headers=_headers(), timeout=30)


def require_login():
    """Call at the top of every page. Stops the page if not logged in."""
    if not is_authenticated():
        st.warning("Please log in from the Home page to view this page.")
        st.stop()
