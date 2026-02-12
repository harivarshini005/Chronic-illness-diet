# ==========================================
# AI DIET PLANNER FOR DIABETES (FINAL PROJECT)
# ==========================================

import streamlit as st
import pandas as pd
import pickle
import plotly.express as px

# PDF libraries
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Diet Planner for Diabetes", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
.card {
    background-color:white;
    padding:20px;
    border-radius:12px;
    box-shadow:0px 4px 12px rgba(0,0,0,0.1);
    margin-bottom:15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD MODEL & DATA ----------------
model = pickle.load(open("diet_model.pkl", "rb"))
label_encoder = pickle.load(open("label_encoder.pkl", "rb"))
model_features = pickle.load(open("model_features.pkl", "rb"))
food_df = pd.read_csv("pred_food.csv")
food_df = food_df.drop_duplicates(subset=["Food Name"])

# ---------------- FUNCTIONS ----------------
def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

# ---------------- HEADER ----------------
st.markdown("""
<div class="card">
<h1>🥗 AI Diet Planner for Diabetes</h1>
<p>Personalized diet recommendations using Machine Learning</p>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR PATIENT DETAILS ----------------
st.sidebar.header("🧍 Patient Details")
age = st.sidebar.slider("Age", 18, 80, 30)
bmi = st.sidebar.slider("BMI", 15.0, 40.0, 23.0)
bp = st.sidebar.slider("Blood Pressure (mmHg)", 90, 180, 120)
glucose = st.sidebar.slider("Glucose (mg/dL)", 70, 300, 120)
cholesterol = st.sidebar.slider("Cholesterol (mg/dL)", 100, 300, 180)

predict_btn = st.sidebar.button("🔍 Predict Diet")

# ---------------- MAIN ----------------
if predict_btn:

    # Feature engineering
    raw_input = pd.DataFrame([{
        "Age": age,
        "BMI_Category": bmi_category(bmi),
        "Disease_Type": "Diabetes",
        "Severity": "Moderate",
        "Physical_Activity_Level": "Medium",
        "High_Glucose": int(glucose > 140),
        "High_BP": int(bp > 130),
        "High_Cholesterol": int(cholesterol > 200)
    }])

    input_data = pd.get_dummies(raw_input, drop_first=True)
    input_data = input_data.reindex(columns=model_features, fill_value=0)

    pred = model.predict(input_data)[0]
    diet = label_encoder.inverse_transform([pred])[0]

    # ---------------- TABS ----------------
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Result", "📈 Analysis", "🍽 Meal Plan", "📄 Download Report"])

    # ========== TAB 1 RESULT ==========
    with tab1:
        st.subheader("Prediction Summary")

        if diet == "Low_Carb":
            st.success("🥗 LOW CARB DIET")
        elif diet == "Low_Sodium":
            st.warning("🧂 LOW SODIUM DIET")
        else:
            st.info("⚖️ BALANCED DIET")

        # -------- AI Explanation --------
        st.subheader("AI Explanation")

        explanation = []

        if bmi > 25:
            explanation.append("BMI is elevated")
        else:
            explanation.append("BMI is normal")

        if glucose > 140:
            explanation.append("High glucose detected")
            explanation.append("Reduced carbohydrate intake recommended")
        else:
            explanation.append("Glucose level is normal")

        if bp > 130:
            explanation.append("Blood pressure is high")

        if cholesterol > 200:
            explanation.append("High cholesterol detected, reduce fatty foods")

        for e in explanation:
            st.write("• " + e)

        st.markdown("</div>", unsafe_allow_html=True)

    # ========== TAB 2 ANALYSIS ==========
    with tab2:
        st.subheader("Nutrient Distribution")

        if diet == "Low_Carb":
            chart_data = {"Carbohydrates": 30, "Protein": 40, "Fat": 30}
        elif diet == "Low_Sodium":
            chart_data = {"Carbohydrates": 50, "Protein": 30, "Fat": 20}
        else:
            chart_data = {"Carbohydrates": 60, "Protein": 25, "Fat": 15}

        df_chart = pd.DataFrame(chart_data.items(), columns=["Nutrient", "Percentage"])
        fig = px.pie(df_chart, names="Nutrient", values="Percentage")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ========== TAB 3 MEAL PLAN ==========
    with tab3:
        st.subheader("📅 Sample Weekly Meal Plan")

        foods = food_df["Food Name"].sample(21).tolist()
        days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        meals = ["Breakfast","Lunch","Dinner"]

        plan = []
        idx = 0
        for d in days:
            for m in meals:
                plan.append({"Day": d, "Meal": m, "Food": foods[idx]})
                idx += 1

        plan_df = pd.DataFrame(plan)
        st.dataframe(plan_df)

        # Recommended foods
        st.subheader("✅ Recommended Foods")
        eat = food_df.sort_values(by=["Protein", "Fiber Content"], ascending=False).head(10)
        st.dataframe(eat[["Food Name", "Protein", "Fiber Content"]])

        # Foods to avoid
        st.subheader("🚫 Foods to Avoid")
        avoid = food_df.sort_values(by=["Carbohydrates", "Glycemic Index"], ascending=False).head(10)
        st.dataframe(avoid[["Food Name", "Carbohydrates", "Glycemic Index"]])

        st.markdown("</div>", unsafe_allow_html=True)

    # ========== TAB 4 DOWNLOAD PDF ==========
    with tab4:
        st.subheader("📄 Download Diet Report")

        def create_pdf(filename):
            styles = getSampleStyleSheet()
            doc = SimpleDocTemplate(filename, pagesize=letter)
            content = []

            content.append(Paragraph("AI Diet Planner Report", styles["Heading1"]))
            content.append(Spacer(1, 12))

            content.append(Paragraph(f"Age: {age}", styles["Normal"]))
            content.append(Paragraph(f"BMI: {bmi} ({bmi_category(bmi)})", styles["Normal"]))
            content.append(Paragraph(f"Glucose: {glucose} mg/dL", styles["Normal"]))
            content.append(Paragraph(f"Blood Pressure: {bp} mmHg", styles["Normal"]))
            content.append(Paragraph(f"Cholesterol: {cholesterol} mg/dL", styles["Normal"]))
            content.append(Spacer(1, 12))

            content.append(Paragraph(f"Recommended Diet: {diet}", styles["Heading2"]))
            content.append(Spacer(1, 12))

            content.append(Paragraph("Sample Weekly Meal Plan:", styles["Heading3"]))
            for i, row in plan_df.iterrows():
                content.append(Paragraph(f"{row['Day']} - {row['Meal']}: {row['Food']}", styles["Normal"]))

            doc.build(content)

        pdf_file = "diet_report.pdf"
        create_pdf(pdf_file)

        with open(pdf_file, "rb") as f:
            st.download_button("⬇️ Download PDF Report", f, file_name="diet_report.pdf")

        st.markdown("</div>", unsafe_allow_html=True)