"""RabbitMQ producer for sending scrape job requests."""

import json
import logging
import uuid
from typing import Optional

import pika
from job_scrapper_contracts import ScrapeJobsRequest, ScrapeJobsResponse

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
        self.response: Optional[ScrapeJobsResponse] = None
        self.correlation_id: Optional[str] = None

    def send_scrape_request(
        self,
        salary: int = 4000,
        employment: str = "remote",
        posted_after: Optional[str] = None,
        timeout: int = 30,
    ) -> ScrapeJobsResponse:
        """Send a scrape jobs request and wait for response.

        Args:
            salary: Minimum salary requirement
            employment: Employment type
            posted_after: ISO format datetime string for filtering by post date
            timeout: Scraper timeout in seconds

        Returns:
            ScrapeJobsResponse: Response containing scraped jobs or error

        Raises:
            TimeoutError: If no response is received within RESPONSE_TIMEOUT
            Exception: If response indicates an error
        """
        channel = self.rabbitmq_connection.connect()

        # Declare request queue (idempotent)
        channel.queue_declare(queue=self.REQUEST_QUEUE, durable=True)

        # Create temporary reply queue
        result = channel.queue_declare(queue="", exclusive=True)
        reply_queue = result.method.queue

        # Generate correlation ID for matching request/response
        self.correlation_id = str(uuid.uuid4())
        self.response = None

        # Setup consumer for reply queue
        channel.basic_consume(
            queue=reply_queue,
            on_message_callback=self._on_response,
            auto_ack=True,
        )

        # Build request
        request: ScrapeJobsRequest = {
            "salary": salary,
            "employment": employment,
            "timeout": timeout,
        }
        if posted_after:
            request["posted_after"] = posted_after

        # Send request
        self.logger.info(
            f"Sending scrape request with correlation_id={self.correlation_id}"
        )

        channel.basic_publish(
            exchange="",
            routing_key=self.REQUEST_QUEUE,
            properties=pika.BasicProperties(
                reply_to=reply_queue,
                correlation_id=self.correlation_id,
                content_type="application/json",
                delivery_mode=2,  # Make message persistent
            ),
            body=json.dumps(request).encode("utf-8"),
        )

        # Wait for response with timeout
        connection = self.rabbitmq_connection.connection
        timeout_counter = 0
        while self.response is None and timeout_counter < self.RESPONSE_TIMEOUT:
            connection.process_data_events(time_limit=1)
            timeout_counter += 1

        if self.response is None:
            self.rabbitmq_connection.close()
            raise TimeoutError(
                f"No response received within {self.RESPONSE_TIMEOUT} seconds"
            )

        response = self.response
        self.rabbitmq_connection.close()

        # Check for errors in response
        if not response["success"]:
            raise Exception(f"Scraper error: {response.get('error', 'Unknown error')}")

        self.logger.info(
            f"Received response with {response['jobs_count']} jobs for correlation_id={self.correlation_id}"
        )

        return response

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
        if properties.correlation_id == self.correlation_id:
            self.response = json.loads(body.decode("utf-8"))
            self.logger.debug(f"Received response for correlation_id={self.correlation_id}")
