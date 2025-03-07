import os
import django

from dotenv import load_dotenv
load_dotenv()
# Set the Django settings module environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skill_matrix.settings')

# Set up Django
django.setup()


from msal import ConfidentialClientApplication
import msal


client_id = str(os.getenv('CLIENTID'))
client_secret= str(os.getenv('CLIENTSECRET'))
tenent_id = str(os.getenv('TENENTID'))

print(f"Client ID: {client_id}")
print(f"Client Secret: {client_secret}")
print(f"Tenant ID: {tenent_id}")


msal_url = f'https://login.microsoftonline.com/{tenent_id}'
msal_scope = ['https://graph.microsoft.com/.default']

msal_app = msal.ConfidentialClientApplication(
    client_id=client_id,
    client_credential=client_secret,
    authority=msal_url,
)

result = msal_app.acquire_token_silent(scopes=msal_scope, account=None)

if not result:
    result = msal_app.acquire_token_for_client(scopes=msal_scope)

# Check if we have an access token
if "access_token" in result:
    access_token = result["access_token"]
    # print(f"Access Token: {access_token}")
else:
    print("Error: Unable to acquire access token.")




import requests


def get_manager(upn, access_token):
    url = f"https://graph.microsoft.com/v1.0/users/{upn}/manager"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()  
    else:
        return {"error": response.json()}



def get_all_users_with_pagination(access_token):
    """Fetch all users from Microsoft Graph API with pagination."""
    url = "https://graph.microsoft.com/v1.0/users"
    all_users = []  # List to store all users

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    while url:  # Loop until there are no more pages
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            all_users.extend(data['value'])  # Add users from the current page
            
            # Get the next page link
            url = data.get('@odata.nextLink')
        else:
            print(f"Error: {response.status_code}, {response.text}")
            break  # Exit loop on error

    return all_users


user_list = {}
users = get_all_users_with_pagination(access_token)
# print(users)
for user in users:
    upn = str(user['userPrincipalName'])
    manager = get_manager(upn, access_token)
    if 'userPrincipalName' in manager.keys():
        # print( f'{user['userPrincipalName']} -{manager['userPrincipalName']}')
        user_list[user['userPrincipalName']] = manager['userPrincipalName']



from user_skills.models import Organization_tree

def initail_data_load(user_list):
    emp_objects = {}

    for emp_email in user_list.keys():
        # Create employee record
        try:
            emp_object = Organization_tree.objects.create(empname=emp_email)
            emp_objects[emp_email] = emp_object
        except django.db.utils.IntegrityError:
            pass
    for emp_email, manager_email in user_list.items():
        try:
            emp_object = emp_objects.get(emp_email)
            
            try:
                manager_object = Organization_tree.objects.get(empname=manager_email)
                emp_object.mgrid = manager_object
                emp_object.save() 

            except Organization_tree.DoesNotExist:
                print(f"Manager not found for {emp_email}: {manager_email}")
        
        except KeyError:
            print(f"Employee not found in emp_objects: {emp_email}")

    print("Initial data load complete!")


initail_data_load(user_list)

# from django.shortcuts import get_object_or_404
# from user_skills.models import SkillRating, CategorySubcategoryNewSkill, CategorySubcategory, Category, Subcategory, NewSkill
# from django.contrib.auth.models import User 
# import pandas as pd

# # Read the CSV file into a DataFrame
# df = pd.read_csv('/Users/aswaththaman_athimurugan/Downloads/filtered_users.csv')


# for index, row in df.iterrows():
#     uname = row['Username']
#     sname = row['Skill name']
#     scat = row['Skill category']
#     cat = row['Skill subcategory']
#     rating = row['User ratings']
#     # try:
#     u_obj= User.objects.get(username = uname)

#     category, c = Category.objects.get_or_create(name=cat)
#     subcategory, s = Subcategory.objects.get_or_create(name=scat)
#     category_subcategory, cs = CategorySubcategory.objects.get_or_create(
#         category=category, subcategory=subcategory
#     )
#     new_skill, ns = NewSkill.objects.get_or_create(name=sname)

#     category_subcategory_new_skill, csns = CategorySubcategoryNewSkill.objects.get_or_create(
#         categorysubcategory=category_subcategory,
#         new_skill=new_skill
#     )

#     SkillRating.objects.create(user = u_obj, skill =category_subcategory_new_skill, rating= rating, mgrreview = None )
    
    



