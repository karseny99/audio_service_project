import logging

logging.basicConfig(
    level=logging.DEBUG, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logging.getLogger("aiokafka").setLevel(logging.WARNING)
logging.getLogger("faststream").setLevel(logging.INFO)  # или WARNING


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) 