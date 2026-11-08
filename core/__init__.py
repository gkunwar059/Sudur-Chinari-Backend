import re
import django.http.request

# Allow underscores in hostnames for Docker container names (e.g. sudur_backend)
# By default, Django enforces RFC 1034/1035 which disallows underscores.
django.http.request.host_validation_re = re.compile(
    r"^([a-z0-9._-]+|\[[a-f0-9]*:[a-f0-9\.:]+\])(:[0-9]+)?$",
    re.IGNORECASE,
)
