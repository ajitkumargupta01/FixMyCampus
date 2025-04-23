import streamlit as st
import fmp_db as db
import mysql.connector 
from streamlit_option_menu import option_menu
import mysql
from datetime import datetime
import pandas as pd
import plotly.express as px

if "page" not in st.session_state:
    st.session_state.page = "login"

st.markdown("""
    <style>
     .stAppHeader
                {
                margin-top:-1000px;
                background-color:green;}
    }
    </style>
    """, unsafe_allow_html=True)

#------------------------------ Issue dashboard -----------------------
def issue_dashboard():
    st.title("📊 Issue Analytics Dashboard")

    # --- Fetch data from DB ---
    issues = db.view_all_issue()
    
    # --- Convert to DataFrame ---
    df = pd.DataFrame(issues, columns=[
        "ID", "Roll Number", "Category", "Description", "Location", "Status", "Date"
    ])
    if df.empty:
        st.warning("No issues found in the database.")
        return

    # --- Clean/format date if needed ---
    df["Date"] = pd.to_datetime(df["Date"])

    # --- Pie Chart: Category Wise ---
    st.markdown("#### 🧩 Category-wise Distribution")
    cat_pie = px.pie(df, names="Category", title="Issues by Category")
    st.plotly_chart(cat_pie, use_container_width=True)

    # --- Bar Chart: Status Wise ---
    st.markdown("### 🏷 Status-wise Count")
    status_count = df["Status"].value_counts().reset_index()
    status_count.columns = ["Status", "Count"]

    bar = px.bar(status_count, x="Status", y="Count",
                 color="Status",
                 color_discrete_map={
                     "Pending": "#f59e0b",
                     "In Progress": "#3b82f6",
                     "Resolved": "#10b981"
                 })
    st.plotly_chart(bar, use_container_width=True)

    # --- Time Trend Chart ---
    st.markdown("### 🕒 Issues Reported Over Time")
    trend = df.groupby(df["Date"].dt.date).size().reset_index(name="Issues")
    line_chart = px.line(trend, x="Date", y="Issues", title="Issues Over Time")
    st.plotly_chart(line_chart, use_container_width=True)

#------------------------------- Login ---------------------------------
def login():
    st.markdown("<h1 style='color: blue; text-align:center;margin-top:-50px;'>FixMyCampus</h1>", unsafe_allow_html=True)
    db.create_Table()
    st.markdown("### Login")
    with st.form("login_form"):
        
        roll_no = st.text_input("Roll Number", placeholder="Enter your roll number").strip()
        password = st.text_input("Password", type="password", placeholder="Enter your password").strip()
        remember = st.checkbox("Remember me")

        col1,col2,col4, col6 = st.columns(4)
        login_button = col1.form_submit_button("Log In")
        forgot_button= col4.form_submit_button("Forgot password")
        signup_button = col2.form_submit_button("Sign Up")
        Admin_button = col6.link_button("Admin login","http://localhost:8502/")

        if forgot_button:
            forgot_password()
            
        elif login_button:
            user = db.check_user(roll_no, password)
            if user:
                st.session_state.roll_no = roll_no
                st.session_state.user = user[0]
                st.success("✅ Successfully logged in!")
                st.session_state.page = "home"
                st.rerun()
            else:
                st.warning("❌ User not found or account is banned. Please sign up.")

        elif signup_button:
            st.session_state.page = "signup"
            st.rerun()

#----------------------------- Forgot password ----------------------------
@st.dialog(" ")
def forgot_password():
    st.markdown("### 🔐 Forgot Password")
    with st.form("forgot_form"):
        roll_no = st.text_input("Roll Number", placeholder="Enter your roll number").strip()
        mob_num = st.text_input("Mobile Number", placeholder="Registered Mobile Number").strip()
        new_pass = st.text_input("New Password", type="password")
        confirm_pass = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Submit")

        if submit:
            if roll_no and mob_num and new_pass and confirm_pass:
                if new_pass == confirm_pass:
                    success = db.forgot_password(roll_no, mob_num, new_pass)
                    if success:
                        st.success("✅ Password reset successfully!")
                        st.session_state.page = "login"
                    else:
                        st.error("❌ No matching user found with that Roll Number and Mobile Number.")
                else:
                    st.error("❌ Passwords do not match.")
            else:
                st.warning("⚠ Please fill in all fields.")

