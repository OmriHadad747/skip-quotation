import flask
import pydantic as pyd

from typing import Tuple
from flask import jsonify
from flask import current_app as app

from skip_common_lib.middleware import job_quotation as middleware
from skip_common_lib.models import job as job_model
from skip_common_lib.models import customer as customer_model
from skip_common_lib.models import freelancer as freelancer_model
from skip_common_lib.database.freelancers import FreelancerDatabase as freelancers_db
from skip_common_lib.database.jobs import JobDatabase as jobs_db
from skip_common_lib.database.customers import CustomerDatabase as customers_db
from skip_common_lib.utils.errors import Errors as err
from skip_common_lib.utils.notifier import Notifier as notify


class JobQuotation:
    @classmethod
    @middleware.update_job_quotation
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

            notify.push_job_quotation(quotation, customer)

        except pyd.ValidationError as e:
            return err.validation_error(e)
        except Exception as e:
            return err.general_exception(e)

        return jsonify(message=f"notification pushed to customer {customer.email}"), 200

    @classmethod
    @middleware.update_job_approved_or_declined
    def confirm(cls, job_id: str) -> Tuple[flask.Response, int]:
        try:
            # get corresponding job
            job = job_model.Job(**jobs_db.get_job_by_id(job_id))

            # get corresponding freelancer
            freelancer = freelancer_model.Freelancer(
                **freelancers_db.get_freelancer_by_email(job.freelancer_email)
            )

            app.logger.debug(f"notifying freelancer about job {job.id} status: {job.job_status}")

            notify.push_quotation_confirmation(job, freelancer)

        except pyd.ValidationError as e:
            return err.validation_error(e)
        except Exception as e:
            return err.general_exception(e)