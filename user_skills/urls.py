from django.urls import path

from .views import SkillDashboardView, HomeViewRedirect, ExportCsvRatingsDataView, UpdateRatingView, SearchUnratedSkillsView, DeleteSkillByAjaxView, CertificateUpload, ExportCertificateData, CertificateEdit, CertificateDelete
from .views import TestDataNormalized, ViewRatingData, SearchRatingData, SearchSuggestion, FetchSuggestionData, ManagerRateEmp, ManagerRateAjax, EmailForManager, CertificateTableView
urlpatterns = [

    path('dashboard/', SkillDashboardView.as_view(), name='skill_dashboard'),
    path(
        'user_skills/redirect',
        HomeViewRedirect.as_view(),
        name='redirect_home_page'),
    path(
        'export_review_data/',
        ExportCsvRatingsDataView.as_view(),
        name='export_review_data'),
    path('update-rating/', UpdateRatingView.as_view(), name='update_rating'),
    path('search-unrated-skills/',
         SearchUnratedSkillsView.as_view(),
         name='search_unrated_skills'),
    path(
        'delete-skill-by-ajax/',
        DeleteSkillByAjaxView.as_view(),
        name='delete_by_ajax'),

    path('check_data/', TestDataNormalized.as_view()),
    path(
        'certificate/add/',
        CertificateUpload.as_view(),
        name='certificate_add'),
    path(
        "export_certificate_data/",
        ExportCertificateData.as_view(),
        name="export_cert_data"),
    path(
        "edit_certificate/<int:certificate_id>/",
        CertificateEdit.as_view(),
        name='edit_certificate'),
    path(
        "delete_certificate/<int:certificate_id>/",
        CertificateDelete.as_view(),
        name='delete_certificate'),
    path(
        "admin_view/rated_data/",
        ViewRatingData.as_view(),
        name='admin_view_rated'),
    path(
        "admin_rated_data/search/",
        SearchRatingData.as_view(),
        name='admin_rated_search'),
    # path("admin_rated_data/searchbyuser/", SearchRatingUser.as_view(), name= 'admin_rated_search_user'),
    path(
        "admin_rated_data/searchsuggestion/",
        SearchSuggestion.as_view(),
        name='admin_search_suggestion'),
    path(
        "admin_reted_data/selected_suggestion_data/",
        FetchSuggestionData.as_view(),
        name='admin_suggested_result'),

    path(
        "manager/rate_emp/", 
        ManagerRateEmp.as_view(), 
        name='managerpage'
    ),

    path(
        "manager/view_ratings/", 
        ManagerRateAjax.as_view(), 
        name='managerrateajax'
    ),

    path("email_test/", EmailForManager.as_view(), name='emailtest'),

    path("certificate/table/", CertificateTableView.as_view(), name='certificate_table'),

    
]
