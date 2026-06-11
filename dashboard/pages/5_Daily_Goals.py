import datetime

import streamlit as st

import api_client as api

st.set_page_config(page_title="Daily Goals", page_icon="🎯", layout="wide")
api.require_login()
st.title("🎯 Daily Goals")

with st.expander("➕ Set a goal", expanded=True):
    desc = st.text_input("Description", placeholder="Solve 2 DP problems")
    goal_type = st.selectbox("Type", ["SOLVE_PROBLEMS", "CONTEST"])
    topic = st.text_input("Topic (optional)")
    target = st.number_input("Target count", min_value=1, value=2)
    date = st.date_input("Date", value=datetime.date.today())
    if st.button("Create goal"):
        resp = api.post("/planner/daily-goals/", {
            "description": desc, "goal_type": goal_type, "topic": topic,
            "target_count": int(target), "completed_count": 0, "date": str(date),
        })
        if resp.status_code == 201:
            st.success("Goal created.")
            st.rerun()
        else:
            st.error(resp.json())

goals = api.get("/planner/daily-goals/").json()
results = goals.get("results", goals) if isinstance(goals, dict) else goals
if not results:
    st.info("No goals yet.")

for g in results:
    with st.container(border=True):
        st.markdown(f"**{g['description']}**  ·  {g['date']}")
        st.progress(g["completion_percentage"] / 100,
                    text=f"{g['completed_count']}/{g['target_count']} "
                         f"({g['completion_percentage']}%)")
        c1, c2 = st.columns(2)
        if c1.button("➕ Log progress", key=f"inc_{g['id']}"):
            api.patch(f"/planner/daily-goals/{g['id']}/",
                      {"completed_count": g["completed_count"] + 1})
            st.rerun()
        if c2.button("🗑️ Delete", key=f"delg_{g['id']}"):
            api.delete(f"/planner/daily-goals/{g['id']}/")
            st.rerun()
