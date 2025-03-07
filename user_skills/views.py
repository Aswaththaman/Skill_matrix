# from .views import IsAdminView  # Import the IsAdminView class
from .serializers import GroupedRatedSkillsSerializer, GroupedUnratedSkillsSerializer
from .models import SkillRating
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import NewSkill, SkillRating, UserRole, Role, Category, Subcategory, CategorySubcategoryNewSkill, CategorySubcategory, CertificateUserMap, Certificate, Organization_tree
from .forms import Add_New_Data, ReportIssueForm
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
import pandas as pd
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic import RedirectView
from django.utils.decorators import method_decorator
# from rest_framework.response import Response
from .serializers import SearchUnratedSkiillSerializer
# from datetime import datetime
# from django.db import IntegrityError
from django.db.models import Q
from django.core.mail import send_mail


class IsAdminView(View):
    def get(self, request, *args, **kwargs):
        # Simply return True or False based on the is_admin method
        is_admin = self.is_admin(request.user)

    def is_admin(self, user):
        try:
            # Check if the user has a 'admin' role in the UserRole model
            # Get the Role object for 'Admin'
            admin_role = Role.objects.get(name='admin')
            user_role = UserRole.objects.get(
                user=user, role=admin_role)  # Check if the user has this role
            return True
        except (Role.DoesNotExist, UserRole.DoesNotExist):
            return False

    def is_manager(self, user):
        try:
            mgr_role = Role.objects.get(name='manager')
            user_role = UserRole.objects.get(
                    user=user, role=mgr_role)
            return True
        except:
            return False
        

