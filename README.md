# Market research project

- [Market research project](#market-research-project)
  - [Personal Domain](#personal-domain)
  - [Cloudflared and Failover](#cloudflared-and-failover)
  - [Excel workbook](#excel-workbook)
  - [Clientside callbacks and authentication](#clientside-callbacks-and-authentication)
    - [Further improving speed with event listeners](#further-improving-speed-with-event-listeners)
  - [Configuration files](#configuration-files)
  - [Environment file](#environment-file)
  - [Minify assets](#minify-assets)
  - [End-to-end testing](#end-to-end-testing)
    - [Testing environment and fixtures](#testing-environment-and-fixtures)

To the next developer that takes over this project, here are some important considerations and guidelines to ensure a smooth setup and maintenance of the infrastructure. This documentation is for version 2 of the project, which introduced significant breaking changes to:

1. Simplify configuration by non-technical people.
2. Move from an AWS architecture to a redundant self-hosted architecture.
3. Allow for products to appear in multiple pages.
4. Cleaner and more pleasing user interface.

In the following sections, you will find detailed instructions on how to properly configure the environment, set up necessary dependencies, and manage the infrastructure effectively. Following these guidelines will help you avoid common pitfalls and ensure that the project remains stable and maintainable. However, **DO NOT** follow this guide blindly and always study what every configuration and instruction is doing.

Variables that you will need to set up will be indicated by: `<var1>`.

## Personal Domain

To make the application accessible, the recommended way for users to connect is via a **web domain**. A personal domain is recommended because it:

- Allows easy creation of multiple subdomains.
- Integrates with Cloudflare for **failover, usability, and security** (traffic points to Cloudflare, not directly to your server).
- Is inexpensive compared to the flexibility it provides.

## Cloudflared and Failover

For redundancy in case of **internet or power loss**, we run Cloudflared (reverse proxy) on two or more machines hosting the application.

- Each Cloudflared instance connects to the same Cloudflare Tunnel.
- Multiple instances act as **replicas**, providing additional ingress points.
- Cloudflare routes requests to the replica **closest to the user geographically**.
- In our setup, replicas are **for failover only**, not load balancing.

Because replicas are rarely used, they can run on **low-resource machines** (e.g., older hardware) located outside the main operating region. Do note that Cloudflare has excellent guides on how to set this up.

## Excel workbook

The `aggregate_reports()` function is responsible for creating the Excel workbook using the `.csv` files from the reports. In case you ever need to change anything, be aware of the following:

1. The goal of the sheets is to be as connected as possible, the main sheet is the `Coleta_Mes` sheet and will sometimes suffer manual corrections. The other sheets should never need any manual change, since the changes must be propagated to them via formulas.
2. To create the workbook, `XlsxWriter` is being used. It has some behaviors that you need to pay attention to:
   1. The dynamic array formulas must be created with `worksheet.write_dynamic_array_formula()`.
   2. The spill range operator, like `A2#`, must be referenced with `ANCHORARRAY(A2)`.
   3. `pd.ExcelWriter` must be passed engine kwargs to prevent newer functions not being interpreted correctly.
   4. Sometimes the formulas end up being interpreted as implicit intersection, you can use `SINGLE()` to prevent this behavior.

## Clientside callbacks and authentication

To increase performance of the application, and decrease the load on the server as much as possible, we can do the following:

1. Clientside callbacks were used because they do not send or receive data from the server. Some functions still had to be server callbacks because they need to send data from the server.
2. `dash_auth` was used to prevent page load and minimize data sent out from the server to people who are not involved in the project. Considerations about the user/password duo is explained in the next section.
3. Administration pages receive a secondary password stored in the `.env` file under the `ADM_PASSWORD` key, so that users are blocked from using them.

### Further improving speed with event listeners

While Dash's clientside callbacks offer solid performance for front-end interactivity, we found that directly attaching native JavaScript event listeners to DOM elements (e.g., input, select, button) significantly improved responsiveness and reduced execution overhead. By bypassing Dash’s callback lifecycle and directly responding to events like input, click, and change, we eliminated redundant updates and avoided callback chaining delays.

This change reduced per-interaction latency from ~25–100ms to <1ms, especially in high-frequency UI scenarios (e.g., typing, dynamically adding product rows, or toggling collapsibles). Additionally, the event-driven structure gave us finer control over validation triggers, badge/icon updates, and visual transitions. It's especially beneficial in scenarios where DOM visibility (e.g., collapsed rows becoming visible) and readiness must be manually tracked.

## Configuration files

- `estabelecimentos.db` - The establishments that are used in the callbacks. Also used for locating the nearest establishment using Haversine distance and outputting the address.
- `marcas.db` - The brands for each product that are used in the callbacks.
- `products.db` - The products and their configurations.
- `CONFIG.py` - Configurations that are available to python files and clientside callbacks, this was done to ensure there weren't two configuration files.

## Environment file

If you see in the `main.py` script, I made calls `getenv()`. This function is using a `.env` file in my directory to load certain variables. This file must **NEVER** be publicly available. In case it ever is, change all passwords and authentication tokens immediately. This file must be passed configured manually and not via GitHub. It has the following parameters:

- `SECRET_KEY` - String used for security-related operations of the Flask server that the app uses.
- `APP_USERNAME` - Username for the initial app log in.
- `APP_PASSWORD` - Password for the initial app log in.
- `ADM_PASSWORD` - Password for administration pages.
- `TEST` - Server initialization parameter (`reloader`, `debug` or empty).

## Minify assets

In order to decrease outgoing data from the application server, minifying the assets can decrease the data sent from the server to the user. SVG, CSS and Javascript files can be minified before setting up the web server. However, this is not strictly necessary, since the assets will be compressed by the Nginx server. Minifying will help decrease the size a little, although compression seems to be enough.

It is worth noting that partially minifying the assets is a good alternative. Simply avoid spaces and newlines when possible. Personally, I remove spaces and newlines on parts of the code that will not make the code overly cluttered and hard to read.

## End-to-end testing

End-to-end testing is essential for ensuring that our Dash application works correctly from the user's perspective. This involves testing the complete functionality of the app, including user interactions, data processing, and visual feedback. The goal is to simulate real-world usage and catch any issues that might not be evident through unit tests alone.

### Testing environment and fixtures

To make the testing as realistic as possible, the tests are setup using the same process that is done for the EC2 server. That involves setting up a Gunicorn server and the Selenium configuration. The setup is done using Pytest fixtures, which allow, for example, the server being used by all tests in the module.

To simply using Selenium, we use `chromedriver_autoinstaller` to manage the ChromeDriver automatically. This ensures that the correct version of ChromeDriver is always available. If you manually close a browser window started by the Selenium, it is possible that the `chromedriver` file will be occupied and therefore not available to be used by the tests. To solve this, use `fuser <path-to-chromedriver>`. It will give you a list of processes using the file, which you can then use to find and terminate.

Also note that the `app()` fixture tries to get the website three times. The first is to get authenticated and save the credentials as cookies. The second and third are to get the site as it normally would be like.

The `@mark.incremental` fixture works by performing the tests in a class sequentially. If a test fails, all further tests get skipped, due to their incremental nature. While this is not how PyTest is usually used, it is a good way to test how the app behaves in a scenario where multiple actions happen sequentially.
