from django.conf import settings
from django.contrib import admin
from django.http import FileResponse, HttpResponseNotFound
from django.urls import include, path

# The agnostic widget engine lives at <repo>/widget/src/embed.js. Serve it from
# the backend so the customer site loads JS and API from the same origin (one
# source, no copy in the theme). In production this can move to a CDN/static
# host; the customer's <script src> just points wherever it is served.
WIDGET_JS = settings.BASE_DIR.parent / "widget" / "src" / "embed.js"


def widget_js(request):
    if not WIDGET_JS.exists():
        return HttpResponseNotFound("embed.js not found")
    resp = FileResponse(open(WIDGET_JS, "rb"), content_type="application/javascript")
    resp["Access-Control-Allow-Origin"] = "*"
    resp["Cache-Control"] = "no-cache"
    return resp


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.chat.urls")),
    path("embed.js", widget_js),
]
