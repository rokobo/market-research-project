from tools import aggregate_reports, delete_old_reports, check_reports

if __name__ == "__main__":
    print(check_reports())
    proceed = input("Gostaria de continuar, mesmo com os erros acima? (y/n): ")
    if proceed == "y":
        year = input("Enter the year: ")
        month = input("Enter the month: ")
        aggregate_reports([year, month])
        delete_old_reports()
