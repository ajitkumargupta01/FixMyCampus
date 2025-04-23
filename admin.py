import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import fmp_db as db

db.create_audit_logs_table()
st.set_page_config(page_title="FixMyCampus Admin", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "login"

def login():
    st.markdown("<h1 style='color: blue; text-align:center;margin-top:-50px;'>FixMyCampus</h1>", unsafe_allow_html=True)
    st.markdown("### Admin Login")
    with st.form("login_form"):
        username = st.text_input("Username").strip()
        password = st.text_input("Password", type="password").strip()
        st.checkbox("Remember me")
        btn = st.form_submit_button("Login")
        if btn:
            if username == "admin@1234" and password == "123":
                st.session_state.page = "dashboard"
                st.success("Login successful!")
                st.rerun()
            else:
                st.warning("❌ Invalid credentials")

def dashboard():
    with st.sidebar:
        selected = option_menu(
            menu_title="FixMyCampus",
            options=["Dashboard", "Manage Issues", "Export Data", "Admin Tools", "Logout"],
            icons=["bar-chart", "wrench", "download", "gear", "box-arrow-right"],
            menu_icon="tools",
            default_index=0
        )
    
    if selected == "Dashboard":
        st.subheader("📊 Admin Dashboard")
        issues = db.view_all_issue()
        users = db.all_user()

        if issues:
            df = pd.DataFrame(issues, columns=["Roll No", "ID", "Category", "Description", "Location", "Status", "Date"])
            resolved = df[df["Status"] == "Resolved"]
            in_progress = df[df["Status"] == "In Progress"]
            pending = df[df["Status"] == "Pending"]

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total", len(df))
            col2.metric("Resolved", len(resolved))
            col3.metric("In Progress", len(in_progress))
            col4.metric("Pending", len(pending))

            st.markdown("### 📅 Recent Issues")
            st.dataframe(df.sort_values("Date", ascending=False).head(5), use_container_width=True)

        st.markdown("### 👥 Registered Users")
        st.success(f"Total Users: {len(users)}")

    elif selected == "Manage Issues":
        manage_issues()

    elif selected == "Export Data":
        export_data()

    elif selected == "Admin Tools":
        admin_tools()

    elif selected == "Logout":
        st.session_state.clear()
        st.success("Logged out.")
        st.session_state.page = "login"
        st.rerun()

def manage_issues():
    st.subheader("📝 View & Update All Reported Issues")
    issues = db.view_all_issue()
    if not issues:
        st.warning("No issues found.")
    else:
        df = pd.DataFrame(issues, columns=["Roll No", "ID", "Category", "Description", "Location", "Status", "Date"])
        with st.expander("🔍 Filter Issues"):
            col1, col2, col3 = st.columns(3)
            status = col1.selectbox("Status", ["All", "Pending", "In Progress", "Resolved"])
            user = col2.text_input("Roll No")
            category = col3.text_input("Category")

            if status != "All":
                df = df[df["Status"] == status]
            if user:
                df = df[df["Roll No"].str.contains(user, case=False)]
            if category:
                df = df[df["Category"].str.contains(category, case=False)]

        st.dataframe(df, use_container_width=True)

        st.markdown("### ✏ Manage Individual Issue")
        issue_id = st.text_input("Enter Issue ID")
        if issue_id:
            issue = db.search_issues(issue_id=issue_id)
            if not issue:
                st.error("Issue ID not found.")
            else:
                col1, col2, col3 = st.columns([2, 2, 1])
                new_status = col1.selectbox("Update Status", ["Pending", "In Progress", "Resolved"])
                if col2.button("✅ Update"):
                    if db.update_issue_status(issue_id, new_status):
                        st.success("Updated")
                        st.rerun()
                if col3.button("🗑 Delete"):
                    if db.delete_issue(issue_id):
                        st.success("Deleted")
                        st.rerun()

def export_data():
    st.subheader("📤 Export Data")
    choice = st.radio("Select Dataset", ["Users", "Issues"], horizontal=True)

    def to_csv(df):
        return df.to_csv(index=False).encode("utf-8")

    if choice == "Users":
        users = db.all_user()
        df = pd.DataFrame(users, columns=["First Name", "Last Name", "Email", "Password", "Mobile", "Gender", "Roll No", "Banned"])
        st.dataframe(df, use_container_width=True)
        st.download_button("⬇ Download CSV", to_csv(df), "users.csv", "text/csv")

    elif choice == "Issues":
        issues = db.view_all_issue()
        df = pd.DataFrame(issues, columns=["Roll No", "ID", "Category", "Description", "Location", "Status", "Date"])
        st.dataframe(df, use_container_width=True)
        st.download_button("⬇ Download CSV", to_csv(df), "issues.csv", "text/csv")

def admin_tools():
    st.subheader("⚙ Admin Tools")
    tabs = st.tabs(["🚫 Ban/Unban", "📜 Audit Logs", "📢 Notifications"])

    with tabs[0]:
        st.markdown("### 🚫 Ban / Unban User")
        roll = st.text_input("Enter Roll No to Ban/Unban")

        col1, col2 = st.columns(2)
        if col1.button("🚫 Ban User"):
            if db.ban_user(roll):
                st.success("✅ User banned.")
                st.rerun()
            else:
                st.error("❌ Failed to ban user.")

        if col2.button("✅ Unban User"):
            if db.unban_user(roll):
                st.success("✅ User unbanned.")
                st.rerun()
            else:
                st.error("❌ Failed to unban user.")

        st.markdown("### 🔍 Currently Banned Users")
        banned_users = db.get_banned_users()
        if banned_users:
            df = pd.DataFrame(banned_users, columns=["Roll No", "First Name", "Last Name"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No users are currently banned.")

    with tabs[1]:
        st.markdown("### 📜 Admin Audit Logs")
        logs = db.get_audit_logs()
        if logs:
            df = pd.DataFrame(logs, columns=["Action", "Details", "Time"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No logs yet.")

    with tabs[2]:
        st.info("📢 Notifications system coming soon.")

if st.session_state.page == "login":
    login()
elif st.session_state.page == "dashboard":
    dashboard()