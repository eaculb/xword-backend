from datetime import datetime, timezone
from marshmallow import fields
from marshmallow_sqlalchemy import auto_field
from flask_resty import ApiError, ModelView
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.hybrid import hybrid_property


def now():
    return datetime.now(timezone.utc)


class SoftDeleteMixin:
    class Model:
        deleted_at = Column(TIMESTAMP, nullable=True)

        @hybrid_property
        def is_deleted(self):
            return self.deleted_at is not None

    class Schema:
        deleted_at = auto_field(dump_only=True)

        # Only for filtering.
        is_deleted = fields.Boolean(load_only=True, dump_only=True)

    class View(ModelView):
        def delete_item(self, item):
            if item.is_deleted:
                raise ApiError(409, {"code": "invalid_item.is_deleted"})

            item = super().delete_item(item)
            self.authorization.authorize_save_item(item)

            return item

        def delete_item_raw(self, item):
            return self.update_item_raw(item, self.make_delete_data())

        def make_delete_data(self):
            return {"deleted_at": now()}

        def undelete(self, id):
            item = self.get_item_or_404(id)

            item = self.undelete_item(item)
            self.commit()

            return self.make_item_response(item)

        def undelete_item(self, item):
            if not item.is_deleted:
                raise ApiError(409, {"code": "invalid_item.is_deleted"})

            return self.update_item(item, self.make_undelete_data())

        def make_undelete_data(self):
            return {"deleted_at": None}