#--------------------------- Sign-Up -----------------------------------
def sign_up():
    st.markdown("<h1 style='color: blue; text-align:center;margin-top:-50px;'>FixMyCampus</h1>", unsafe_allow_html=True)
    db.create_Table()
    st.markdown("<h1 style='font-size:30px;'>Sign-Up</h1>", unsafe_allow_html=True)

    with st.form("signup_form"):
        col6, col7 = st.columns(2)
        first_name = col6.text_input("First Name", placeholder="Enter your first name").strip()
        last_name = col7.text_input("Last Name", placeholder="Enter your last name").strip()

        col1, col2 = st.columns(2)
        email = col1.text_input("Email", placeholder="Enter your email").strip()
        password = col2.text_input("Password", type="password", placeholder="Enter your password").strip()

        col8, col9, col12 = st.columns(3)
        roll_no = col8.text_input("Roll Number", placeholder="Enter your roll number").strip()
        mob_num = col9.text_input("Mobile Number", placeholder="Enter your mobile number").strip()
        gender = col12.selectbox("Gender", ("Select", "Male", "Female", "Other"))

        col10,d,f,g,col11 = st.columns(5)
        submitted = col10.form_submit_button("Sign Up")
        login_btn = col11.form_submit_button("Back to Login")

        if submitted:
            if all([first_name, last_name, email, password, roll_no, mob_num, gender != "Select"]):
                data = (first_name, last_name, email, password, mob_num, gender, roll_no)
                try:
                    db.register_user(data)
                    st.success("✅ Sign-up successful! Please log in.")
                    st.session_state.page = "login"
                except mysql.connector.errors.IntegrityError:
                    st.warning("The Roll number already exists ⚠")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.warning("⚠ Please fill in all fields.")
        elif login_btn:
            st.session_state.page = "login"
            st.rerun()

