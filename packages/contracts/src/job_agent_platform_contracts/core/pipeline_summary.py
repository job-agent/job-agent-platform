from typing_extensions import TypedDict


class PipelineSummary(TypedDict):
    total_scraped: int
    total_filtered: int
    total_processed: int
