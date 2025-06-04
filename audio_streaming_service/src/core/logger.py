import logging

logging.basicConfig(
    level=logging.DEBUG, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logging.getLogger("aiokafka").setLevel(logging.WARNING)
logging.getLogger("faststream").setLevel(logging.INFO)  # или WARNING
logging.getLogger("aiobotocore").setLevel(logging.CRITICAL)
logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger("boto3").setLevel(logging.WARNING)      
logging.getLogger("urllib3").setLevel(logging.WARNING)      

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) 