from rest_framework.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse


class ActiveJobConflict(ValidationError):
    status_code = 409

    def __init__(self):
        # During APIException.__init__(), Django Rest Framework
        # turn everything in self.detail into string by using force_text.
        # Declare detail afterwards circumvent this behavior.
        super(ActiveJobConflict, self).__init__()
        self.detail = {
            "error": "Resource is being used by running jobs.",
        }
        return JsonResponse(detail)

