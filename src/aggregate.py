from tools import aggregate_reports, delete_old_reports

if __name__ == "__main__":
    year = input("Enter the year: ")
    month = input("Enter the month: ")
    aggregate_reports([year, month])
    delete_old_reports()
