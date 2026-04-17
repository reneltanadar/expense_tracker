from auth import register, login
from expense import add_expense, view_expense,monthly_summary,set_budget,show_insights,spending_trend,monthly_report
from expense import export_to_csv,export_to_excel,search_expenses,show_pie_chart,show_line_graph


def user_menu(user_id):
    while True:
        print("\n========== DASHBOARD ==========")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Monthly Summary")
        print("4. Set Budget")
        print("5. Show Insights")
        print("6. Spending Trend")
        print("7. Monthly Report")
        print("8. Export to CSV")
        print("9. Export to Excel")
        print("10. Search/Filter")
        print("11. Pie Chart")
        print("12. Line Graph")
        print("13. Logout")

        option = input("Enter choice: ")

        if option == "1":
            add_expense(user_id)

        elif option == "2":
            view_expense(user_id)

        elif option == "3":
            monthly_summary(user_id)

        elif option == "4":
            set_budget(user_id)

        elif option == "5":
            show_insights(user_id)

        elif option == "6":
            spending_trend(user_id)

        elif option == "7":
            monthly_report(user_id)

        elif option == "8":
            export_to_csv(user_id)

        elif option == "9":
            export_to_excel(user_id)

        elif option == "10":
            search_expenses(user_id)

        elif option == "11":
            show_pie_chart(user_id)

        elif option == "12":
            show_line_graph(user_id)

        elif option == "13":
            print("Logged out successfully!")
            break

        else:
            print("Invalid choice!")

        input("\nPress Enter to continue...")


#  MAIN MENU
def main():
    print("Welcome to Smart Expense Tracker")

    while True:
        print("\n========== MAIN MENU ==========")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            register()

        elif choice == "2":
            user_id = login()
            if user_id:
                user_menu(user_id)

        elif choice == "3":
            print("Goodbye!")
            break

        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()