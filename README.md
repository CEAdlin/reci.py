# reci.py - Recipe Website for Coders

[Live website](https://reci-py-93c536d719a2.herokuapp.com/).

## Screenshot

![](docs/overview.png)

## Design & Color Palette

The visual design is structured using a custom theme built over Bootstrap, prioritizing high contrast and a developer-centric layout using the **PT Serif** font family. The palette is defined as follows:

*   **Charcoal Blue (`#264653`)**: Used as the primary color for structural elements like the main header navigation block.
*   **Sandy Brown (`#F4A261`)**: Applied as the bright highlight accent color for hover items and structural borders.
*   **Bright Snow (`#F8F9FA`)**: The core universal background color for standard views.
*   **Carbon Black (`#212529`)**: The high-contrast text color profile.
*   **Dark Spruce (`#2D4A22`)**: The accent color reserved for specific interactive application headings and booked reservation states.

![](docs/screenshots/color_pallet.png)

## Data Model

### Database Architecture

``` mermaid
erDiagram
    User ||--o{ Reservation : booked
    User {
        int user_id PK
        string name
        string email
        string first_name
        string last_name
        string phone_number
    }
    Reservation {
        int reservation_id PK
        string svc_date
        string res_date
        string time
        int duration "minutes"
        int guest_count
        int status
        int user_id FK
    }
    Table {
        int table_id PK
        int table_number UK
        int seat_count
    }
    ServiceTime {
        int hours_id PK
        int day_of_week "0-mon to 6-sun"
        string start_time "24-hour clock"
        string end_time "24-hour clock"
    }
    ServiceException {
        int exception_id PK
        string date
        string start_time "24-hour clock"
        string end_time "24-hour clock"
    }
```

## User Roles and Stories

### Target User Roles
*   **Recipe Author**: A coder looking to submit, maintain, and showcase technical culinary scripts.
*   **Site Visitor**: A user searching the application database for structural meal preparation guides.

### In-Progress User Stories
*   **Recipe Management Authorization (Must-Have)**: As a recipe author I can edit or delete my own recipes so that I can fix mistakes or remove them.
    *   *Acceptance Criteria*:
        *   Edit/Delete control actions appear exclusively on documents owned by the logged-in author.
        *   Destructive actions (Delete) trigger an explicit front-end confirmation prompt before completion.
        *   Unauthorized modification attempts via direct URL manipulation drop execution and return a secure **403 Forbidden** server page response.

## Features & Implementation Progress

*   **Unified Application Theme**: Upgraded standard Bootstrap specificity paths to cleanly execute custom palette variables without relying on performance-degrading `!important` tags.
*   **Asset Pipeline Integration**: Stabilized the layout render loops for core vector properties:
    *   `static/images/reci_py_logo.png` inside the brand navbar element.
    *   `static/favicon/favicon.ico` running via explicit cache-busted header tags (`?v=2`).

    ![](docs/screenshots/site_logo.png)

## Technology Stack

*   **Core Framework**: Django 6.1.1 (Python-based dynamic templating architecture).
*   **Frontend UI Utilities**: Bootstrap 5 + Font Awesome Brand Icon Assets.
*   **Styles**: Standard Scoped Custom CSS.
*   **Static Asset Management**: WhiteNoise Pipeline Utility + Heroku Direct Engine Compilation.
