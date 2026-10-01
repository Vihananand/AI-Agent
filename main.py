from agent.agent import AgentSession, run_agent
from agent.logging_config import get_logger, start_run_logging, stop_run_logging

logger = get_logger("main")

print("YOU CAN ASK AS MUCH AS YOU WANT BUT IF YOU WANT TO EXIT JUST WRITE -1 AND NOTHING ELSE AND THE CHAT ENDS")
print("========================================================================================")
print()

log_path = start_run_logging()
logger.info("CHAT SESSION START; log_file=%s", log_path)
session = AgentSession()
try:
    while True:
        response = input("You: ")
        if response == "-1":
            logger.info("CHAT SESSION EXIT requested by user")
            break
        agent_response = run_agent(response, session)
        print(agent_response)
        print("-------------------------------------")
finally:
    logger.info("CHAT SESSION ENDED")
    stop_run_logging()