import logging

logger = logging.getLogger(__name__)

class ReportAnalysis:
    def __init__(self, correlation_uuid: str):
        self.correlation_uuid = correlation_uuid

    def process(self, params: dict) -> dict:
        reports: list = params['reports']
        logger.info(f"{self.correlation_uuid}: Starting processing {len(reports)} reports")

        success_count = 0
        report_aggregate = list()
        for report in reports:
            if report['status'] == 'SUCCESS':
                success_count += 1
            report_aggregate.append(report)

        logger.info(f"{self.correlation_uuid}: Finished processing {len(reports)} reports")
        return {
            'status': 'SUCCESS',
            'correlation_uuid': self.correlation_uuid,
            'tool': 'report_analysis',
            'params': params,
            'message': 'Reports processed successfully.',
            'report': {
                'success_percentage': f"{100 * success_count / len(reports)}%",
                'report_aggregate': report_aggregate
            }
        }

