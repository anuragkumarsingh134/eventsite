from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import EventPhoto, UserProfile
import numpy as np
import face_recognition


def home(request):
    return HttpResponse("""
        <h1>Welcome to Event Photos</h1>
        <p><a href='/upload_selfie/'>Upload Selfie</a></p>
        <p><a href='/my_photos/'>My Photos</a></p>
        <p><a href='/admin/'>Admin Panel</a></p>
    """)


@login_required
def upload_selfie(request):
    """
    User uploads a selfie, system saves encoding and finds matching photos.
    """
    if request.method == "POST" and request.FILES.get("selfie"):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.selfie = request.FILES["selfie"]
        profile.save()  # selfie encoding auto-generated in model

        # match user selfie with event photos
        if profile.selfie_encoding:
            photos = EventPhoto.objects.all()
            for photo in photos:
                if not photo.face_encodings:
                    continue
                for enc in photo.face_encodings:
                    results = face_recognition.compare_faces(
                        [np.array(enc)],
                        np.array(profile.selfie_encoding),
                        tolerance=0.6
                    )
                    if True in results:
                        profile.matched_photos.add(photo)

        return redirect("my_photos")

    return render(request, "upload_selfie.html")


@login_required
def my_photos(request):
    """
    Show only the photos matched with this user.
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, "my_photos.html", {"photos": profile.matched_photos.all()})
