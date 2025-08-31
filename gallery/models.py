from django.db import models
from django.contrib.auth.models import User
import face_recognition
from django.core.files.storage import default_storage


class EventPhoto(models.Model):
    file = models.ImageField(upload_to="event_photos/")
    # Store list of face encodings (multiple faces per photo)
    face_encodings = models.JSONField(blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        Override save() to auto-generate face encodings when photo is uploaded.
        Supports multiple faces in one photo.
        """
        super().save(*args, **kwargs)  # save image first
        image_path = default_storage.path(self.file.name)
        img = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(img)
        if encodings:
            # store all encodings as list of lists
            self.face_encodings = [enc.tolist() for enc in encodings]
            super().save(update_fields=["face_encodings"])

    def __str__(self):
        return self.file.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    selfie = models.ImageField(upload_to="selfies/", null=True, blank=True)
    selfie_encoding = models.JSONField(blank=True, null=True)  # one encoding per user
    matched_photos = models.ManyToManyField(EventPhoto, blank=True)

    def save(self, *args, **kwargs):
        """
        Auto-generate face encoding when selfie is uploaded.
        """
        super().save(*args, **kwargs)
        if self.selfie:
            image_path = default_storage.path(self.selfie.name)
            img = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(img)
            if encodings:
                self.selfie_encoding = encodings[0].tolist()  # only one face for a selfie
                super().save(update_fields=["selfie_encoding"])

    def __str__(self):
        return self.user.username
