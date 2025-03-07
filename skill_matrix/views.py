# # yourproject/views.py
# # from djangosaml2.views import login, logout
# from django.contrib.auth import login
# # from djangosaml2.utils import get_saml_attribute
# from django.shortcuts import redirect
# from django.contrib.auth.models import User


# # # Optional custom login view if needed
# # def custom_login(request):
# #     return login(request)

# # # Optional custom logout view if needed
# # def custom_logout(request):
# #     return logout(request)


# from django.contrib.auth import login

# from djangosaml2.views import AssertionConsumerServiceView


# def saml_authenticated_view(request):
#     user_email = get_saml_attribute(request, 'email')
#     user, created = User.objects.get_or_create(email=user_email)

#     if created:
#         # Optionally set other attributes, e.g., first name, etc.
#         user.first_name = get_saml_attribute(request, 'first_name')
#         user.last_name = get_saml_attribute(request, 'last_name')
#         user.save()

#     # Authenticate and log in the user
#     login(request, user)
#     return redirect('home')  # Redirect to a protected view


# class CustomACSView(AssertionConsumerServiceView):
#     def post(self, request, *args, **kwargs):
#         # Custom handling of the SAML response
#         user_email = get_saml_attribute(request, 'email')
#         user, created = User.objects.get_or_create(email=user_email)

#         # Optionally, map more attributes here
#         if created:
#             user.first_name = get_saml_attribute(request, 'first_name')
#             user.save()

#         # Log in the user
#         login(request, user)
#         return redirect('home')  # Redirect to a secure page


# def get_saml_attribute(request, attribute_name):
#     """Extract a SAML attribute from the request."""
#     saml_attributes = request.session.get('samlUserdata', {})
# return saml_attributes.get(attribute_name, [None])[0]  # Return the
# first value if available


# from django.contrib.auth import login
# from django.http import HttpResponseRedirect
# from django.contrib.auth.models import User
# from djangosaml2.utils import get_saml_attribute
# from djangosaml2.views import AssertionConsumerServiceView


# from django.contrib.auth import login
# from django.http import HttpResponseRedirect, HttpResponse
# from django.contrib.auth.models import User
# from djangosaml2.views import AssertionConsumerServiceView


# # Your custom view for handling SAML authentication
# def saml_authenticated_view(request):
#     user_email = get_saml_attribute(request, 'email')
#     user, created = User.objects.get_or_create(email=user_email)

#     if created:
#         # Optionally set other attributes, e.g., first name, etc.
#         user.first_name = get_saml_attribute(request, 'first_name')
#         user.last_name = get_saml_attribute(request, 'last_name')
#         user.save()

#     # Authenticate and log in the user using Django's default login function
#     login(request, user)
#     return HttpResponseRedirect('/home/')  # Redirect to a protected page


# class CustomACSView(AssertionConsumerServiceView):
#     def post(self, request, *args, **kwargs):
#         # Extract SAML attributes from the request after successful authentication
#         saml_response = request.POST.get("SAMLResponse")
#         if saml_response:
#             # Assuming the response is parsed and contains user attributes
#             # Example: You can use `request.user` if `SAMLResponse` is valid
#             user_email = request.user.email  # The email should be available here after successful SSO
#             user_first_name = request.user.first_name  # Assuming these attributes exist
# user_last_name = request.user.last_name  # Assuming these attributes
# exist

#             # Get or create the user in the database
#             user, created = User.objects.get_or_create(email=user_email)

#             if created:
#                 # Optionally, set more attributes, e.g., first name, last name
#                 user.first_name = user_first_name
#                 user.last_name = user_last_name
#                 user.save()

#             # Log in the user
#             login(request, user)
# return HttpResponseRedirect('/home/')  # Redirect to the homepage after
# successful login

#         # If no SAML response is found, return an error
#         return HttpResponse("SAML Response not found.", status=400)


# from django.contrib.auth import login
# from django.contrib.auth.models import User
# from django.shortcuts import redirect
# from django.http import HttpResponse

# def saml_authenticated_view(request):
#     # Ensure the session contains the correct SAML attributes
#     user_email = request.session.get('saml2_email')  # Check if email is in the session
#     first_name = request.session.get('saml2_first_name')  # Check if first name is in the session
# last_name = request.session.get('saml2_last_name')  # Check if last name
# is in the session

#     if not user_email:
# return HttpResponse("SAML authentication failed. Missing email
# attribute.", status=400)

#     # Create or get the user from the database based on the email
#     user, created = User.objects.get_or_create(email=user_email)

#     if created:
#         # Set additional attributes if the user is newly created
#         user.first_name = first_name
#         user.last_name = last_name
#         user.save()

#     # Log the user in
#     login(request, user)

#     # Redirect to home or any protected page
#     return redirect('home')


# from django.shortcuts import render
# from djangosaml2.views import LoginView as BaseLoginView
# from django.http import HttpResponse
# from django.urls import reverse

# class CustomLoginView(BaseLoginView):
#     """
#     Custom view to display a login page and allow the user to trigger SAML authentication manually.
#     """
#     def get(self, request, *args, **kwargs):
#         """
#         Custom GET method for rendering a custom login page.
#         This step does not automatically trigger the redirect to the IdP.
#         """
#         # Render your custom login page here
#         return render(request, "account/custom_login_page.html")

#     def post(self, request, *args, **kwargs):
#         """
#         Custom POST method to initiate the SAML login process on form submission.
#         This triggers the redirect to the IdP for authentication.
#         """
#         # Redirect to the default SAML login view that triggers the IdP redirect
#         return super().get(request, *args, **kwargs)
from django.shortcuts import render


def custom_logout_view(request):
    request.session.flush()
    return render(request, 'account/logout_temp.html')
