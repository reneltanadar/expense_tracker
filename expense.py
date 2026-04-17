from db import connect_db
from datetime import datetime
import csv                                # export_to_csv function
import pandas as pd                       # export_to_excel function
import matplotlib.pyplot as plt           # for show_pie_chart function

CATEGORIES = ["Food", "Travel", "Shopping", "Bills"]


# code to add expenses
from db import connect_db
from datetime import datetime

CATEGORIES = ["Food", "Travel", "Shopping", "Bills"]

def add_expense(user_id, amount, category, date):
    
    #  Amount validation
    try:
        amount = float(amount)
    except ValueError:
        return "Invalid amount!"

    # Category validation
    if category not in CATEGORIES:
        return "Invalid category!"

    #  Date validation
    try:
        date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return "Invalid date format!"

    conn = connect_db()
    cursor = conn.cursor()

    #  Insert expense
    cursor.execute(
        "INSERT INTO expenses (user_id, amount, category, date) VALUES (%s, %s, %s, %s)",
        (user_id, amount, category, date)
    )
    conn.commit()

    #  TOTAL SPENT THIS MONTH
    cursor.execute("""
        SELECT SUM(amount)
        FROM expenses
        WHERE user_id=%s AND MONTH(date)=MONTH(CURDATE()) AND YEAR(date)=YEAR(CURDATE())
    """, (user_id,))
    
    total_result = cursor.fetchone()
    total = total_result[0] if total_result and total_result[0] else 0

    # USER BUDGET
    cursor.execute("SELECT budget FROM users WHERE id=%s", (user_id,))
    budget_result = cursor.fetchone()
    budget = budget_result[0] if budget_result and budget_result[0] else 0

    conn.close()

    total = float(total)
    budget = float(budget)

    #  Budget check
    if budget>0 and total > budget:
        return f"⚠️ You exceeded budget by ₹{total - budget}"

    return "Expense added successfully!"


# code to view expenses
def view_expense(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, amount, category, date FROM expenses WHERE user_id=%s",
        (user_id,)
    )

    results = cursor.fetchall()
    conn.close()

    if not results:
        return []

    return results

# code to view monthly expenses
def monthly_summary(user_id):
    month = input("Enter month (1-12): ")

    #  validation 
    if not month.isdigit() or int(month) < 1 or int(month) > 12:
        print("Invalid month!")
        return

    conn = connect_db()
    cursor = conn.cursor()

    # total expenses for the selected month
    query_total = """
    SELECT SUM(amount)
    FROM expenses
    WHERE user_id=%s AND MONTH(date)=%s AND
    YEAR(date)=YEAR(CURDATE())
    """
    cursor.execute(query_total, (user_id, month))
    total = cursor.fetchone()[0]

    if total is None:
        total = 0

    print(f"\nTotal Spending of Month {month}: ₹{total}")

    # category-wise spending
    query_cat = """
    SELECT category, SUM(amount)
    FROM expenses
    WHERE user_id=%s AND MONTH(date)=%s
    GROUP BY category
    """
    cursor.execute(query_cat, (user_id, month))
    results = cursor.fetchall()

    print("\nCategory-wise Spending:")
    
    if not results:
        print("No data for this month")
    else:
        for row in results:
            print(f"{row[0]}: ₹{row[1]}")

    conn.close()

# CODE FOR USER SETTING THEIR BUDGET
def set_budget(user_id, budget):
    conn = connect_db()
    cursor = conn.cursor()

    query = "UPDATE users SET budget=%s WHERE id=%s"
    cursor.execute(query, (budget, user_id))

    conn.commit()
    conn.close()

    return "success"



