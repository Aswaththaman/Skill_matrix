from rest_framework import serializers
from .models import SkillRating, NewSkill, CategorySubcategoryNewSkill


def data_formatter_rated(items):
    grouped_data = {}

    for rating in items:
        category = rating.skill.categorysubcategory.category.name
        subcategory = rating.skill.categorysubcategory.subcategory.name

        if category not in grouped_data:
            grouped_data[category] = {}

        if subcategory not in grouped_data[category]:
            grouped_data[category][subcategory] = []

        grouped_data[category][subcategory].append(rating)

    return grouped_data


class GroupedRatedSkillsSerializer(serializers.Serializer):
    """
    Serializer to group rated skills by category and subcategory directly in the serializer.
    """

    def to_representation(self, instance):
        # Grouping logic
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError(
                "User is required in the serializer context.")

        rated_skills = SkillRating.objects.filter(
            user=user).select_related('skill')
        return data_formatter_rated(rated_skills)


class GroupedUnratedSkillsSerializer(serializers.Serializer):
    """
    Serializer to group unrated skills by category and subcategory.
    """

    def to_representation(self, instance):
        # Grouping logic for unrated skills
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError(
                "User is required in the serializer context.")

        rated_skills = SkillRating.objects.filter(
            user=user).select_related('skill')
        rated_skill_ids = rated_skills.values_list('skill_id', flat=True)
        unrated_skills = CategorySubcategoryNewSkill.objects.exclude(
            id__in=rated_skill_ids)

        grouped_data = {}

        for skill in unrated_skills:
            category = skill.categorysubcategory.category.name
            subcategory = skill.categorysubcategory.subcategory.name

            if category not in grouped_data:
                grouped_data[category] = {}

            if subcategory not in grouped_data[category]:
                grouped_data[category][subcategory] = []

            grouped_data[category][subcategory].append(skill)

        return grouped_data


class SearchUnratedSkiillSerializer(serializers.Serializer):
    """
    serializer for searching unrated skill
    """

    def to_representation(self, instance):
        unrated_skills_by_category = {}
        for skill in instance:
            category = skill.categorysubcategory.category.name
            subcategory = skill.categorysubcategory.subcategory.name

            if category not in unrated_skills_by_category:
                unrated_skills_by_category[category] = {}

            if subcategory not in unrated_skills_by_category[category]:
                unrated_skills_by_category[category][subcategory] = []

            unrated_skills_by_category[category][subcategory].append(skill)

        return unrated_skills_by_category
