import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import fmp_db as db
import time

db.create_audit_logs_table()
st.set_page_config(page_title="FixMyCampus Admin", layout="wide")

# -------------- Initialize session state --------------
if "page" not in st.session_state:
    st.session_state.page = "login"

# -------------- Login Page --------------
def login():
    st.markdown("<h1 style='color: blue; text-align:center;margin-top:-50px;'>FixMyCampus</h1>", unsafe_allow_html=True)
    st.markdown("### Login")
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

# -------------- Dashboard Page --------------
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
# -------------- Manage Issues --------------
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


def to_csv(df):
        return df.to_csv(index=False).encode("utf-8")
# -------------- Export Data --------------
def export_data():
    st.subheader("📤 Export Data")
    choice = st.radio("Select Dataset", ["Users","Banned Users", "Issues"], horizontal=True)

    

    if choice == "Users":
        st.markdown("### All Users")
        users = db.all_user()
        df = pd.DataFrame(users, columns=["First Name", "Last Name", "Email", "Password", "Mobile", "Gender", "Roll No"])
        st.dataframe(df, use_container_width=True)
        st.download_button("⬇ Download CSV", to_csv(df), "users.csv", "text/csv")

    elif choice == "Issues":
        st.markdown("### All Issues")
        issues = db.view_all_issue()
        df = pd.DataFrame(issues, columns=["Roll No", "ID", "Category", "Description", "Location", "Status", "Date"])
        st.dataframe(df, use_container_width=True)
        st.download_button("⬇ Download CSV", to_csv(df), "issues.csv", "text/csv")

    elif choice == "Banned Users":
        st.markdown("### Banned Users")
        users = db.get_banned_users_all()
        columns = df = pd.DataFrame(users, columns=["First Name", "Last Name", "Email", "Password", "Mobile", "Gender", "Roll No"])
        st.dataframe(df,use_container_width=True)
        st.download_button("⬇ Download CSV", to_csv(df), "banned_users.csv", "text/csv")
# -------------- Admin Tools --------------
def admin_tools():
    st.subheader("⚙ Admin Tools")
    tabs = st.tabs(["🚫 Ban/Unban", "📜 Audit Logs", "📢 Notifications (Coming Soon)"])

    # Initialize session state keys
    if "user_details_fetched" not in st.session_state:
        st.session_state.user_details_fetched = False
    if "user_data" not in st.session_state:
        st.session_state.user_data = None
    if "roll_input" not in st.session_state:
        st.session_state.roll_input = ""

    # ---------------- BAN / UNBAN TAB ----------------
    with tabs[0]:
        st.markdown("### 🚫 Ban / Unban User")
        roll = st.text_input("Enter Roll No to Ban/Unban",placeholder="Enter Roll Number", key="roll_input")
        get = st.button("Get Details")
        if get:
            try:
                user_data = db.fetch_user(roll)
                st.session_state.user_data = user_data
                st.session_state.user_details_fetched = True
                # st.success("✅ User details fetched.")
            except Exception as e:
                st.error(f"Some Error: {e}")
                st.session_state.user_details_fetched = False

        if st.session_state.user_details_fetched and st.session_state.user_data:
            first_name, last_name, email, mob_num, gender,roll, ban_status = st.session_state.user_data
            ban_status = "Banned" if ban_status==1 else "Unbanned"
            st.markdown(f"""
                <div class="profile-container">
                    <div class="profile-title">Name: {first_name} {last_name}</div>
                    <div class="profile-field"><span class="profile-label">📧 Email:</span> {email}</div>
                    <div class="profile-field"><span class="profile-label">📞 Mobile:</span> {mob_num}</div>
                    <div class="profile-field"><span class="profile-label">⚧ Gender:</span> {gender}</div>
                    <div class="profile-field"><span class="profile-label">🎓 Roll No:</span> {roll}</div>
                    <div class="profile-field"><span class="profile-label">🚫 Ban Status:</span> {ban_status}</div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚫 Confirm Ban"):
                    if db.ban_user(roll):
                        st.success("✅ User banned.")
                        time.sleep(1)  # Short hold to show result clearly
                        st.session_state.user_details_fetched = False
                        st.rerun()
                    else:
                        st.error("❌ Failed to ban user.")
                        st.rerun()
            with col2:
                if st.button("✅ Unban User"):
                    if db.unban_user(roll):
                        st.success("✅ User unbanned.")
                        time.sleep(1)
                        st.session_state.user_details_fetched = False
                        st.rerun()
                    else:
                        st.error("❌ Failed to unban user.")
                        st.rerun()
        if get and not st.session_state.user_details_fetched:
            st.error("User not found ❌")
        st.markdown("### 🔍 Currently Banned Users")
        banned_users = db.get_banned_users()

        if banned_users:
            column = ["Roll No", "First Name", "Last Name"]
            df = pd.DataFrame(banned_users, columns=column)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No users are currently banned.")

    # ---------------- AUDIT LOG TAB ----------------
    with tabs[1]:
        from datetime import datetime
        st.markdown("### 📜 Admin Audit Logs")
        logs = db.get_audit_logs()
        if logs:
            df = pd.DataFrame(logs, columns=["Audit ID","Action", "Details", "Time"])
            st.dataframe(df, use_container_width=True)
            now =datetime.now()
            filename = "audit_logs"+str(now.strftime("%Y-%m-%d %H:%M:%S"))+".csv"
            st.download_button("⬇ Download CSV", to_csv(df), filename, "text/csv")
        else:
            st.info("No logs yet.")

    # ---------------- NOTIFICATION TAB ----------------
    with tabs[2]:
        st.info("📢 Notifications system coming soon.")

# -------------- Routing based on session --------------
if st.session_state.page == "login":
    login()
elif st.session_state.page == "dashboard":
    dashboard()
