# Example script used to programmatically add users to a build group

**Note - This is a proof of concept script; validate the scripts functionality before using it.** 

### Python version: 3.9

## Description of functionality
1. This script gets current group members with a given roleId
2. The script reads csv data (see sample_data.csv
    * As the CSV is being read, a check is done to see if "added_to_group" is True. If that column is set to True, the row is not returned
3. The function go_through_data then executes if there are additional entries in the csv
    1. For each entry in the csv data an attempt is made to find a single user where the CHECK_VAL (see .env.sample) in the csv matches the data returned from the API
    2. If a user is found, the user's build id is appended to the list of current group members. This user is also added to a list that will be updated later.
    4. The group's roles attribute is updated with the new list of members. If the group is successfully updated, a "success" is returned
5. For users that were added to the group, the csv file's "added_to_group" attribute is updated to "True"


## Setup
1. Preferably, use a virtual environment (activate that in directory where code is)
2. pip install -r requirements.txt
3. Create and edit .env (see sample)
    * TOKEN - The api token from Build instance (admin token)
    * DOMAIN - The domain (excluding '/' at the end of domain)
    * GROUP_ID - The unique id for the group (can be found in the URL when viewing the group)
    * ROLE_ID - The unique id associated with the role (if members is the assigned role, it will be "member"). This can be set by admins when creating the group
    * CHECK_VAL - Is likely email or username. This should be a unique value that can be used to query for the user
4. Create csv (see sample_data.csv)
5. Edit FILE_NAME in main.py
6. Run script - "python3 main.py"

## Things to consider adding
* Functionality to remove a user if condition is met
    * a CSV header could be added - maybe "delete" that could be set to True. This could be used somwhere in the script to remove the values that are to be deleted
* Functionality to remove a csv row if a delete functionality is added.