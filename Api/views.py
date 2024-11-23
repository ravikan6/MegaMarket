from django.shortcuts import render
from cloudinary.uploader import upload_image
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
<<<<<<< HEAD
=======
from Common.models import Image
>>>>>>> 1ea1b6c (Reinitialize repository and commit existing changes)

@login_required
def image_upload(request):
    context = {}
    if request.method == 'POST':
        image = request.FILES.get('image', None)
        if not image:
            context['error'] = 'No image provided'
        else:
            try:
<<<<<<< HEAD
                image = upload_image(image)
                context = {
                    'url': image.build_url(),
                    'public_id': image.public_id,
                    'format': image.format
                }
            except Exception as e:
=======
                image = upload_image(image, use_filename_as_display_name=True, auto_tagging=0.5)
                img = Image(
                    url=image.public_id,
                    alt=image.metadata.get('display_name', '')
                )
                img.save()
                context = {
                    'url': img.get_https_url(),
                    'public_id': img.url,
                    'format': image.format
                }
            except Exception as e:
                raise e
                print(str(e))
>>>>>>> 1ea1b6c (Reinitialize repository and commit existing changes)
                context['error'] = 'Image upload failed'
    return render(request, 'upload_image.html', context)