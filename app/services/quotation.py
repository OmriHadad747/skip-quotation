import flask
import pydantic as pyd

from typing import Tuple
from flask import jsonify
from flask import current_app as app
from firebase_admin import messaging
from app import middlewares
from app.utils.errors import Errors as err
from skip_db_lib.models import job as job_model
from skip_db_lib.models import customer as customer_model
from skip_db_lib.database.freelancers import FreelancerDatabase as freelancers_db
from skip_db_lib.database.jobs import JobDatabase as jobs_db
from skip_db_lib.database.customers import CustomerDatabase as customers_db


class JobQuotation:
    @classmethod
    @pyd.validate_arguments
    def _notify_customer(
        cls, quotation: job_model.JobQuotation, customer: customer_model.Customer
    ) -> None:
        # TODO write docstring
        app.logger.info("notifying customer about job quotation")

        msg = messaging.Message(
            data=quotation.quotation_to_str(), token=customer.registration_token
        )
        # resp = messaging.send(msg, dry_run=True)

        # app.logger.debug(f"customer notified with message {resp}")

    @classmethod
    @middlewares.update_job_quotation
    def quote(cls, job_id, quotation: job_model.JobQuotation) -> Tuple[flask.Response, int]:
        """Retrieval of job by the given 'job_id',
        Retrieval of the corresponding customer and notify him about the quotation.

        Args:
            job_id (_type_): An id of a job.
            quotation (job_model.JobQuotation)

        Returns:
            Tuple[flask.Response, int]
        """
        try:
            # get corresponding job
            job = job_model.Job(**jobs_db.get_job_by_id(job_id))

            # get corresponding customer
            customer = customer_model.Customer(
                **customers_db.get_customer_by_email(job.customer_email)
            )

            cls._notify_customer(quotation, customer)

        except pyd.ValidationError as e:
            return err.validation_error(e)
        except Exception as e:
            return err.general_exception(e)

        return jsonify(message=f"notification pushed to customer {customer.email}"), 200

    @classmethod
    def approve() -> Tuple[flask.Response, int]:
        pass

    @classmethod
    def decline() -> Tuple[flask.Response, int]:
        pass