class HomeViewRedirect(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        user_id = self.request.user.id  # Access the user ID from the request
        # This is equivalent to redirecting to the skill_dashboard view
        return reverse('skill_dashboard')

class RedirectAnonymous(View):
    """
    A base class that checks if the user is authenticated.
    If not, it redirects to a specified URL (e.g., login page).
    """
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        # If user is authenticated, you can add more logic here if needed.
        return super().get(request, *args, **kwargs)

    
class ExportCsvRatingsDataView(View):
    def get(self, request, *args, **kwargs):
        # Fetch data for users, skill ratings, skills, categories, and
        # subcategories
        users = User.objects.all().values()
        user_df = pd.DataFrame(list(users))

        
        admin_view = IsAdminView()
        is_admin_user = admin_view.is_admin(request.user)
        if not is_admin_user:
            return HttpResponse("Unauthorized kindly login as a admin user to use more features", status=401)
        
        
        skill_ratings = SkillRating.objects.all().select_related(
            'user',
            'skill').values(
            'user__username',
            'rating',
            'skill__new_skill__name',
            'skill__categorysubcategory__category__name',
            'skill__categorysubcategory__subcategory__name')
        review_df = pd.DataFrame(list(skill_ratings))

        # Merge the data frames (if necessary, based on the data structure)
        # Data already includes the necessary user, skill, category,
        # subcategory info
        result_df = review_df

        # Select relevant columns for export
        selected_cols = [
            'user__username',
            'skill__new_skill__name',
            'skill__categorysubcategory__category__name',
            'skill__categorysubcategory__subcategory__name',
            'rating']
        download_df = result_df[selected_cols]
        download_df.rename(
            columns={
                'user__username': 'Username',
                'skill__new_skill__name': 'Skill name',
                'skill__categorysubcategory__category__name': 'Skill category',
                'skill__categorysubcategory__subcategory__name': 'Skill subcategory',
                'rating': 'User ratings'},
            inplace=True)

        # Prepare the CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="skill_matrix_data.csv"'
        download_df.to_csv(response, index=False)

        return response


class UpdateRatingView(View):
    def post(self, request, *args, **kwargs):
        # Get data from POST request
        skill_id = request.POST.get('skill_id')
        rating = int(request.POST.get('rating'))
        user_id = request.POST.get('user_id')
        skill_name = request.POST.get('skillName').lower()
        skill_cat = request.POST.get('skill_cat').lower()
        skill_subcat = request.POST.get('skill_subcat').lower()

        skill_cat = skill_cat.replace('-', ' ')
        skill_subcat = skill_subcat.replace('-', ' ')

        # print(f"Skill name: {skill_name}, skill id: {skill_id}, skill ratings {rating}, user id {user_id}, cat - {skill_cat}, subcat- {skill_subcat}")

        if rating < 1 or rating > 5:
            return JsonResponse(
                {'success': False, 'message': 'Invalid rating value.'})

        try:
            skill_rating = SkillRating.objects.get(
                user_id=user_id, skill_id=skill_id)
            skill_rating.rating = rating  # Update the rating
            skill_rating.save()
            message = 'Rating updated successfully!'

            return JsonResponse({'success': True, 'message': message})

        except SkillRating.DoesNotExist:
            # If no rating exists, create a new one
            try:
                category = get_object_or_404(Category, name=skill_cat)
                subcategory = get_object_or_404(Subcategory, name=skill_subcat)
                category_subcategory = get_object_or_404(
                    CategorySubcategory, category=category, subcategory=subcategory)
                new_skill = get_object_or_404(NewSkill, name=skill_name)
                category_subcategory_new_skill = get_object_or_404(
                    CategorySubcategoryNewSkill,
                    categorysubcategory=category_subcategory,
                    new_skill=new_skill
                )
                user_ins = User.objects.get(id=user_id)
                skill_rating = SkillRating.objects.create(
                    user=user_ins, skill=category_subcategory_new_skill, rating=rating)
                message = 'Rating created and saved successfully!'

            except NewSkill.DoesNotExist:
                return JsonResponse(
                    {'success': False, 'message': 'Skill not found.'}, status=400)

            created_skill = CategorySubcategoryNewSkill.objects.get(
                id=skill_id)
            category = created_skill.categorysubcategory.category.name
            subcategory = created_skill.categorysubcategory.subcategory.name

            skill_cat = skill_cat.replace(' ', '-')
            skill_subcat = skill_subcat.replace(' ', '-')
            # Render the new rated skill's HTML snippet
            skill_html = render_to_string(
                'user_skills/partials/_rated_skill_item.html',
                {
                    'skill': created_skill,
                    'skill_name': skill_name,
                    'skill_id': skill_id,
                    'skill_rating': rating,
                    'skill_category': skill_cat,
                    'skill_subcatgory': skill_subcat})
            return JsonResponse({
                'success': True,
                'message': message,
                'category_slug': slugify(category),
                'subcategory_slug': slugify(subcategory),
                'skill_html': skill_html  # Include the HTML to inject
            })

    def get(self, request, *args, **kwargs):
        return JsonResponse(
            {'success': False, 'message': 'Invalid request method. the request is not a post request'})


class SkillDashboardView(RedirectAnonymous):
    def get(self, request, *args, **kwargs):
        # This part handles the GET request as before

        if not request.user.is_authenticated:
            return redirect('login')
    

        admin_view = IsAdminView()
        is_admin_user = admin_view.is_admin(request.user)
        is_mgr_user = admin_view.is_manager(request.user)

        user = request.user
        if not is_admin_user and not is_mgr_user:
            #check for logged in user is a manager or not
            mgr_obj = Organization_tree.objects.get(empname= user.username)
            user_under_mgr = Organization_tree.objects.filter(mgrid=mgr_obj)

            if user_under_mgr:
                user_obj = User.objects.get(username = user.username)
                role_obj = Role.objects.get(name = 'manager')
                # print(user_obj, role_obj)
                UserRole.objects.create(user = user_obj, role = role_obj)


        issue_form = ReportIssueForm()
        # Serialize the grouped data directly in the serializer
        serializer = GroupedRatedSkillsSerializer(context={'user': user})
        skills_by_category = serializer.to_representation(None)

        serializer = GroupedUnratedSkillsSerializer(context={'user': user})
        unrated_skills_by_category = serializer.to_representation(None)

    # Fetch the certificates associated with the user
        user_certificates = CertificateUserMap.objects.filter(
            user_id=user).select_related('cert_id')

        # Prepare a list of certificates with their name and provider
        certificates_data = []
        for certificate_map in user_certificates:
            certificates_data.append({
                'cert_name': certificate_map.cert_id.name,  # Certificate name
                'cert_provider': certificate_map.cert_id.provider,  # Certificate provider
                'cert_status': certificate_map.status,
                'cert_map_id': certificate_map.id,
            })

        add_skill_form = Add_New_Data()


        mgr = Organization_tree.objects.filter(mgrid__empname=request.user.username)
        userlist = []
        for usr in mgr:
            userlist+=[usr.empname]

        unverified = SkillRating.objects.filter(user__username__in = userlist)
        unverified_null_mgrreview = unverified.filter(mgrreview__isnull=True)

       
        context = {
            'skills_by_category': skills_by_category,
            'unrated_skills_by_category': unrated_skills_by_category,
            'user_id': user.id,
            'admin_user': is_admin_user,
            'mgr_user': is_mgr_user,
            'add_skill': add_skill_form,
            'issue_form': issue_form,
            'certificates': certificates_data,
            'unverified': unverified_null_mgrreview,
        }
        return render(request, 'user_skills/skill_dashboard.html', context)

    def post(self, request, *args, **kwargs):
        add_skill_form = Add_New_Data(request.POST or None)

        if 'skill_submit' in request.POST:
            if add_skill_form.is_valid():

                # Get form values from the request
                category = request.POST.get('category').lower()
                subcategory = request.POST.get('subcategory').lower()
                # skill_name = request.POST.get('name')
                skill_name = add_skill_form.cleaned_data['skill_name'].lower()

                category_ins = Category.objects.get(name=category)
                subcategory_ins = Subcategory.objects.get(name=subcategory)
                categorysubcategory_ins = CategorySubcategory.objects.get(
                    category=category_ins, subcategory=subcategory_ins)
                newskill_ins, d1 = NewSkill.objects.get_or_create(
                    name=skill_name)
                categorysubcategorynewskill_ins, d2 = CategorySubcategoryNewSkill.objects.get_or_create(
                    categorysubcategory=categorysubcategory_ins, new_skill=newskill_ins)
                print(categorysubcategorynewskill_ins)
                return redirect('skill_dashboard')

        elif 'subcat_submit' in request.POST:
            if add_skill_form.is_valid():
                category = request.POST.get('category').lower()
                subcategory_name = add_skill_form.cleaned_data['subcategory'].lower(
                )
                skill_name = add_skill_form.cleaned_data['skill_name'].lower()

                category_ins = Category.objects.get(name=category)
                subcategory_ins, d1 = Subcategory.objects.get_or_create(
                    name=subcategory_name)
                categorysubcategory_ins, d5 = CategorySubcategory.objects.get_or_create(
                    category=category_ins, subcategory=subcategory_ins)
                newskill_ins, d2 = NewSkill.objects.get_or_create(
                    name=skill_name)

                sample_data_create, created_msg = NewSkill.objects.get_or_create(
                    name='Sample_Skill')
                create_sample_skill, d3 = CategorySubcategoryNewSkill.objects.get_or_create(
                    categorysubcategory=categorysubcategory_ins, new_skill=sample_data_create)
                categorysubcategorynewskill_ins, d4 = CategorySubcategoryNewSkill.objects.get_or_create(
                    categorysubcategory=categorysubcategory_ins, new_skill=newskill_ins)

                return redirect('skill_dashboard')

        elif 'cat_submit' in request.POST:
            if add_skill_form.is_valid():
                category_name = add_skill_form.cleaned_data['category'].lower()
                subcategory_name = add_skill_form.cleaned_data['subcategory'].lower(
                )
                skill_name = add_skill_form.cleaned_data['skill_name'].lower()

                category_ins, d1 = Category.objects.get_or_create(
                    name=category_name)
                subcategory_ins, d2 = Subcategory.objects.get_or_create(
                    name=subcategory_name)
                categorysubcategory_ins, d3 = CategorySubcategory.objects.get_or_create(
                    category=category_ins, subcategory=subcategory_ins)
                newskill_ins, d4 = NewSkill.objects.get_or_create(
                    name=skill_name)

                sample_data_create, created_msg = NewSkill.objects.get_or_create(
                    name='Sample_Skill')
                create_sample_skill, d5 = CategorySubcategoryNewSkill.objects.get_or_create(
                    categorysubcategory=categorysubcategory_ins, new_skill=sample_data_create)
                categorysubcategorynewskill_ins, d6 = CategorySubcategoryNewSkill.objects.get_or_create(
                    categorysubcategory=categorysubcategory_ins, new_skill=newskill_ins)

                return redirect('skill_dashboard')

        issue_form = ReportIssueForm(request.POST)
        if issue_form.is_valid():
            issue_form.instance.user = request.user
            issue_form.save()
            return redirect('skill_dashboard')

        # In case form submission fails or is incomplete
        return redirect('skill_dashboard')


# Decorate the class-based view with @login_required
@method_decorator(login_required, name='dispatch')
class SearchUnratedSkillsView(View):
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('query', '').strip()
        user = request.user
        rated_skills = SkillRating.objects.filter(
            user=user).select_related('skill')
        rated_skill_ids = rated_skills.values_list('skill_id', flat=True)

        unrated_skills = CategorySubcategoryNewSkill.objects.exclude(
            new_skill_id__in=rated_skill_ids).filter(
            new_skill__name__icontains=search_query).distinct()

        serializer = SearchUnratedSkiillSerializer(context={'user': user})
        unrated_skills_by_category = serializer.to_representation(
            unrated_skills)

        return render(request, 'user_skills/partials/_unrated_skills.html', {
            'unrated_skills_by_category': unrated_skills_by_category
        })


# Decorate the class-based view with @login_required
@method_decorator(login_required, name='dispatch')
class DeleteSkillByAjaxView(View):
    def post(self, request, *args, **kwargs):
        skill_id = request.POST.get('skill_id')
        user_id = request.POST.get('user_id')
        skill_subcat = request.POST.get('skill_subcategory')
        skill_cat = request.POST.get('skill_category')
        skill_name = request.POST.get('')

        if not skill_id or not user_id:
            return JsonResponse({'success': False,
                                 'message': 'Missing skill_id or user_id'})

        try:
            # Delete the skill rating
            skill = get_object_or_404(
                SkillRating, user_id=user_id, skill_id=skill_id)
            skill.delete()

            # Fetch the skill details
            deleted_skill = CategorySubcategoryNewSkill.objects.get(
                id=skill_id)
            category = deleted_skill.categorysubcategory.category.name
            subcategory = deleted_skill.categorysubcategory.subcategory.name

            # Render the deleted skill's HTML snippet
            skill_html = render_to_string(
                'user_skills/partials/_skill_item.html',
                {
                    'skill': deleted_skill,
                    'skill_category': category,
                    'skill_subcatgory': subcategory})

            return JsonResponse({
                'success': True,
                'category_slug': slugify(category),
                'subcategory_slug': slugify(subcategory),
                'skill_html': skill_html
            })

        except Exception as e:
            return JsonResponse(
                {'success': False, 'message': f'Error: {str(e)}'})

    def get(self, request, *args, **kwargs):
        return JsonResponse(
            {'success': False, 'message': 'Invalid request method. The request is not post'})


class TestDataNormalized(View):
    def get(self, request, **args,):
        # Fetch rated skills
        user = request.user

        rated_skills = SkillRating.objects.filter(user=user).select_related(
            'skill__categorysubcategory__category',
            'skill__categorysubcategory__subcategory',
            'skill__new_skill'
        )
        rated_skill_ids = rated_skills.values_list('skill_id', flat=True)

        # Group rated skills by category and subcategory
        skills_by_category = {}
        for rating in rated_skills:
            category = rating.skill.categorysubcategory.category.name
            subcategory = rating.skill.categorysubcategory.subcategory.name

            if category not in skills_by_category:
                skills_by_category[category] = {}
            if subcategory not in skills_by_category[category]:
                skills_by_category[category][subcategory] = []
            skills_by_category[category][subcategory].append(rating)

        return render(request, 'user_skills/demo_temp.html', {
            'skills_by_category': skills_by_category
        })


class CertificateUpload(View):
    def post(self, request):
        cert_name = request.POST.get('certification-name')
        cert_issue_by = request.POST.get('issued-by')
        cert_status = request.POST.get('certification-status')
        cert_issue_date = request.POST.get('issued-date')
        cert_expiry_date = request.POST.get('expiry-date')
        cert_url = request.POST.get('certification-url')

        if not (cert_name and cert_issue_by and cert_status and cert_url):
            return JsonResponse({"error": "All fields are required."})

        try:
            # Check if the certificate already exists or create it
            certificate, created = Certificate.objects.get_or_create(
                name=cert_name,
                provider=cert_issue_by
            )

            # Save certificate-user mapping
            user = request.user  # Assuming the user is logged in
            CertificateUserMap.objects.create(
                user_id=user,
                cert_id=certificate,
                issue_date=cert_issue_date,
                expiry_date=cert_expiry_date,
                status=cert_status,
                url=cert_url
            )

            context = {
                'cert_name': cert_name,
                'cert_issue_by': cert_issue_by,

            }

            return redirect('skill_dashboard')
        except Exception as e:
            return HttpResponse(str(e))


class CertificateEdit(View):
    def get(self, request, certificate_id):
        certificate_map = CertificateUserMap.objects.get(
            id=certificate_id, user_id=request.user)

        issue_date = certificate_map.issue_date.strftime(
            '%Y-%m-%d') if certificate_map.issue_date else ''
        expiry_date = certificate_map.expiry_date.strftime(
            '%Y-%m-%d') if certificate_map.expiry_date else ''

        context = {
            'cert_name': certificate_map.cert_id.name,
            'cert_issue_by': certificate_map.cert_id.provider,
            'cert_status': certificate_map.status,
            'cert_issue_date': issue_date,
            'cert_expiry_date': expiry_date,
            'cert_url': certificate_map.url,
            'certificate_id': certificate_map.id,
        }
        return render(request, 'user_skills/edit_certificate.html', context)

    def post(self, request, certificate_id):
        # Fetch the certificate-user mapping object
        certificate_map = get_object_or_404(
            CertificateUserMap,
            id=certificate_id,
            user_id=request.user)

        # Get the form data
        cert_name = request.POST.get('certification-name')
        cert_issue_by = request.POST.get('issued-by')
        cert_status = request.POST.get('certification-status')
        cert_issue_date = request.POST.get('issued-date')
        cert_expiry_date = request.POST.get('expiry-date')
        cert_url = request.POST.get('certification-url')

        # Validate required fields
        if not (cert_name and cert_issue_by and cert_status and cert_url):
            return JsonResponse({"error": "All fields are required."})

        # Update the related certificate object
        certificate = certificate_map.cert_id  # Fetch the related certificate instance
        certificate.name = cert_name
        certificate.provider = cert_issue_by
        certificate.save()

        # Update the certificate-user mapping fields
        certificate_map.status = cert_status
        certificate_map.issue_date = cert_issue_date
        certificate_map.expiry_date = cert_expiry_date
        certificate_map.url = cert_url
        certificate_map.save()

        # Redirect to the dashboard
        return redirect('skill_dashboard')


class CertificateDelete(View):

    def post(self, request, certificate_id):
        # Handle delete action via POST
        return self.delete(request, certificate_id)

    def delete(self, request, certificate_id):
        try:
            certificate = CertificateUserMap.objects.get(
                pk=certificate_id, user_id=request.user.id)
            # print(certificate)
            # certificate.cert_id.delete()
            certificate.delete()

            return redirect('skill_dashboard')

        except CertificateUserMap.DoesNotExist:
            return HttpResponse(
                "Certificate not found or you're not authorized to delete it.",
                status=404)


class ExportCertificateData(View):
    def get(self, request):
        # Fetch data for certificates and related user information
        admin_view = IsAdminView()
        is_admin_user = admin_view.is_admin(request.user)
        if not is_admin_user:
            return HttpResponse("Unauthorized kindly login as a admin user to use more features", status=401)
        try:
            certificateusermap_data = CertificateUserMap.objects.select_related(
                'user_id',
                'cert_id').values(
                'user_id__username',
                'cert_id__name',
                'cert_id__provider',
                'issue_date',
                'expiry_date',
                'status',
                'url')

            # Convert to DataFrame
            cert_df = pd.DataFrame(list(certificateusermap_data))

            # Select relevant columns for export
            selected_cols = [
                'user_id__username',
                'cert_id__name',
                'cert_id__provider',
                'issue_date',
                'expiry_date',
                'status',
                'url'
            ]
            download_df = cert_df[selected_cols]
            download_df.rename(
                columns={
                    'user_id__username': 'Username',
                    'cert_id__name': 'Certificate name',
                    'cert_id__provider': 'Provider',
                    'issue_date': 'issue_date',
                    'expiry_date': 'expiry_date',
                    'status': 'status',
                    'url': 'url'},
                inplace=True)

            # Prepare the CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="certificate_data.csv"'

            download_df.to_csv(response, index=False)

            return response
        except:
            return JsonResponse({'message':'There is no certificate data uploaded yet'})


class SearchRatingData(View):
    def get(self, request):
        query = request.GET.get('query', '').strip()
        # format_query = query.split(", ")

        # format_query = [i.strip() for i in query_to_format if i.strip()]

        if not query:
            # Return empty results for empty query
            return JsonResponse({'results': []})
        results = SkillRating.objects.filter(
            Q(skill__new_skill__name__icontains=query) |
            Q(skill__categorysubcategory__category__name__icontains=query) |
            Q(skill__categorysubcategory__subcategory__name__icontains=query) |
            Q(user__username__icontains=query)
        )

        # for free search with comma
        # search_query = Q()

        # for i in format_query:
        #     i = i.replace(", ", "")
        #     i = i.replace(",", "")
        #     search_query |= Q(skill__new_skill__name__icontains=i)
        #     search_query |= Q(skill__categorysubcategory__category__name__icontains=i)
        #     search_query |= Q(skill__categorysubcategory__subcategory__name__icontains=i)
        #     search_query |= Q(user__username__icontains=i)

        # results = SkillRating.objects.filter(search_query)

        return render(request, 'user_skills/partials/_admin_rated_list.html', {
            'rated_admin_data': results
        })


class ViewRatingData(View):
    def get(self, request):
        user_id = request.user
        admin_view = IsAdminView()
        is_admin_user = admin_view.is_admin(request.user)
        if not is_admin_user:
            return HttpResponse("Unauthorized kindly login as a admin user to use more features", status=401)
        # You can pass initial data here if needed
        return render(request,
                      'user_skills/admin_rated_data.html',
                      {'user_id': user_id,
                       'admin_user': is_admin_user})


class SearchSuggestion(View):
    def get(self, request):
        query = request.GET.get('query', '').strip()
        is_tod = request.GET.get('tog_data')

        if not query:
            return JsonResponse({'results': []})

        if is_tod == 'skill':
            # Query the SkillRating model to get the suggestions
            suggestions = SkillRating.objects.filter(
                Q(skill__new_skill__name__icontains=query) |
                Q(skill__categorysubcategory__category__name__icontains=query) |
                Q(skill__categorysubcategory__subcategory__name__icontains=query) |
                Q(user__username__icontains=query)
            ).distinct()

            # Format suggestions as a hierarchy: category -> subcategory ->
            # skill
            result = []
            for suggestion in suggestions:
                result.append({
                    'category': suggestion.skill.categorysubcategory.category.name,
                    'subcategory': suggestion.skill.categorysubcategory.subcategory.name,
                    'skill': suggestion.skill.new_skill.name,

                })
            unique_list = [
                dict(t) for t in {
                    frozenset(
                        d.items()) for d in result}]
            result = unique_list

        else:
            suggestion = suggestions = SkillRating.objects.filter(
                Q(user__username__icontains=query)
            ).distinct()

            result = []
            for suggestion in suggestions:
                result.append({
                    'user': suggestion.user.username,
                })

            unique_list = [
                dict(t) for t in {
                    frozenset(
                        d.items()) for d in result}]
            result = unique_list

        print(result)
        # print(result)
        return render(request,
                      'user_skills/partials/_admin_search_suggestion.html',
                      {'suggestion_data': result,
                       'type': is_tod,
                       })


class FetchSuggestionData(View):
    def get(self, request):
        skill = request.GET.get('skill')
        subcat = request.GET.get('subcat')
        cat = request.GET.get('cat')
        user_name = request.GET.get('user_name')

        # Check if the necessary query parameters are present
        # if not skill or not subcat or not cat:
        #     return JsonResponse({'error': 'Missing parameters'}, status=400)

        if skill and subcat and cat:
            # Query SkillRating model with the provided skill, subcategory, and
            # category
            results = SkillRating.objects.filter(
                Q(skill__new_skill__name__icontains=skill),
                Q(skill__categorysubcategory__category__name__icontains=cat),
                Q(skill__categorysubcategory__subcategory__name__icontains=subcat)
            )
        elif user_name:
            results = SkillRating.objects.filter(
                Q(user__username__icontains=user_name))
        # print(results)
        # Render the results in the appropriate template
        return render(request,
                      'user_skills/partials/_show_suggested_data_result.html',
                      {'rated_admin_data': results})



class ManagerRateEmp(View):
    def get(self, request):
        admin_view = IsAdminView()
        is_admin_user = admin_view.is_admin(request.user)
        is_mgr_user = admin_view.is_manager(request.user)
        mgr_name = request.user.username
        mgr_obj = Organization_tree.objects.get(empname=mgr_name)
        user_under_mgr = Organization_tree.objects.filter(mgrid=mgr_obj)
        user_list = []
        for user_name in user_under_mgr:
            user_list += [user_name.empname]

        try:
            skill_rated = SkillRating.objects.filter(user__username__in = user_list).order_by('user__username', 'id')
        except:
            print(f'unable to find records of {user_name.empname}')

            
        return render(request, 'user_skills/manager_rate_user.html', {'users_ratings': skill_rated, 'user_list': user_list, 'admin_user': is_admin_user, 'mgr_user': is_mgr_user,})
    

class ManagerRateAjax(View):
    def post(self, request):
        rating_id = request.POST.get('rating_id')
        rating = int(request.POST.get('rating'))

        if rating < 1 or rating > 5:
            return JsonResponse(
                {'success': False, 'message': 'Invalid rating value.'})
        
        try:
            rated_obj = SkillRating.objects.get(pk=rating_id)
            rated_obj.mgrreview = rating
            rated_obj.save()
            
            return JsonResponse({'success': True, 'message': 'Rating updated successfully!'})
        except:
            print(f'error{rating_id}{rating}')
            return JsonResponse({'success': False, 'message': 'Invalid request or rating.'})




class EmailForManager(View):
    def get(self, request, *args, **kwargs):
        mgrlist = []

        unverified_ratings = SkillRating.objects.filter(mgrreview__isnull=True)

        for rating in unverified_ratings:
            employee = Organization_tree.objects.get(empname=rating.user.username)
            if employee.mgrid:
                mgrlist.append(employee.mgrid.empname)

        mgr_unique_set = set(mgrlist)
        mgrlist = list(mgr_unique_set)

        # send_mail(
        #     subject="Review of Skills Rated by Your Team Members",
        #     message = "Dear manager,The skills ratings submitted by your team are available for review. Please take a moment to go through them. Your feedback is appreciated.",
        #     from_email="aswaththamanpersonal@gmail.com",  
        #     recipient_list=mgrlist,  
        #     fail_silently=False,
        # )
        
        return HttpResponse(f"Test email sent successfully! to {mgrlist}")
    

class CertificateTableView(View):
    def get(self, request):
        all_cert = CertificateUserMap.objects.all()

        return render(request, 'user_skills/certificate_table.html', {'all_cert': all_cert})
    
