from rest_framework.throttling import ScopedRateThrottle


class OrgSearchThrottle(ScopedRateThrottle):
    scope = "org_search"


class OrgCreateThrottle(ScopedRateThrottle):
    scope = "org_create"


class OrgJoinThrottle(ScopedRateThrottle):
    scope = "org_join"


# Add to settings.py:
#
# REST_FRAMEWORK = {
#     ...
#     "DEFAULT_THROTTLE_CLASSES": [...],
#     "DEFAULT_THROTTLE_RATES": {
#         "org_search": "30/min",
#         "org_create": "5/hour",
#         "org_join": "20/hour",
#     },
# }