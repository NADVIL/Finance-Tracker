import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import os

# --- Configuration ---
st.set_page_config(page_title="💸 Finance Tracker", layout="centered", page_icon="💸")
st.title("💸 Personal Finance Tracker")
st.markdown("Track income, expenses, and savings with insights & goals.")

# --- Session State Initialization ---
if "expense_data" not in st.session_state:
    st.session_state.expense_data = []
if "categories" not in st.session_state:
    st.session_state.categories = ["Rent", "Food", "Clothing", "Transport", "Utilities", "Entertainment", "Others"]

# --- Select Month ---
st.sidebar.header("📅 Select Month")
selected_month = st.sidebar.date_input("Month", datetime.date.today().replace(day=1))

# --- Income Section ---
st.sidebar.header("🧮 Income Details")
income_sources = {}
for source in ["Salary", "Freelance", "Investments"]:
    income_sources[source] = st.sidebar.number_input(f"{source} Income (₹)", min_value=0, step=100, key=source)
total_income = sum(income_sources.values())

saving_goal = st.sidebar.number_input("Saving Goal (₹)", min_value=0, step=100)

# --- Custom Categories ---
st.sidebar.header("➕ Manage Categories")
new_cat = st.sidebar.text_input("Add a Category")
if st.sidebar.button("Add Category"):
    if new_cat and new_cat not in st.session_state.categories:
        st.session_state.categories.append(new_cat)

# --- Expense Form ---
st.subheader("🧾 Enter Your Monthly Expenses")
expenses = {}
budgets = {}
with st.form("expenses_form"):
    for category in st.session_state.categories:
        expenses[category] = st.number_input(f"{category} (₹):", min_value=0, step=100, key=category)
        budgets[category] = st.number_input(f"{category} Budget (₹):", min_value=0, step=100, key=f"budget_{category}")
    submitted = st.form_submit_button("📊 Show Finance Summary")

if submitted:
    total_expense = sum(expenses.values())
    remaining = total_income - total_expense - saving_goal
    saving_percent = (saving_goal / total_income * 100) if total_income else 0

    # --- Save data ---
    entry = {
        "Month": selected_month.strftime("%Y-%m"),
        "Income": total_income,
        "Saving Goal": saving_goal,
        "Total Expenses": total_expense,
        "Remaining": remaining,
        "Saving %": saving_percent,
        **expenses
    }
    st.session_state.expense_data.append(entry)

    # --- Summary ---
    st.markdown("## 📋 Finance Summary")
    col1, col2 = st.columns(2)
    col1.metric("Total Income", f"₹{total_income}")
    col1.metric("Total Expenses", f"₹{total_expense}")
    col2.metric("Saving Goal", f"₹{saving_goal}")
    col2.metric("Remaining Balance", f"₹{remaining}")

    st.progress(min(saving_percent / 100, 1.0), text=f"Savings: {saving_percent:.1f}%")

    # --- Tips ---
    st.markdown("### 📌 Smart Tips")
    if total_income == 0:
        st.warning("⚠ Please enter a valid income.")
    elif total_expense > total_income:
        st.error("🚨 You're spending more than you earn!")
    elif saving_percent < 20:
        st.warning("⚠ Try to save at least 20% of your income.")
    else:
        st.success("✅ Great job! You're managing your finances well.")

    for category in st.session_state.categories:
        if budgets[category] > 0 and expenses[category] > budgets[category]:
            st.warning(f"⚠ Over budget in {category} by ₹{expenses[category] - budgets[category]}")

    # --- Spending Breakdown ---
    st.markdown("### 📊 Spending Breakdown")
    if total_expense > 0:
        fig, ax = plt.subplots()
        ax.pie(expenses.values(), labels=expenses.keys(), autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)
    else:
        st.info("Enter expenses to see the chart.")

# --- History Table ---
st.markdown("## 📅 Monthly History")
if st.session_state.expense_data:
    df = pd.DataFrame(st.session_state.expense_data)
    st.dataframe(df, use_container_width=True)

    # --- Export CSV ---
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📤 Export to CSV", csv, "finance_data.csv", "text/csv")
else:
    st.info("No data yet. Submit this month's report to start tracking.")
