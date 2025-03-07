# from django.contrib import admin

# # Register your models here.
# from django.contrib import admin
# from .models import Category, Subcategory, NewSkill, UserRole, SkillRating, Role


# # @admin.register(NewSkill)
# # class NewSkillAdmin(admin.ModelAdmin):
# #     list_display = ('category', 'subcategory', 'name')
# #     search_fields = ('category', 'subcategory', 'name')


# # @admin.register(UserNewSkill)
# # class UserNewSkillAdmin(admin.ModelAdmin):
# #     list_display = ('user', 'skill')
# #     search_fields = ('user__username', 'skill__name')
# admin.site.register(Category)
# admin.site.register(Subcategory)
# admin.site.register(NewSkill)
# admin.site.register(SkillRating)
# admin.site.register(UserRole)
# admin.site.register(Role)


from django.contrib import admin
from .models import Organization_tree, Subcategory, NewSkill, UserRole, SkillRating, Role, CategorySubcategory, CategorySubcategoryNewSkill, UserReport


# admin.site.register(Category)
# admin.site.register(Subcategory)
# admin.site.register(NewSkill)
admin.site.register(SkillRating)
admin.site.register(Role)
admin.site.register(UserRole)
admin.site.register(UserReport)
admin.site.register(Organization_tree)
# admin.site.register(CategorySubcategoryNewSkill)
# admin.site.register(CategorySubcategory)
