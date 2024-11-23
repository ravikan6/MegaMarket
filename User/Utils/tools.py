from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_verification_email_otp(email, otp):
    context = {
        "receiver_name": "User",
        "otp_code": otp,
    }

    receiver_email = email
    template_name = "email/otp.html"
    convert_to_html_content =  render_to_string(
      template_name=template_name,
      context=context
    )

    plain_message = strip_tags(convert_to_html_content)

    sent = send_mail(
      subject="Email Verification OTP",
      message=plain_message,
      from_email=settings.EMAIL_HOST_USER,
      recipient_list=[receiver_email,]  ,
      html_message=convert_to_html_content,
      fail_silently=True  
    )

    return sent


def generate_otp():
    import random
    return random.randint(100000, 999999)


OIDC_RSA_PRIVATE_KEY="""-----BEGIN PRIVATE KEY-----
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
oeaDu6x6aWDE50mCwXwFpAWICbUG
-----END PRIVATE KEY-----"""