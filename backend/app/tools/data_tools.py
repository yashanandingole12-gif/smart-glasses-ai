from typing import Dict, Any, Optional
from backend.app.services.data_analytics_engine import data_analytics_engine

def tabular_data_query(query: str) -> Dict[str, Any]:
    """
    Query the active uploaded document or tabular financial dataset with natural language.
    """
    return data_analytics_engine.query_dataset(query=query)

def tabular_data_operation(operation: str, dataset_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute statistical calculation, anomaly detection, or dataset summarization on tabular data.
    """
    return data_analytics_engine.execute_operation(operation=operation, dataset_name=dataset_name)