# code for insights
def show_insights(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    # 1. Highest spending category
    query1 = """
    SELECT category, SUM(amount) as total
    FROM expenses
    WHERE user_id=%s
    GROUP BY category
    ORDER BY total DESC
    LIMIT 1
    """
    cursor.execute(query1, (user_id,))
    result1 = cursor.fetchone()

    # 2. Daily average spending
    query2 = """
    SELECT AVG(daily_total)
    FROM (
        SELECT SUM(amount) as daily_total
        FROM expenses
        WHERE user_id=%s
        GROUP BY date
    ) as temp
    """
    cursor.execute(query2, (user_id,))
    result2 = cursor.fetchone()[0]

    conn.close()

    insights = {}

    if result1:
        insights["top_category"] = f"{result1[0]} (₹{result1[1]})"
    else:
        insights["top_category"] = "No data"

    if result2:
        insights["avg_daily"] = round(result2, 2)
    else:
        insights["avg_daily"] = 0

    return insights

# code for smart trend and suggestions
def spending_trend(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    # current
    cursor.execute("""
        SELECT SUM(amount)
        FROM expenses
        WHERE user_id=%s AND MONTH(date)=MONTH(CURDATE())
    """, (user_id,))
    current = cursor.fetchone()[0] or 0

    # previous
    cursor.execute("""
        SELECT SUM(amount)
        FROM expenses
        WHERE user_id=%s 
        AND MONTH(date)=MONTH(CURRENT_DATE - INTERVAL 1 MONTH)
        AND YEAR(date)=YEAR(CURRENT_DATE - INTERVAL 1 MONTH)
    """, (user_id,))
    previous = cursor.fetchone()[0] or 0

    result = {}

    result["current"] = current
    result["previous"] = previous

    if previous > 0:
        change = ((current - previous) / previous) * 100

        if change > 0:
            result["message"] = f"📈 {round(change,2)}% more spending"
        elif change < 0:
            result["message"] = f"📉 {abs(round(change,2))}% less spending"
        else:
            result["message"] = "No change"
    else:
        result["message"] = "No previous data"

    # suggestion
    cursor.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        WHERE user_id=%s AND MONTH(date)=MONTH(CURDATE())
        GROUP BY category
        ORDER BY SUM(amount) DESC
        LIMIT 1
    """, (user_id,))
    res = cursor.fetchone()

    result["suggestion"] = f"Reduce {res[0]}" if res else "No suggestion"

    conn.close()
    return result


#code for monthly report of expenses
def monthly_report(user_id, month):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(amount)
        FROM expenses
        WHERE user_id=%s AND MONTH(date)=%s
    """, (user_id, month))
    total = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        WHERE user_id=%s AND MONTH(date)=%s
        GROUP BY category
        ORDER BY SUM(amount) DESC
    """, (user_id, month))
    data = cursor.fetchall()

    cursor.execute("""
        SELECT AVG(daily_total)
        FROM (
            SELECT SUM(amount) as daily_total
            FROM expenses
            WHERE user_id=%s AND MONTH(date)=%s
            GROUP BY date
        ) temp
    """, (user_id, month))
    avg = cursor.fetchone()[0] or 0

    conn.close()

    return {
        "total": total,
        "categories": data,
        "top": data[0] if data else None,
        "avg": round(avg, 2)
    }


# code for data to be save in an excel file
def export_to_csv(user_id, month=None):
    conn = connect_db()
    cursor = conn.cursor()

    if month:
        cursor.execute("""
            SELECT amount, category, date
            FROM expenses
            WHERE user_id=%s AND MONTH(date)=%s
        """, (user_id, month))
        file = f"static/month_{month}.csv"
    else:
        cursor.execute("""
            SELECT amount, category, date
            FROM expenses
            WHERE user_id=%s
        """, (user_id,))
        file = "static/all.csv"

    data = cursor.fetchall()

    import csv
    with open(file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Amount", "Category", "Date"])
        writer.writerows(data)

    conn.close()
    return file

# code to export as excel
def export_to_excel(user_id, month=None):
    import pandas as pd

    conn = connect_db()

    if month:
        query = """
        SELECT amount, category, date
        FROM expenses
        WHERE user_id=%s AND MONTH(date)=%s
        """
        df = pd.read_sql(query, conn, params=(user_id, month))
        file = f"static/month_{month}.xlsx"
    else:
        query = "SELECT amount, category, date FROM expenses WHERE user_id=%s"
        df = pd.read_sql(query, conn, params=(user_id,))
        file = "static/all.xlsx"

    df.to_excel(file, index=False)
    conn.close()

    return file

# code for searching and filtering
def search_expenses(user_id, category=None, month=None):
    conn = connect_db()
    cursor = conn.cursor()

    query = "SELECT id, amount, category, date FROM expenses WHERE user_id=%s"
    params = [user_id]

    if category:
        query += " AND category=%s"
        params.append(category)

    if month:
        query += " AND MONTH(date)=%s"
        params.append(int(month))

    query += " ORDER BY date DESC"

    cursor.execute(query, tuple(params))
    results = cursor.fetchall()

    total = sum(row[1] for row in results) if results else 0

    conn.close()
    return results, total


# code for pie chart(Category totals)
def get_category_totals(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    query = """
    SELECT category, SUM(amount)
    FROM expenses
    WHERE user_id=%s
    GROUP BY category
    """
    cursor.execute(query, (user_id,))
    data = cursor.fetchall()

    conn.close()
    return data


# code for line graph(daily totals)
def get_daily_totals(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    query = """
    SELECT date, SUM(amount)
    FROM expenses
    WHERE user_id=%s
    GROUP BY date
    ORDER BY date
    """
    cursor.execute(query, (user_id,))
    data = cursor.fetchall()

    conn.close()
    return data


# code for getting all the expenses
def get_all_expenses(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    query = "SELECT amount, category, date FROM expenses WHERE user_id=%s"
    cursor.execute(query, (user_id,))
    data = cursor.fetchall()

    conn.close()
    return data



# code for displaying pie chart
def show_pie_chart(user_id, month):
    conn = connect_db()
    cursor = conn.cursor()

    query = """
    SELECT category, SUM(amount)
    FROM expenses
    WHERE user_id=%s AND MONTH(date)=%s
    GROUP BY category
    """
    cursor.execute(query, (user_id, month))
    data = cursor.fetchall()

    conn.close()

    if not data:
        return None

    categories = [row[0] for row in data]
    amounts = [float(row[1]) for row in data]

    plt.figure()
    plt.pie(amounts, labels=categories, autopct='%1.1f%%')
    plt.title(f"Expense Distribution (Month {month})")

    path = "static/pie_chart.png"
    plt.savefig(path)
    plt.close()

    return path


# code for displaying line chart
def show_line_graph(user_id, month):
    conn = connect_db()
    cursor = conn.cursor()

    query = """
    SELECT date, SUM(amount)
    FROM expenses
    WHERE user_id=%s AND MONTH(date)=%s
    GROUP BY date
    ORDER BY date
    """
    cursor.execute(query, (user_id, month))
    data = cursor.fetchall()

    conn.close()

    if not data:
        return None

    dates = [str(row[0]) for row in data]
    amounts = [float(row[1]) for row in data]

    plt.figure()
    plt.plot(dates, amounts, marker='o')

    plt.title(f"Spending Trend (Month {month})")
    plt.xlabel("Date")
    plt.ylabel("Amount")

    plt.xticks(rotation=45)
    plt.tight_layout()

    path = "static/line_chart.png"
    plt.savefig(path)
    plt.close()

    return path


def delete_expense(expense_id, user_id):
    conn = connect_db()
    cursor = conn.cursor()

    query = "DELETE FROM expenses WHERE id=%s AND user_id=%s"
    cursor.execute(query, (expense_id, user_id))

    conn.commit()
    conn.close()

    return "deleted"