from typing import Optional

from pydantic import BaseModel

from wexample_app.common.service.service_mixin import ServiceMixin


class AbstractMiddleware(ServiceMixin, BaseModel):
    def __init__(self, **kwargs):
        # Manage ini order.
        BaseModel.__init__(self, **kwargs)
        ServiceMixin.__init__(self)

    @classmethod
    def get_class_name_suffix(cls) -> Optional[str]:
        return 'Middleware'
