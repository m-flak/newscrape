# newscrape
Fetch and save news articles with multi-user support. A Flask web app.

__Features:__
* Multi-User Login
* Administration for managing registered users
* Customizable keywords for news results from search engines *(Currently: Google & Bing)*
* Saving of stories so you can read them later

### Before using:
1. Ensure that the MySQL server has the database, tables, and etc required. A SQL script is in __*/sql*__.
2. __*(Optional)*__ Execute the required SQL commands to create an initial admin account. Refer to the SQL script.
2. Run ```make``` to generate the secret key file to be used by Flask.

That's all for now.
