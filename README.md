# Market research project

To the next developer that takes over this project, here are some important considerations and guidelines to ensure a smooth setup and maintenance of the infrastructure. This project requires careful attention to detail during the initial setup phase, as well as ongoing management to keep everything running smoothly.

In the following sections, you will find detailed instructions on how to properly configure the environment, set up necessary dependencies, and manage the infrastructure effectively. Following these guidelines will help you avoid common pitfalls and ensure that the project remains stable and maintainable.

## Excel workbook

The `aggregate_reports()` function is responsible for creating the Excel workbook using the `.csv` files from the reports. In case you ever need to change anything, be aware of the following:

1. The goal of the sheets is to be as connected as possible, the main sheet is the `Coleta_Mes` sheet and will sometimes suffer manual corrections. The other sheets should never need any manual change, since the changes must be propagated to them via formulas.
2. To create the workbook, `XlsxWriter` is being used. It has some behaviors that you need to pay attention to:
   1. The dynamic array formulas must be created with `worksheet.write_dynamic_array_formula()`.
   2. The spill range operator, like `A2#`, must be referenced with `ANCHORARRAY(A2)`.
   3. `pd.ExcelWriter` must be passed engine kwargs to prevent newer functions not being interpreted correctly.
   4. Sometimes the formulas end up being interpreted as implicit intersection, you can use `SINGLE()` to prevent this behavior.

## AWS costs and free tier

This project relies heavily on the free tier of EC2 with EBS and Lambda. EC2 has 12 months free tier which is a yearly maintenance for the project developer. Just create a new account and use the free tier again.

That said, the only cost that this project is supposed to possibly have is if the data sent out of the server is bigger than the free tier limit (always check if there were any changes to the billing policy). Ways to decrease or eliminate this cost are explained in the following sections.

## Clientside callbacks and authentication

To prevent possibly having a large AWS bill, the data being sent out of EC2 must be minimized. To achieve this:

1. Clientside callbacks were used because they do not send or receive data from the EC2 server. Some functions still had to be server callbacks because they either need to send data or need to create components dynamically (although I imagine it is possible to do this).
2. `dash_auth` was used to prevent page load and minimize data sent out from the server to people who are not involved in the project. Considerations about the user/password duo is explained in the next section.
3. One common mistake when creating callbacks in dash is not understanding the order in which the callbacks are called. Sometimes they are not even constant. One way to handle this is to use dummy inputs and outputs. If only one function outputs to a dummy container, then you can use as an input for a callback you want executed later.

## Environment file

If you see in the `main.py` script, I made calls `getenv()`. This function is using a `.env` file in my directory to load certain variables. This file must **NEVER** be publicly available. In case it ever is, change all passwords and authentication tokens immediately. This file must be passed to EC2 manually and not via GitHub.

## AWS deployment to EC2

## Upload to OneDrive with AWS Lambda
