from flask import Flask, render_template, request, redirect, url_for,session
from auth import register_user, login_user
from expense import add_expense, view_expense,search_expenses,show_line_graph,show_pie_chart
from expense import set_budget, show_insights,spending_trend,monthly_report,export_to_csv,export_to_excel
from expense import delete_expense
from db import connect_db

app = Flask(__name__)
app.secret_key= "secret123"

#  HOME
@app.route("/")
def home():
    return render_template("base.html")   


#  REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    message = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        result = register_user(username, password)

        if result == "exists":
            message = "Username already exists!"
        else:
            return redirect(url_for("login"))

    return render_template("register.html", message=message)


#  LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    message = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = login_user(username, password)

        if user_id:
            session["user_id"]= user_id
            session["username"]= username
            return redirect(url_for("dashboard"))
        else:
            message = "Invalid Username or Password!"

    return render_template("login.html", message=message)


# DASHBOARD

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    username = session.get("username")

    # ➕ ADD EXPENSE (from dashboard form)
    if request.method == "POST":
        amount = request.form["amount"]
        category = request.form["category"]
        date = request.form["date"]

        add_expense(user_id, amount, category, date)

    #filter
    category = request.args.get("category")
    month = request.args.get("month")

    # clean
    category = category if category else None
    month = month if month else None

    expenses = []
    total = 0

    # ONLY filter
    if category or month:
        expenses, total = search_expenses(user_id, category=category, month=month)





    #  view expwnses
    all_expenses = view_expense(user_id)
    all_total = sum(row[1] for row in all_expenses) if all_expenses else 0



    #  CHARTS
    chart_month = request.args.get("chart_month")
    pie_chart = None
    line_chart = None
    if chart_month:
        pie_chart = show_pie_chart(user_id, chart_month)
        line_chart = show_line_graph(user_id, chart_month)


    # get insights
    insights = show_insights(user_id)

    # get budget
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT budget FROM users WHERE id=%s", (user_id,))
    budget = cursor.fetchone()[0]

    conn.close()


    # spending trend
    trend = spending_trend(user_id)
    report = None
    report_month = request.args.get("report_month")

    if report_month:
        report = monthly_report(user_id, report_month)


    

    return render_template(
        "dashboard.html",
        username=username,
        expenses=expenses,
        total=total,
        pie_chart=pie_chart,
        line_chart=line_chart,
        insights=insights,
        budget=budget,
        trend=trend,
        report=report,
        all_expenses=all_expenses,
        all_total=all_total,

    )





# route for set budget
@app.route("/set-budget", methods=["POST"])
def set_budget_route():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    budget = request.form["budget"]

    set_budget(user_id, budget)

    return redirect(url_for("dashboard"))


#csv
@app.route("/export-csv")
def export_csv():
    user_id = session["user_id"]
    month = request.args.get("month")
    path = export_to_csv(user_id, month)
    return redirect("/" + path)

# excel
@app.route("/export-excel")
def export_excel():
    user_id = session["user_id"]
    month = request.args.get("month")
    path = export_to_excel(user_id, month)
    return redirect("/" + path)




# ai
@app.route("/ai-chat", methods=["POST"])
def ai_chat():

    if "user_id" not in session:
        return "⚠️ Login required"

    user_id = session["user_id"]
    msg = request.form.get("message", "").lower().strip()

    #  TOTAL
    if "total" in msg:
        data, total = search_expenses(user_id)
        return f"💰 You spent ₹{total} overall"

    #  CATEGORY
    elif "food" in msg:
        data, total = search_expenses(user_id, category="Food")
        return f"🍔 Food: ₹{total}"

    elif "travel" in msg:
        data, total = search_expenses(user_id, category="Travel")
        return f"✈️ Travel: ₹{total}"
    
    elif "shopping" in msg:
        data, total = search_expenses(user_id, category="Shopping")
        return f" Shopping: ₹{total}"

    elif "bills" in msg:
        data, total = search_expenses(user_id, category="Bills")
        return f" Bills: ₹{total}"


    #  MONTH
    elif "month" in msg:
        from datetime import datetime
        m = datetime.now().month
        data, total = search_expenses(user_id, month=m)
        return f" This month: ₹{total}"

    # TREND
    elif "trend" in msg:
        trend = spending_trend(user_id)
        return f"📈 {trend['message']}"

    #  SUGGESTION
    elif "suggest" in msg or "advice" in msg:
        insights = show_insights(user_id)
        return f"💡 Reduce spending on {insights['top_category']}"
    elif "hi" in msg or "hello" in msg:
         return (
            "Hello! How can i help you")
    #  DEFAULT
    else:
        return (
            "Sorry, I didn’t understand.\n"
            "Try asking:\n"
            "- total spending\n"
            "- food / travel / shopping / bills\n"
            "- this month\n"
            "- trend\n"
            "- suggestion"
        )
    

# logout
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("home"))


# delete expenses
@app.route("/delete-expense/<int:expense_id>", methods=["POST"])
def delete_expense_route(expense_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    delete_expense(expense_id, user_id)

    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)

    