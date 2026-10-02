# reci.py - Recipe Website for Coders

[Live website](https://reci-py-93c536d719a2.herokuapp.com/)

reci.py is a Django recipe website where visitors can discover public recipes and registered users can submit recipes, comment, and receive updates about the review process.

![Screenshot Responsive Testing](docs/screenshots/responsive.png)

## Design & Planning

### User Stories

The user stories below are taken from the project board and grouped by user persona. The MoSCoW priority identifies whether each story was a must-have, should-have, could-have, or won't-have requirement for this release.

| US No. | User Story | User | MoSCoW |
| --- | --- | --- | --- |
| US 3 | As a developer I can work from a shared, deployed Django project so that the team can build features in parallel from day one. | Developer | Must have |
| US 7 | As a developer I can follow agreed wireframes, an ERD, and a colour/font scheme so that the build is consistent and the UX process is documented. | Developer | Must have |
| US 14 | As a developer I can run automated tests for models, forms, views, and permissions so that we know the app works and can evidence it for assessment. | Developer | Must have |
| US 4 | As a visitor I can create an account and log in so that I can post recipes and join in. | Visitor | Must have |
| US 5 | As a visitor I can see a list of published recipes so that I can find something to cook. | Visitor | Must have |
| US 6 | As a visitor I can open a recipe to see its ingredients and method so that I can follow it. | Visitor | Must have |
| US 16 | As a visitor I can search by title or ingredient and filter by difficulty or time so that I find a suitable recipe faster. | Visitor | Could have |
| US 18 | As a visitor on a budget I can see the cost per portion of each recipe so that I can cook affordably. | Visitor on a budget | Could have |
| US 20 | As a visitor I can scale a recipe from 2 to 6 servings so that quantities fit the number of people I am cooking for. | Visitor | Won't have |
| US 8 | As a logged-in user I can submit my own recipe through a form so that I can share it with others. | Logged-in user | Must have |
| US 10 | As a logged-in user I can leave, edit, and delete my own comments so that I can share tips and feedback. | Logged-in user | Should have |
| US 13 | As a logged-in user I can view and update my profile so that other users know who shared a recipe. | Logged-in user | Should have |
| US 17 | As a logged-in user I can like recipes and see them in a My Liked Recipes list on my profile so that I can find my favourites again quickly. | Logged-in user | Could have |
| US 54 | As a logged-in user I can like a recipe and receive a confirmation notification so that I know it was saved to my profile. | Logged-in user | Could have |
| US 9 | As a recipe author I can edit or delete my own recipes so that I can fix mistakes or remove them. | Recipe author | Must have |
| US 11 | As a recipe author I can receive a notification when my recipe is approved or rejected, or someone comments on it, so that I know what is happening with my content. | Recipe author | Must have |
| US 19 | As a recipe author I can get an email when my recipe is approved so that I do not have to log in to check. | Recipe author | Won't have |
| US 12 | As an admin I can approve, reject, or remove any recipe or comment so that the blog stays accurate and appropriate. | Admin | Must have |
| US 15 | As an assessor I can read a complete README with testing and deployment evidence so that I can see how the project was planned, built, tested, and deployed. | Assessor | Must have |
| US 55 | As a visitor I can share a recipe I want on social media so that I can show the joy I just viewed as a fellow coder. | Visitor | Could have |

### Wireframes

![Wire-Frames](docs/wireframes.png)

### Agile Methodology

Development was organised around small user stories and acceptance criteria. Features were tested as they were implemented, with priority given to recipe discovery, authenticated submission, moderation, comments, and notifications.

> ![Project Board](docs/project_board.png)

### Typography

* **DM Sans** is used for interface text.
* **Fraunces** is used for headings.
* **JetBrains Mono** is available for code-style details.

>![Fonts used](docs/fonts_used.png)

### Colour Scheme

* **Warm Cream (`#FFF8F0`)**: Page background and light surfaces.
* **Ink (`#2B2118`)**: Main text, headings, and footer content.
* **Tomato (`#B54128`)**: Buttons, links, and interactive accents.
* **Butter (`#F2C14E`)**: Highlights and visual emphasis.
* **Basil (`#3A7022`)**: Tags and positive recipe states.
* **Crust (`#F3EED0`)**: Soft panels, borders, and secondary surfaces.
* **Muted (`#6B5B4E`)**: Secondary text.

> ![Colour pallet](docs/recipe-colour-pallet.png)

### Branding

**Logo**

<p align="center">
    <img src="docs/screenshots/site_logo.png" alt="Reci.py Logo" width="33%">
</p>

**Tagline**  
*Simple Recipes • Healthy Meals • For Coders*

Reci.py is a recipe-sharing platform built specifically for developers and coders. It combines clean, simple recipes with healthy meal ideas in an interface that feels right at home for the tech community.

### Database Diagram

```mermaid
erDiagram
    User ||--o{ Recipe : authors
    User ||--o{ Comment : writes
    Recipe ||--o{ Comment : receives
    User {
        int user_id PK
        string username
        string email
    }
    Recipe {
        int recipe_id PK
        string title UK
        string description
        string ingredients
        string method
        string image_url
        int servings
        int prep_time
        int cook_time
        string difficulty
        string status
        datetime created_at
        int author_id FK
    }
    Comment {
        int comment_id PK
        string body
        datetime created_at
        datetime updated_at
        int recipe_id FK
        int author_id FK
    }
```

Recipe statuses are `pending`, `approved`, `published`, and `rejected`. New submissions begin as `pending` and are reviewed by staff.

> **Screenshot placeholder:** Add a database diagram screenshot if a visual diagram is preferred.

## Features

### Navigation

The responsive navigation provides links to Home, Register, Login, Profile, Submit recipe, Notifications, and the staff Admin area when appropriate. The mobile menu collapses using Bootstrap.

> **Screenshot:** ![Navigation](docs/features/feat_nav.png)

### Footer

The footer contains the team attribution and social media links, including the project GitHub repository.

> **Screenshot:** ![Footer](docs/features/feat_footer.png)

### Home Page

The homepage displays approved and published recipes in responsive cards. Visitors can search by title or description, filter by difficulty, sort by date, title, or preparation time, and use pagination.

> **Screenshot:** ![Home](docs/features/feat_home.png)

### Recipe Detail Page

Each public recipe shows its image, description, servings, preparation and cooking times, ingredients, numbered method, author, date, and approved comments.

> **Screenshot:** ![Recipe detail](docs/features/feat_recipe_deets.png)

### Submit Recipe

Authenticated users can submit recipe details, an optional uploaded image, or an image URL. Required fields, positive numeric values, and unique recipe titles are validated. New recipes are stored as `pending`.

> **Screenshot:** ![Submit recipe](docs/features/feat_recipe_sub.png)

### Profile

Authenticated users can view their profile and update their email address.

> **Screenshot:** ![Profile](docs/features/feat_profile.png)

### Notifications

Authenticated users receive notifications for recipe submission, approval, rejection, and comments. The navigation displays an unread badge, and notifications can be marked as read from the inbox.

> **Screenshot:** ![Notification](docs/features/feat_notify.png)

### Comments

Authenticated users can comment on public recipes. Comment authors can edit or delete their own comments, and ownership checks protect these actions.

> **Screenshot:** ![Comments](docs/features/feat_comments.png)

### CRUD

* **Create**: Registered users create recipes and comments.
![Create](docs/crud/crud_create.png)
* **Read**: Visitors read public recipes and approved comments.
![alt text](docs/crud/crud_read.png)
* **Update**: Users update their profile email and their own recipe's.
* **Delete**: Users delete their own comments.

![alt text](docs/crud/crud_update_delete.png)


* **Moderate**: Staff approve or reject pending recipes and comments.
![alt text](docs/crud/crud_mod.png)


### Authentication & Authorisation

Django Allauth provides registration and login. Login protection is applied to user-only pages, staff-only review pages require staff status, and comment edit/delete actions require ownership.



## Technologies Used

* Python
* Django 6.1.1
* HTML5, CSS3, and JavaScript
* PostgreSQL in deployment
* Heroku
* Git and GitHub

## Libraries Used

* Django Allauth for authentication.
* Bootstrap 5 for responsive layout, cards, forms, navigation, and pagination.
* Font Awesome for interface icons.
* Django Crispy Forms and Crispy Bootstrap 5 for form rendering.
* django-notifications-community for the notification inbox and unread badge.
* WhiteNoise and Django staticfiles for static asset handling.

## Testing

### Manual Testing

The following tables are ready for a screenshot to be added to each test case. Replace each placeholder with the relevant image link when testing is complete.

#### User Stories

| User story | Test steps | Expected result | Screenshot |
| --- | --- | --- | --- |
| Browse public recipes | Open the homepage as a visitor. | Approved and published recipes appear; pending and rejected recipes remain hidden. | `[Screenshot placeholder: user story 1]` |
| Find a suitable recipe | Search, filter by difficulty, sort, and change page. | Results and ordering update while the selected controls remain usable. | `[Screenshot placeholder: user story 2]` |
| View recipe information | Open a recipe card. | The detail page shows the recipe image, ingredients, method, timings, author, and date. | `[Screenshot placeholder: user story 3]` |
| Submit a recipe | Log in, complete the form, and submit it. | The recipe is saved as `pending` and a confirmation message is shown. | `[Screenshot placeholder: user story 4]` |
| Receive recipe notifications | Submit, approve, or reject a recipe. | The relevant author receives an unread notification in the inbox. | `[Screenshot placeholder: user story 5]` |
| Comment on a recipe | Log in and submit a valid comment. | The comment appears and the recipe author is notified when applicable. | `[Screenshot placeholder: user story 6]` |
| Manage own comments | Edit and delete a comment created by the logged-in user. | The comment is updated or removed; another user's comment cannot be managed. | `[Screenshot placeholder: user story 7]` |
| Review submissions | Sign in as staff and approve or reject a pending recipe. | The recipe status changes and public visibility follows the decision. | `[Screenshot placeholder: user story 8]` |

#### Features

| Feature | Test steps | Expected result | Screenshot |
| --- | --- | --- | --- |
| Navigation | Use the desktop navigation and open the mobile menu. | Correct links are shown for the user's role and the menu works on small screens. | `[Screenshot placeholder: feature 1]` |
| Footer | Scroll to the bottom of a page and select a social link. | Footer content is visible and links open correctly. | `[Screenshot placeholder: feature 2]` |
| Homepage cards | Load the homepage with public recipes available. | Recipe cards display consistently with working detail links. | `[Screenshot placeholder: feature 3]` |
| Search and filtering | Search by title/description and select each difficulty. | Matching recipes remain and unrelated recipes are removed. | `[Screenshot placeholder: feature 4]` |
| Sorting and pagination | Select each sort option and move between pages. | Card order changes and pagination works without losing the current query. | `[Screenshot placeholder: feature 5]` |
| Recipe detail | Open an approved recipe. | All recipe details and approved comments are readable. | `[Screenshot placeholder: feature 6]` |
| Form validation | Submit empty fields, duplicate titles, and non-positive numbers. | Clear field-level validation messages prevent invalid submission. | `[Screenshot placeholder: feature 7]` |
| Profile and notifications | Update an email address and mark a notification as read. | The profile saves and the notification is removed from the unread list. | `[Screenshot placeholder: feature 8]` |
| Responsive layout | Test the homepage, forms, detail page, and inbox at desktop, tablet, and mobile widths. | Content stacks correctly without horizontal scrolling or distorted images. | `[Screenshot placeholder: feature 9]` |


### Performance and Responsiveness

| Feature                  | Test steps                                                                 | Expected result                                      | Screenshot                  |
|--------------------------|----------------------------------------------------------------------------|------------------------------------------------------|-----------------------------|
| Am I responsive          | Resize the browser window or use device emulation to test multiple breakpoints. | Layout adapts correctly on desktop, tablet, and mobile. | ![](docs/screenshots/responsive.png)             |
| Home page                | Load the homepage on different screen sizes.                               | All content is visible and properly aligned.         | ![](docs/screenshots/home_page.png)              |
| Recipe page              | Open a recipe detail page on various screen widths.                        | Recipe content, images, and comments display correctly. | ![](docs/screenshots/recipe_page.png)            |
| Sign up page             | View the sign-up form on desktop, tablet, and mobile.                      | Form fields and buttons are responsive and usable.   | ![](docs/screenshots/sign_up_page.png)           |
| Sign in page             | View the sign-in form on multiple devices.                                 | Form layout and validation work correctly.           | ![](docs/screenshots/sign_in_page.png)           |
| Profile page             | Open the user profile on different screen sizes.                           | Profile information and actions are accessible.      | ![](docs/screenshots/profile_page.png)           |
| My recipe page           | View the “My Recipes” page on desktop and mobile.                          | Recipe list and management buttons respond well.     | ![](docs/screenshots/my_recipe_page.png)         |
| Notification page        | Open the notifications page on various devices.                            | Notifications list displays cleanly on all screens.  | ![](docs/screenshots/notification_page.png)      |


### Accessibility

Accessibility was tested using Lighthouse and the [WAVE accessibility extension](https://wave.webaim.org/extension/).

All pages have a warning about redundant links because the logo and site name both link to the home page.  This is what users expect.

|Page|WAVE Screenshot|
|-|-|
|Home|![](docs/wave/home.png)|
|Register|![](docs/wave/register.png)|
|Login|![](docs/wave/login.png)|
|Recipe Detail|![](docs/wave/recipe.png)|
|Submit a Recipe|![](docs/wave/submit.png)|
|Notifications|![](docs/wave/notifications.png)|
|Edit Recipe|![](docs/wave/edit-recipe.png)|
|Edit Comment|![](docs/wave/edit-comment.png)|
|My Recipes|![](docs/wave/my-recipes.png)|
|Profile|![](docs/wave/profile.png)|
|Admin|![](docs/wave/admin.png)|
|Review|![](docs/wave/review.png)|

### Automated Tests

Install dependencies before running Django commands:

```powershell
python -m pip install -r requirements.txt
```

Run the focused recipe tests:

```powershell
.\.venv\Scripts\python.exe manage.py test core.test_recipe_submission
```

Run the full test suite:

```powershell
.\.venv\Scripts\python.exe manage.py test
```

Run Django system checks:

```powershell
.\.venv\Scripts\python.exe manage.py check
```

#### What the Automated Tests Cover

The automated tests use Django's `TestCase` framework. Each test creates an isolated temporary test database, creates the users and recipes needed for the scenario, sends requests through Django's test client, and checks the response, database state, redirects, messages, permissions, and notifications. The temporary database is removed when the test run finishes, so test data does not affect development or production data.

The main test modules cover the following areas:

* **`core.test_recipe_submission`** checks that recipe submission requires authentication, validates required fields and positive numeric values, prevents duplicate titles, saves a valid submission as `pending`, and displays the expected confirmation message. It also checks public recipe detail pages, hidden pending or rejected recipes, and links from the homepage.
* **`core.test_recipe_list`** checks that only approved and published recipes appear publicly, pagination returns six cards per page, category and difficulty filters work, name and most-liked sorting work, and the `My liked` filter is limited to logged-in users. It also checks that users can like and unlike recipes and that unsafe redirect URLs are rejected.
* **`core.test_profile`** checks the username heading, newest-first authored recipes, pending submissions, owner-only edit and delete links, liked public recipes, empty-profile behaviour, password-reset access, and valid or invalid email updates.
* **`core.test_edit_delete_recipe`** checks that users can manage their own recipes, edits return recipes to the review queue, invalid edits do not save, delete actions require confirmation, and other users receive `403 Forbidden` responses when attempting to manage someone else's recipe.
* **`core.test_comments`** checks anonymous access restrictions, valid and empty comment submissions, comment approval visibility, comment ownership, editing, deletion, and notification of the recipe author.
* **`core.test_notifications`** checks login protection for the inbox, that users see only their own unread notifications, that notifications can be marked as read, and that another user's notification cannot be changed.
* **`core.test_moderation`** checks staff-only access to moderation pages, recipe approval and rejection, comment approval and rejection, status changes, and notifications sent to authors.

The focused application test command below runs these behaviour tests without the external W3C validator suite:

```powershell
.\.venv\Scripts\python.exe manage.py test core.test_comments core.test_notifications core.test_moderation core.test_profile core.test_edit_delete_recipe core.test_recipe_list core.test_recipe_submission
```

The full `manage.py test` command also includes the validation tests. `manage.py check` verifies Django configuration, installed applications, URL configuration, and model setup. `manage.py makemigrations --check --dry-run` confirms that model changes have corresponding committed migrations and that no migration file is missing.

The project also includes HTML and CSS validation tests in `core/test_valid.py`. These tests use the W3C validator supplied in the `fixtures` directory and require Java. Accessibility checks include image alternative text, labelled form fields, keyboard navigation, logical headings, colour contrast, and assistive-technology state for recipe detail controls.

## Bugs

No known bugs are outstanding at the time of writing. Any newly discovered issue should be recorded with reproduction steps, expected behaviour, actual behaviour, and its resolution.

> **Screenshot placeholder:** Add evidence of the final bug-testing pass if required.

## Deployment

The deployed application is hosted on Heroku:

[https://reci-py-93c536d719a2.herokuapp.com/](https://reci-py-93c536d719a2.herokuapp.com/)

The deployment uses PostgreSQL, environment-based configuration, WhiteNoise for collected static files, and a `Procfile` to start the Django application. Before deployment, install requirements, configure environment variables, run migrations, collect static files, and create a staff user for the review workflow.

## AI

AI tools were used as development support for brainstorming, documentation structure, debugging guidance, and reviewing implementation details. All generated suggestions were checked against the project code, tests, and final application behaviour.

## Credits

* Bootstrap documentation and components: [getbootstrap.com](https://getbootstrap.com/)
* Font Awesome icons: [fontawesome.com](https://fontawesome.com/)
* Django documentation: [docs.djangoproject.com](https://docs.djangoproject.com/)
* Django Allauth documentation: [docs.allauth.org](https://docs.allauth.org/)
* Project repository: [github.com/lion695/reci.py](https://github.com/lion695/reci.py)