#-------------------------------- About Campus ----------------------------
def about_campus():
    st.markdown("""
    <style>
        body {
            background-image: url("https://cdn.pixabay.com/photo/2023/08/14/15/42/milkyway-8190232_1280.jpg");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            color: #f1a7c2;
        }
        .highlight {
            background-color: rgba(0, 0, 0, 0.7);
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.15);
            margin-bottom: 20px;
        }
        .section-title {
            font-size: 24px;
            font-weight: bold;
            color: #ffffff;
            margin-top: 25px;
        }
        .emoji {
            font-size: 22px;
        }
        .content {
            font-size: 18px;
            color: #f1a7c2;
        }
        .subheader {
            font-size: 20px;
            font-weight: bold;
            color: #ffffff;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("🏫 Meerut Institute of Technology ")
    st.subheader("📍 Location")
    st.write("NH-58, Baral Partapur Bypass Road, Meerut – 250103, Uttar Pradesh, India")

    st.markdown('<div class="section-title">☎ Contact</div>', unsafe_allow_html=True)
    st.markdown("- 📞 Phone: +91-9334455661")
    st.markdown("- 📧 Email: info@mitmeerut.net.in")
    st.markdown("- 🌐 Website: [mitmeerut.net.in](https://mitmeerut.net.in/)")

    st.markdown('<div class="section-title">🏢 Campus Facilities</div>', unsafe_allow_html=True)
    st.markdown(""" 
    - 🏠 Separate Hostels for Boys & Girls
    - 💻 High-Speed Wi-Fi & Computing Labs
    - 🚌 Transport Facilities to/from City
    - 🏥 24/7 Medical & First-Aid Services
    - 🏅 Gymnasium, Indoor & Outdoor Sports
    - 🧑‍🏫 Qualified Faculty with Guest Houses
    - 📖 Central Library & Digital Learning Hubs
    - 🛠 State-of-the-art Engineering Labs
    """)

    st.markdown('<div class="section-title">🎓 Courses Offered</div>', unsafe_allow_html=True)
    st.markdown(""" 
    - 🖥 B.Tech - Computer Science & Engineering
    - ⚙ B.Tech - Mechanical Engineering
    - 🏗 B.Tech - Civil Engineering
    - 📡 B.Tech - Electronics & Communication
    - 🧠 B.Tech - Artificial Intelligence & Data Science
    - 💊 Bachelor of Pharmacy (B.Pharm)
    - 🌱 B.Sc. in Agriculture
    - 🧮 Bachelor of Computer Applications (BCA)
    - 📊 Bachelor of Business Administration (BBA)
    - 🧑‍🏫 Bachelor of Education (B.Ed)
    - 🎓 M.Tech and MBA programs
    """)

    st.markdown('<div class="section-title">🌟 Vision</div>', unsafe_allow_html=True)
    st.info("To impart value-based education integrated with practical knowledge, preparing students to lead with wisdom and integrity.")

    st.markdown('<div class="section-title">🎯 Mission</div>', unsafe_allow_html=True)
    st.markdown(""" 
    - 🔬 Foster research, innovation, and critical thinking.
    - 💡 Promote creativity and entrepreneurship.
    - 🤝 Serve society through responsible technological contributions.
    - 🧑‍🎓 Deliver quality technical and professional education.
    - 🌍 Nurture students into global citizens with strong ethics.
    """)

    st.markdown('<div class="section-title">💼 Career Development & Training</div>', unsafe_allow_html=True)
    st.markdown(""" 
    - 🧩 Industry-Specific Training Modules
    - 🤝 Corporate Tie-ups with TCS, Wipro, Infosys, etc.
    - 🗣 Soft Skills & Communication Workshops
    - 🎯 Placement Preparation and Mock Interviews
    """)

    st.markdown('<div class="section-title">📚 Extra Curriculars</div>', unsafe_allow_html=True)
    st.markdown(""" 
    - 🎭 Annual Fest, Cultural & Tech Events
    - 🏸 Intra & Inter-college Sports Competitions
    - 🌱 NSS & Environmental Activities
    - 💬 Debate, Coding & Entrepreneurship Clubs
    """)

    st.markdown('<div class="section-title">🔗 More Information</div>', unsafe_allow_html=True)
    st.markdown("👉 [Click here to visit the official website](https://mitmeerut.net.in/)")

#-------------------------------- View Profile -----------------------------
def view_profile():
    st.title("👤 My Profile")

    st.markdown("""
        <style>
            .profile-container {
                background: linear-gradient(to right, #e0e7ff, #f0f4ff);
                padding: 2rem;
                border-radius: 15px;
                margin-top: 20px;
                box-shadow: 4px 4px 15px rgba(0, 0, 0, 0.1);
            }
            .profile-title {
                font-size: 26px;
                font-weight: bold;
                color: #1e3a8a;
                margin-bottom: 1rem;
            }
            .profile-field {
                font-size: 18px;
                margin: 0.5rem 0;
                color: #1f2937;
            }
            .profile-label {
                font-weight: 600;
                color: #111827;
            }
        </style>
    """, unsafe_allow_html=True)

    if 'roll_no' not in st.session_state:
        st.error("⚠ You must be logged in to view your profile.")
        return

    roll_no = st.session_state.roll_no
    user = db.fetch_user(roll_no)

    if not user:
        st.warning("🚫 No user data found for the logged-in Roll No.")
        return

    first_name, last_name, email, mob_num, gender, roll_no = user

    st.markdown(f"""
        <div class="profile-container">
            <div class="profile-title">Welcome, {first_name} {last_name}!</div>
            <div class="profile-field"><span class="profile-label">📧 Email:</span> {email}</div>
            <div class="profile-field"><span class="profile-label">📞 Mobile:</span> {mob_num}</div>
            <div class="profile-field"><span class="profile-label">⚧ Gender:</span> {gender}</div>
            <div class="profile-field"><span class="profile-label">🎓 Roll No:</span> {roll_no}</div>
        </div>
    """, unsafe_allow_html=True)

    with st.form("edit_form"):
        edit = st.form_submit_button("✏ Edit My Profile")
        if edit:
            edit_profile()

#------------------------------- Edit profile -----------------------------
@st.dialog(" ")
def edit_profile():
    st.title("✏ Edit My Profile")

    if 'roll_no' not in st.session_state:
        st.error("⚠ You must be logged in to edit your profile.")
        return

    roll_no = st.session_state.roll_no
    user = db.fetch_user(roll_no)

    if not user:
        st.warning("🚫 No user data found for the logged-in Roll No.")
        return

    first_name, last_name, email, mob_num, gender, _ = user

    st.markdown("### 📝 Update Your Information")
    new_first_name = st.text_input("First Name", value=first_name)
    new_last_name = st.text_input("Last Name", value=last_name)
    new_email = st.text_input("Email", value=email)
    new_mobile = st.text_input("Mobile Number", value=mob_num)
    new_gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(gender))

    if st.button("💾 Save Changes"):
        success = db.update_user(
            roll_no,
            new_first_name,
            new_last_name,
            new_email,
            new_mobile,
            new_gender
        )
        if success:
            st.success("✅ Profile updated successfully!")
            st.session_state.page="👤 View Profile"
            st.rerun()
        else:
            st.error("❌ Failed to update profile.")

#--------------------------------- Report Issue ----------------------------
def report_issue():
    st.markdown("# Report an Issue")
    db.create_issues_table()
    st.markdown("## Fill the form to report a campus issue")

    issue_type = st.selectbox("Select Issue Type", [
        "Electricity", "Water Supply", "Internet", "Furniture", "Cleanliness", "Bus", "Other"
    ])
    if issue_type == "Other":
        issue_type = st.text_input("Enter Issue Type",placeholder="Issue Name")
    description = st.text_area("Describe the Issue")
    location = st.text_input("Issue Location (e.g., Room No, Block Name, etc.)")
    date_reported = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        if st.button("Submit Issue"):
            if issue_type and description and location:
                status = "Pending"
                roll_no = st.session_state.roll_no
                data = (roll_no,issue_type,description,location,status,date_reported)
                db.add_issue(data)
                st.success("Issue reported successfully!")
                st.info(f"Date: {date_reported}")
            else:
                st.error("Please fill all fields before submitting.")
    except Exception as e:
        st.warning(f"Some Error:{e}")

#------------------------------------ My Issues ----------------------------
def my_issue():
    status_colors = {
        "Pending": "#f59e0b",
        "In Progress": "#3b82f6",
        "Resolved": "#10b981"
    }
    st.title("📊 Issue Status Dashboard")
    st.markdown("Here you can track the status of your reported campus issues.")
    st.markdown("---")
    roll_no = st.session_state.roll_no
    issues = db.view_my_issue(roll_no)
    st.markdown("""
        <style>
            .my-issues-box:hover{
                transform: translateY(-5px) scale(1.02);
                box-shadow: 0 12px 24px rgba(79,70,229,0.2);
            }
        </style>
    """,unsafe_allow_html=True)
    if not issues:
        st.info("You haven't reported any issues yet.")
        return
    issues.reverse()
    for issue in issues:
        issue_id,issue_type,description,location,status,date_reported = issue[1],issue[2],issue[3],issue[4],issue[5],issue[6]
        color = status_colors.get(status, "#9ca3af")

        with st.container():
            st.markdown(f"""
                <div class="my-issues-box" style='
                    background-color: #fff;
                    padding: 1.2rem;
                    margin-bottom: 1rem;
                    border-left: 6px solid {color};
                    border-radius: 10px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                '>
                    <h4 style='margin:0;font-size:30px; color:#4f46e5;'>{issue_type}</h4>
                    <p style='margin:0.2rem 0; color:#374151;'>Issue ID:{issue_id}</p>
                    <p style='margin:0.2rem 0; color:#374151;'>{description}</p>
                    <p style='margin:0.2rem 0; font-size: 14px; color:#6b7280;'>📍 Location: {location}</p>
                    <p style='margin:0.2rem 0; font-size: 14px; color:#6b7280;'>📅 Reported: {date_reported}</p>
                    <strong style='color:{color};'>Status: {status}</strong>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("""-----""")

#--------------------------------- 📊 Issue Status -----------------------------
def issue_status():
    status_colors = {
        "Pending": "#f59e0b",
        "In Progress": "#3b82f6",
        "Resolved": "#10b981"
    }

    st.markdown("""
        <style>
            .issues-status-box:hover{
                transform: translateY(-5px) scale(1.02);
                box-shadow: 0 12px 24px rgba(79,70,229,0.2);
            }
        </style>
    """,unsafe_allow_html=True)

    st.markdown("## 📊 Issue Status Dashboard in Campus")
    st.markdown("Here you can track the status of your reported campus issues.")
    st.markdown("---")
    roll_no = st.session_state.roll_no
    issues = db.view_all_issue()

    if not issues:
        st.info("No issues found in the database.")
        return

    col1,col2 = st.columns(2)
    issues.reverse()
    
    for index, issue in enumerate(issues):
        issue_id,issue_type,description,location,status,date_reported = issue[1],issue[2],issue[3],issue[4],issue[5],issue[6]
        color = status_colors.get(status, "#9ca3af")

        container = col1 if index % 2 == 0 else col2

        with container:
            st.markdown(f"""
                <div class="issues-status-box" style='
                    background-color: #fff;
                    padding: 1.2rem;
                    margin-bottom: 1rem;
                    border-left: 6px solid {color};
                    border-radius: 10px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                '>
                    <h4 style='margin:0;font-size:30px; color:#4f46e5;'>{issue_type}</h4>
                    <p style='margin:0.2rem 0; color:#374151;'>Issue ID:{issue_id}</p>
                    <p style='margin:0.2rem 0; color:#374151;'>{description}</p>
                    <p style='margin:0.2rem 0; font-size: 14px; color:#6b7280;'>📍 Location: {location}</p>
                    <p style='margin:0.2rem 0; font-size: 14px; color:#6b7280;'>📅 Reported: {date_reported}</p>
                    <strong style='color:{color};'>Status: {status}</strong>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("""-----""")

#---------------------------------- Change password -----------------------------
def change_password():
    st.title("🔐 Change Password")

    if 'roll_no' not in st.session_state:
        st.warning("⚠ You must be logged in to change your password.")
        return

    with st.form("change_password_form"):
        st.markdown("### Please enter your credentials")
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        submit_btn = st.form_submit_button("Update Password")

        if submit_btn:
            if not current_password or not new_password or not confirm_password:
                st.error("🚫 All fields are required.")
            elif new_password != confirm_password:
                st.error("❌ New passwords do not match.")
            elif new_password == current_password:
                st.warning("⚠ New password should be different from the current password.")
            else:
                success = db.verify_and_update_password(
                    st.session_state.roll_no,
                    current_password,
                    new_password
                )
                if success:
                    st.success("✅ Password changed successfully!")
                else:
                    st.error("❌ Failed to update password. Please check your current password.")

#------------------------------------ Help and support -----------------------------
def help_support_page():
    st.title("🆘 Help & Support")
    st.markdown("Click on a question below to view its answer. Only one can stay open at a time.")

    faq_items = [
        {
            "key": "faq1",
            "question": "How do I report an issue?",
            "answer": "Go to 'Report Issue' from the menu, fill the form, and click submit. You can track it in 'My Issues'."
        },
        {
            "key": "faq2",
            "question": "Can I edit or delete my reported issue?",
            "answer": "Currently, editing or deleting is not available. You may contact admin for any major changes."
        },
        {
            "key": "faq3",
            "question": "How long does it take to resolve an issue?",
            "answer": "Depending on the type of issue, resolution may take 1–5 working days. Track it in your dashboard."
        },
        {
            "key": "faq4",
            "question": "How do I reset my password?",
            "answer": "Go to the Login page, click 'Forgot Password', verify your mobile & username, then set a new password."
        }
    ]

    if "active_faq" not in st.session_state:
        st.session_state.active_faq = None

    for item in faq_items:
        if st.button(f"📌 {item['question']}", key=item["key"]):
            if st.session_state.active_faq == item["key"]:
                st.session_state.active_faq = None
            else:
                st.session_state.active_faq = item["key"]

        if st.session_state.active_faq == item["key"]:
            st.info(item["answer"])
            st.markdown("---")

    st.markdown("### 📞 Contact Support")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("---")
        st.markdown("📧 Email:")
        st.code("fixmycampus@mitmeerut.ac.in")

        st.markdown("📱 Phone:")
        st.code("+91 96936 83039")
        st.code("+91 97253 58432")
        st.code("+91 72504 06015")

    with col2:
        st.markdown("---")
        st.markdown("🏢 Office Address:")
        st.write("Room no-201, 2nd floor, Block-A\nMIT Meerut Campus\nUttar Pradesh, India")

    st.markdown("### 💬 Chat Assistant (Coming Soon)")
    st.info("Hello! I'm your FixMyCampus assistant bot. This feature will be live soon 😉")

#-----------------Home-----------------------
def home():
    user_name = st.session_state.user if "user" in st.session_state else "Guest"

    st.markdown(f"""
        <style>
            .home-hero {{
                background: linear-gradient(135deg, #6D28D9, #9333EA, #D946EF);
                padding: 3.5rem 2rem;
                border-radius: 25px;
                text-align: center;
                color: #fff;
                box-shadow: 0 15px 40px rgba(0,0,0,0.3);
                animation: fadeIn 1s ease;
                margin-bottom: 3rem;
            }}
            .home-section {{
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(15px);
                border-radius: 20px;
                padding: 2rem;
                margin-bottom: 2.5rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }}
            .home-title {{
                font-size: 30px;
                font-weight: 700;
                color: #F9FAFB;
                text-shadow: 0 0 10px rgba(255,255,255,0.6);
                margin-bottom: 0.8rem;
            }}
            .home-text {{
                font-size: 18px;
                line-height: 1.7;
                color: #D1D5DB;
                text-shadow: 1px 1px 4px rgba(0,0,0,0.8);
            }}
            .cta {{
                margin-top: 2rem;
            }}
            .cta button {{
                background: #9333EA;
                color: white;
                font-weight: bold;
                padding: 0.8rem 1.8rem;
                border: none;
                border-radius: 50px;
                font-size: 16px;
                box-shadow: 0 8px 20px rgba(147, 51, 234, 0.4);
                transition: all 0.3s ease-in-out;
            }}
            .cta button:hover {{
                background: #7e22ce;
                transform: scale(1.05);
                cursor: pointer;
            }}
            @keyframes fadeIn {{
                from {{opacity: 0;}}
                to {{opacity: 1;}}
            }}
        </style>

        <div class="home-hero">
            <h1>Welcome, {user_name}! 🎓</h1>
            <p style="font-size:20px;">You're on FixMyCampus – report, track, and resolve campus issues effortlessly.</p>
        </div>
    """, unsafe_allow_html=True)

#---------------------About----------------
def about():
    st.markdown("""
        <style>
            .hero-section {
                background-image: linear-gradient(to right top, #14338e, #006fca, #00a2c2, #00cd7f, #a6eb12);
                padding: 3rem 1.5rem;
                border-radius: 30px;
                color: white;
                text-align: center;
                margin-bottom: 3rem;
                box-shadow: 0 12px 30px rgba(0,0,0,0.3);
                font-size: 22px;
                height:180px;
                opacity:0.8;
            }
            .info-card {
                background: rgba(255, 255, 255, 0.1);
                padding: 2rem;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.25);
                margin-bottom: 2rem;
                transition: transform 0.3s ease-in-out;
            }
            .info-card:hover {
                transform: translateY(-10px);
            }
            .info-title {
                color: #ffffff;
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 1rem;
                text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.5);
            }
            .info-text {
                color: #d1d7ff;
                font-size: 20px;
                line-height: 1.8;
                text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
            }
            #about-fixmycampus{
                margin-top:-50px;}
            @keyframes fadeIn {
                from {
                    opacity: 0;
                }
                to {
                    opacity: 1;
                }
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="hero-section">
            <h1>About FixMyCampus</h1>
            <p>Your trusted platform for transparent campus issue reporting and resolution.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown('<div class="info-title">🚀 What is FixMyCampus?</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-text">FixMyCampus is a platform designed to help students report infrastructure issues such as electricity, water, internet, cleanliness, and more. We aim to ensure transparency and efficient resolutions for a better campus experience.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown('<div class="info-title">📊 Why Use FixMyCampus?</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-text">FixMyCampus makes it easy for students to track the status of their complaints. No more wondering what happened to your report. Everything is tracked, and you get notified as your issues progress.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown('<div class="info-title">🛠 Categories Covered</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="info-text">
        - ⚡ Electricity Issues<br>
        - 🚰 Water Supply Problems<br>
        - 🌐 Internet/Network Complaints<br>
        - 🧹 Cleanliness Requests<br>
        - 🚪 Furniture & Facility Damage<br>
        - 🚌 Transport or Bus Issues<br>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown('<div class="info-title">📈 Transparency & Trust</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-text">Each report is given a unique ID and logged into our system. You can track the progress of your complaint and view updates in real-time. Our system ensures accountability and transparency for every issue raised.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown('<div class="info-title">🤝 Together, We Improve Campus Life</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-text">FixMyCampus is more than just a platform for reporting issues; its a community-driven initiative to improve campus facilities and student life. Your voice matters, and together we can make a difference.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

#-------------------------------------- Main page ----------------
if st.session_state.page not in ["login", "signup"]:
    st.sidebar.markdown("""
        <style>
        .eu6p4el3
            {
                margin-top:-40px;
            }
        .eht7o1d1,.e19011e68
            {
                background-color:blue;
            }
        .eht7o1d1
            {
                background-image:url("https://cdn.pixabay.com/photo/2023/08/14/15/42/milkyway-8190232_1280.jpg");
                background-size: cover; 
                background-repeat: no-repeat; 
                background-position: center;
                opacity:1;
            }
        .e19011e68
            {    
                background-image:url("https://cdn.pixabay.com/photo/2023/08/14/15/42/milkyway-8190232_1280.jpg");
                background-size: cover; 
                background-repeat: no-repeat;  
                opacity:0.9;
            }
        .e4hpqof0
            {
                margin-top:-140px;
                background-image:url("https://as2.ftcdn.net/v2/jpg/06/34/14/27/1000_F_634142702_krpVzitHatLALEzzwN5TXBJGr8JeOr1C.jpg");
            }
        .flex-column
                        {
                        background-color:#333;
                        }
        </style>
    """,unsafe_allow_html=True)

    with st.sidebar:
        st.session_state.page=option_menu(
        "FixMyCampus",
        [
            "🏠 Home",
            "📌 Institute Info",
            "📝 Report an Issue",
            "📋 My Issue",
            "📊 Issue Status",
            "👤 View Profile",
            "🔐 Change Password",
            "💬 Help & Support",
            "🏫 About",
            "🚪 Logout"
        ],
            icons=["none"]*10,
            menu_icon="cast",
            default_index=0,
        )

#----------------------------------- PAGE ROUTING ---------------------------------
if st.session_state.page == "login":
    login()

elif st.session_state.page == "📌 Institute Info":
    about_campus()

elif st.session_state.page == "signup":
    sign_up()

elif st.session_state.page == "👤 View Profile":
    view_profile()
    
elif st.session_state.page == "📝 Report an Issue":
    report_issue()   
    
elif st.session_state.page == "📋 My Issue":
    my_issue()    

elif st.session_state.page =="🔐 Change Password":
    change_password()    
 
elif st.session_state.page == "🏠 Home":
    home()
elif st.session_state.page == "📊 Issue Status":
    issue_dashboard()
    issue_status()     

elif st.session_state.page == "💬 Help & Support":
    help_support_page()
               
elif st.session_state.page=="🚪 Logout":
    st.session_state.clear()
    st.session_state.page = "login"
    st.rerun()
elif st.session_state.page=="🏫 About":
    about()
