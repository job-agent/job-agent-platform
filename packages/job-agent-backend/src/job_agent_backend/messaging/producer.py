"""RabbitMQ producer for sending scrape job requests."""

import json
import logging
import uuid
from typing import Iterator, Optional

import pika
from job_scrapper_contracts import ScrapeJobsFilter, ScrapeJobsRequest, ScrapeJobsResponse

from job_agent_backend.messaging.connection import RabbitMQConnection


class ScrapperProducer:
    """RabbitMQ producer that sends scrape job requests using RPC pattern.

    Sends requests to job.scrape.request queue and waits for responses
    in a temporary reply queue.
    """

    REQUEST_QUEUE = "job.scrape.request"
    RESPONSE_TIMEOUT = 300  # 5 minutes timeout for scraping operations

    def __init__(self, rabbitmq_url: Optional[str] = None):
        """Initialize the producer.

        Args:
            rabbitmq_url: RabbitMQ connection URL
        """
        self.rabbitmq_connection = RabbitMQConnection(rabbitmq_url)
        self.logger = logging.getLogger(__name__)
        self.responses: list[ScrapeJobsResponse] = []
        self.is_complete: bool = False
        self.correlation_id: Optional[str] = None

    def send_scrape_request(
        self,
        min_salary: Optional[int] = 4000,
        employment_location: Optional[str] = "remote",
        posted_after: Optional[str] = None,
        timeout: int = 30,
    ) -> ScrapeJobsResponse:
        """Send a scrape jobs request and wait for response.

        Args:
            min_salary: Minimum salary requirement
            employment_location: Employment type or location
            posted_after: ISO format datetime string for filtering by post date
            timeout: Scraper timeout in seconds

        Returns:
            ScrapeJobsResponse: Response containing scraped jobs or error

        Raises:
            TimeoutError: If no response is received within RESPONSE_TIMEOUT
            Exception: If response indicates an error
        """
        channel = self.rabbitmq_connection.connect()

        channel.queue_declare(queue=self.REQUEST_QUEUE, durable=True)

        result = channel.queue_declare(queue="", exclusive=True)
        reply_queue = result.method.queue

        self.correlation_id = str(uuid.uuid4())
        self.responses = []
        self.is_complete = False

        channel.basic_consume(
            queue=reply_queue,
            on_message_callback=self._on_response,
            auto_ack=True,
        )

        filter_payload: ScrapeJobsFilter = {}
        if min_salary is not None:
            filter_payload["min_salary"] = min_salary
        if employment_location is not None:
            filter_payload["employment_location"] = employment_location
        if posted_after:
            filter_payload["posted_after"] = posted_after

        request: ScrapeJobsRequest = {"timeout": timeout}
        if filter_payload:
            request["filters"] = filter_payload

        self.logger.info(f"Sending scrape request with correlation_id={self.correlation_id}")

        channel.basic_publish(
            exchange="",
            routing_key=self.REQUEST_QUEUE,
            properties=pika.BasicProperties(
                reply_to=reply_queue,
                correlation_id=self.correlation_id,
                content_type="application/json",
                delivery_mode=2,
            ),
            body=json.dumps(request).encode("utf-8"),
        )

        connection = self.rabbitmq_connection.connection
        timeout_counter = 0
        while not self.is_complete and timeout_counter < self.RESPONSE_TIMEOUT:
            connection.process_data_events(time_limit=1)
            timeout_counter += 1

        if not self.is_complete:
            self.rabbitmq_connection.close()
            raise TimeoutError(
                f"No completion response received within {self.RESPONSE_TIMEOUT} seconds"
            )

        self.rabbitmq_connection.close()

        all_jobs = []
        for response in self.responses:
            if response.get("jobs"):
                all_jobs.extend(response["jobs"])
            if not response["success"]:
                raise Exception(f"Scraper error: {response.get('error', 'Unknown error')}")

        aggregated_response: ScrapeJobsResponse = {
            "jobs": all_jobs,
            "success": True,
            "error": None,
            "jobs_count": len(all_jobs),
        }

        self.logger.info(
            f"Received {len(self.responses)} responses with {len(all_jobs)} total jobs for correlation_id={self.correlation_id}"
        )

        return aggregated_response

    def _on_response(
        self,
        channel: pika.channel.Channel,
        method: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        body: bytes,
    ) -> None:
        """Callback for processing response messages.

        Args:
            channel: Pika channel
            method: Delivery method
            properties: Message properties
            body: Message body
        """
        message_payload = body.decode("utf-8")
        is_expected_message = properties.correlation_id == self.correlation_id
        self.logger.info(
            "Received message from queue with correlation_id=%s expected=%s payload=%s",
            properties.correlation_id,
            is_expected_message,
            message_payload,
        )
        if is_expected_message:
            response = json.loads(message_payload)
            self.responses.append(response)

            if response.get("is_complete", False):
                self.is_complete = True
                self.logger.debug(
                    f"Received completion response for correlation_id={self.correlation_id}"
                )
            else:
                jobs_count = response.get("jobs_count", 0)
                self.logger.info(
                    f"Received batch response with {jobs_count} jobs for correlation_id={self.correlation_id}"
                )

    def scrape_jobs_streaming(
        self,
        min_salary: Optional[int] = 4000,
        employment_location: Optional[str] = "remote",
        posted_after: Optional[str] = None,
        timeout: int = 30,
    ) -> Iterator[ScrapeJobsResponse]:
        """Send a scrape jobs request and yield responses as they arrive.

        This method yields each batch of jobs as soon as it's received from the scrapper,
        allowing for incremental processing instead of waiting for all pages.

        Args:
            min_salary: Minimum salary requirement
            employment_location: Employment type or location
            posted_after: ISO format datetime string for filtering by post date
            timeout: Scraper timeout in seconds

        Yields:
            ScrapeJobsResponse: Each page response containing a batch of jobs

        Raises:
            TimeoutError: If no response is received within RESPONSE_TIMEOUT
            Exception: If any response indicates an error
        """
        channel = self.rabbitmq_connection.connect()

        channel.queue_declare(queue=self.REQUEST_QUEUE, durable=True)

        result = channel.queue_declare(queue="", exclusive=True)
        reply_queue = result.method.queue

        self.correlation_id = str(uuid.uuid4())
        self.responses = []
        self.is_complete = False

        channel.basic_consume(
            queue=reply_queue,
            on_message_callback=self._on_response,
            auto_ack=True,
        )

        filter_payload: ScrapeJobsFilter = {}
        if min_salary is not None:
            filter_payload["min_salary"] = min_salary
        if employment_location is not None:
            filter_payload["employment_location"] = employment_location
        if posted_after:
            filter_payload["posted_after"] = posted_after

        request: ScrapeJobsRequest = {"timeout": timeout}
        if filter_payload:
            request["filters"] = filter_payload

        self.logger.info(f"Sending scrape request with correlation_id={self.correlation_id}")

        channel.basic_publish(
            exchange="",
            routing_key=self.REQUEST_QUEUE,
            properties=pika.BasicProperties(
                reply_to=reply_queue,
                correlation_id=self.correlation_id,
                content_type="application/json",
                delivery_mode=2,
            ),
            body=json.dumps(request).encode("utf-8"),
        )

        connection = self.rabbitmq_connection.connection
        timeout_counter = 0
        last_yielded_index = 0

        while not self.is_complete and timeout_counter < self.RESPONSE_TIMEOUT:
            connection.process_data_events(time_limit=1)
            timeout_counter += 1

            while last_yielded_index < len(self.responses):
                response = self.responses[last_yielded_index]
                last_yielded_index += 1

                if not response["success"]:
                    self.rabbitmq_connection.close()
                    raise Exception(f"Scraper error: {response.get('error', 'Unknown error')}")

                yield response

        if not self.is_complete:
            self.rabbitmq_connection.close()
            raise TimeoutError(
                f"No completion response received within {self.RESPONSE_TIMEOUT} seconds"
            )

        self.rabbitmq_connection.close()
        self.logger.info(
            f"Streaming completed: {len(self.responses) - 1} batches for correlation_id={self.correlation_id}"
        )
