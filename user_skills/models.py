from django.db import models
from django.contrib.auth.models import User  # Using Django's default User model


class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Role name

    def __str__(self):
        return self.name


class UserRole(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_roles')
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_roles')
    # assigned_at = models.DateTimeField(auto_now_add=True)  # When the role
    # was assigned

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"

    class Meta:
        unique_together = ('user', 'role')


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)


class Subcategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)


class CategorySubcategory(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="category_subcategories")
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.CASCADE,
        related_name="subcategory_categories")

    def __str__(self):
        return f"{self.category.name} -> {self.subcategory.name}"

    class Meta:
        # Ensures a category-subcategory combination is unique
        unique_together = ('category', 'subcategory')


class NewSkill(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CategorySubcategoryNewSkill(models.Model):
    categorysubcategory = models.ForeignKey(
        CategorySubcategory,
        on_delete=models.CASCADE,
        related_name="category_subcategory_newskills")
    new_skill = models.ForeignKey(
        NewSkill,
        on_delete=models.CASCADE,
        related_name="newskill_subcategories")

    def __str__(self):
        return f"{
            self.categorysubcategory.category.name} -> {
            self.categorysubcategory.subcategory.name} -> {
            self.new_skill.name}"

    class Meta:
        # Ensures each skill is linked to a unique category-subcategory pair
        unique_together = ('categorysubcategory', 'new_skill')


class SkillRating(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='skill_ratings')
    skill = models.ForeignKey(
        CategorySubcategoryNewSkill,
        on_delete=models.CASCADE,
        related_name='skill_ratings')
    rating = models.PositiveSmallIntegerField()  # Rating between 1-5
    mgrreview = models.PositiveSmallIntegerField(blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{
            self.user.username} - {
            self.skill.categorysubcategory.category.name} > {
            self.skill.categorysubcategory.subcategory.name} > {
                self.skill.new_skill.name} - {
                    self.rating} stars "


class UserReport(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reports")
    report = models.TextField()  # Field to store the report content
    # Automatically stores the creation timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {
            self.user.username} on {
            self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class Certificate(models.Model):
    name = models.CharField(max_length=150)
    provider = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class CertificateUserMap(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    cert_id = models.ForeignKey(Certificate, on_delete=models.CASCADE)
    issue_date = models.DateField(blank=True)
    expiry_date = models.DateField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=[('active', 'Active'), ('expired', 'Expired'), ('revoked', 'Revoked')],
        default='active'
    )
    url = models.CharField(max_length=300)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'user_id',
                    'cert_id',
                    'issue_date',
                    'status'],
                name='unique_user_certificate')]

    def __str__(self):
        return f"{self.user_id.username} - {self.cert_id.name}"



class Organization_tree(models.Model):
    empname = models.CharField(max_length=200, unique=True)
    mgrid = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)  

    def __str__(self):
        return self.empname



