"""
One-off command: copy recipe images from the local media/ folder to Cloudinary.

Run it once on Heroku after setting CLOUDINARY_URL:
    python manage.py move_images_to_cloudinary
"""
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from core.models import Recipe


class Command(BaseCommand):
    help = "Upload recipe images that are in media/ to Cloudinary."

    def handle(self, *args, **options):
        backend = settings.STORAGES["default"]["BACKEND"]
        if "cloudinary" not in backend:
            raise CommandError(
                "CLOUDINARY_URL is not set, so there is nowhere to upload to."
            )

        moved = 0
        missing = 0
        for recipe in Recipe.objects.exclude(image="").exclude(image=None):
            local_file = Path(settings.MEDIA_ROOT) / recipe.image.name
            if not local_file.exists():
                self.stdout.write(f"Skipped {recipe.title}: no local file")
                missing += 1
                continue
            with local_file.open("rb") as image_file:
                recipe.image.save(local_file.name, File(image_file), save=True)
            self.stdout.write(f"Uploaded {recipe.title}")
            moved += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done: {moved} uploaded, {missing} skipped."
        ))
