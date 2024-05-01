# CUHK Class Schedule to Google Calendar

A python script that uses the CUHK ClassTT app's endpoints to retrieve the class schedule and add it to Google Calendar.

## Usage

1. Clone the repository

2. Install the required packages

    ```bash
    pip install -r requirements.txt
    ```

3. Run the script

    ```bash
    python main.py
    ```

4. Fill out the generated `config.ini`. You do not need to add `""` to the values.

5. Follow the quickstart guide for Google Calendar API to get the `credentials.json` file and place it in the root directory of the project.
    1. [Enable the API](https://developers.google.com/calendar/api/quickstart/python#enable_the_api)
    2. [Configure the OAuth consent screen](https://developers.google.com/calendar/api/quickstart/python#configure_the_oauth_consent_screen)
        - I had to select `External` as it was the only option that was clickable
        - On the scope section, add the following, `auth/calendar.app.created`
        - Remember to add yourself as a test user
    3. [Authorize credentials for a desktop application](https://developers.google.com/calendar/api/quickstart/python#configure_the_oauth_consent_screen)

6. Run the script again

    ```bash
    python main.py
    ```

7. Follow the steps to authenticate with Google. A new file will be created after authentication, `token.json`. This file will be used to authenticate with Google in the future and will not require you to authenticate again.

8. Follow the prompts. All of them have default values so you can press enter to skip.
