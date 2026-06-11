import streamlit as st

import api_client as api

st.set_page_config(page_title="Revision Planner", page_icon="🗂️", layout="wide")
api.require_login()
st.title("🗂️ Revision Planner")

# --- Create a task ---------------------------------------------------------
with st.expander("➕ Add a revision task", expanded=True):
    topic = st.text_input("Topic", key="rt_topic")
    priority = st.selectbox("Priority", ["LOW", "MEDIUM", "HIGH"], index=1)
    target_date = st.date_input("Target date")
    if st.button("Create task"):
        resp = api.post("/planner/revision-tasks/", {
            "topic": topic, "priority": priority,
            "target_date": str(target_date), "status": "PENDING",
        })
        if resp.status_code == 201:
            st.success("Task created.")
            st.rerun()
        else:
            st.error(resp.json())

# --- List + manage tasks ---------------------------------------------------
tasks = api.get("/planner/revision-tasks/").json()
results = tasks.get("results", tasks) if isinstance(tasks, dict) else tasks
if not results:
    st.info("No tasks yet.")

for t in results:
    with st.container(border=True):
        cols = st.columns([3, 2, 2, 2, 1])
        cols[0].markdown(f"**{t['topic']}**")
        cols[1].write(f"Priority: {t['priority']}")
        cols[2].write(f"Due: {t.get('target_date') or '—'}")
        new_status = cols[3].selectbox(
            "Status", ["PENDING", "IN_PROGRESS", "COMPLETED"],
            index=["PENDING", "IN_PROGRESS", "COMPLETED"].index(t["status"]),
            key=f"status_{t['id']}",
        )
        if new_status != t["status"]:
            api.patch(f"/planner/revision-tasks/{t['id']}/", {"status": new_status})
            st.rerun()
        if cols[4].button("🗑️", key=f"del_{t['id']}"):
            api.delete(f"/planner/revision-tasks/{t['id']}/")
            st.rerun()
