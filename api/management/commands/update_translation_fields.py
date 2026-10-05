from django.core.management.base import BaseCommand
from api.models import (
    Category,
    Author,
    District,
    Article,
    VideoItem,
    PhotoStory,
    BreakingNews,
    Partner,
    DistrictStats,
    DistrictCulture,
    DistrictPlace,
)

class Command(BaseCommand):
    help = "Copies existing English data into _en columns and synchronizes translation fields."

    def handle(self, *args, **options):
        # 1. Category
        for cat in Category.objects.all():
            if not cat.name_en and cat.name:
                cat.name_en = cat.name
            elif cat.name_en and not cat.name:
                cat.name = cat.name_en
            cat.save()

        # 2. Author
        for author in Author.objects.all():
            if not author.name_en and author.name:
                author.name_en = author.name
            if not author.bio_en and author.bio:
                author.bio_en = author.bio
            author.save()

        # 3. District
        for district in District.objects.all():
            if not district.name_en and district.name:
                district.name_en = district.name
            if not district.description_en and district.description:
                district.description_en = district.description
            if not district.meta_title_en:
                district.meta_title_en = district.name_en
            if not district.meta_description_en:
                district.meta_description_en = (district.description_en or "")[:160]
            district.save()

        # 4. Article
        for article in Article.objects.all():
            if not article.title_en and article.title:
                article.title_en = article.title
            if not article.excerpt_en and article.excerpt:
                article.excerpt_en = article.excerpt
            if not article.content_en and article.content:
                article.content_en = article.content
            if not article.imageCaption_en and article.imageCaption:
                article.imageCaption_en = article.imageCaption
            if not article.meta_title_en:
                article.meta_title_en = article.title_en
            if not article.meta_description_en:
                article.meta_description_en = (article.excerpt_en or "")[:160]
            article.save()

        # 5. VideoItem
        for video in VideoItem.objects.all():
            if not video.title_en and video.title:
                video.title_en = video.title
            video.save()

        # 6. PhotoStory
        for photo in PhotoStory.objects.all():
            if not photo.title_en and photo.title:
                photo.title_en = photo.title
            if not photo.description_en and photo.description:
                photo.description_en = photo.description
            photo.save()

        # 7. BreakingNews
        for item in BreakingNews.objects.all():
            if not item.text_en and item.text:
                item.text_en = item.text
            item.save()

        # 8. Partner
        for partner in Partner.objects.all():
            if not partner.name_en and partner.name:
                partner.name_en = partner.name
            if not partner.role_en and partner.role:
                partner.role_en = partner.role
            partner.save()

        # 9. DistrictStats
        for stats in DistrictStats.objects.all():
            if not stats.headquarters_en and stats.headquarters:
                stats.headquarters_en = stats.headquarters
            if not stats.majorRivers_en and stats.majorRivers:
                stats.majorRivers_en = stats.majorRivers
            stats.save()

        # 10. DistrictCulture
        for culture in DistrictCulture.objects.all():
            if not culture.folkDance_en and culture.folkDance:
                culture.folkDance_en = culture.folkDance
            if not culture.festivals_en and culture.festivals:
                culture.festivals_en = culture.festivals
            if not culture.cuisine_en and culture.cuisine:
                culture.cuisine_en = culture.cuisine
            if not culture.dialects_en and culture.dialects:
                culture.dialects_en = culture.dialects
            culture.save()

        # 11. DistrictPlace
        for place in DistrictPlace.objects.all():
            if not place.title_en and place.title:
                place.title_en = place.title
            if not place.description_en and place.description:
                place.description_en = place.description
            place.save()

        self.stdout.write(self.style.SUCCESS("Translation fields updated and synchronized successfully!"))
