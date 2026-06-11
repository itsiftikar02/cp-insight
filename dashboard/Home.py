"""CP Insight - Home Dashboard (Streamlit entry point)."""
import streamlit as st

import api_client as api

st.set_page_config(page_title="CP Insight", page_icon="📊", layout="wide")


def auth_panel():
    st.title("📊 CP Insight")
    st.caption("Competitive Programming Analytics for Codeforces")
    tab_login, tab_register = st.tabs(["Log in", "Register"])

    with tab_login:
        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")
        if st.button("Log in"):
            resp = api.login(u, p)
            if resp.status_code == 200:
                st.success("Logged in!")
                st.rerun()
            else:
                st.error("Invalid credentials.")

    with tab_register:
        ru = st.text_input("Username", key="reg_user")
        rn = st.text_input("Full name", key="reg_name")
        re = st.text_input("Email", key="reg_email")
        rp = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Create account"):
            resp = api.register(ru, re, rp, rn)
            if resp.status_code == 201:
                st.success("Account created. Switch to the Log in tab.")
            else:
                st.error(resp.json())


def dashboard():
    st.sidebar.write(f"Signed in as **{st.session_state.get('username')}**")
    if st.sidebar.button("Log out"):
        api.logout()
        st.rerun()

    st.title("📊 Home Dashboard")

    # --- Connect / refresh handle ------------------------------------------
    profile = api.get("/auth/profile/").json()
    with st.expander("🔗 Connect / refresh Codeforces handle", expanded=not profile.get("codeforces_handle")):
        handle = st.text_input("Codeforces handle",
                               value=profile.get("codeforces_handle") or "")
        if st.button("Sync now"):
            with st.spinner("Fetching data from Codeforces..."):
                resp = api.post("/cf/sync/", {"handle": handle})
            if resp.status_code == 200:
                s = resp.json()
                st.success(f"Synced {s['problems_synced']} problems and "
                           f"{s['contests_synced']} contests.")
                st.rerun()
            else:
                st.error(resp.json().get("detail", "Sync failed."))

    # --- Overview cards ----------------------------------------------------
    ov = api.get("/cf/analytics/overview/").json()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current Rating", ov.get("current_rating") or "—")
    c2.metric("Max Rating", ov.get("max_rating") or "—")
    c3.metric("Contests", ov.get("contest_count", 0))
    c4.metric("Problems Solved", ov.get("total_solved", 0))

    st.info("Use the sidebar pages for Rating, Topic Analysis, Recommendations, "
            "Revision Planner, and Daily Goals.")


if api.is_authenticated():
    dashboard()
else:
    auth_panel()
