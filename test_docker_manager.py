from llm_platform.serving.docker_manager import DockerManager # import class def from llm_platform/serving/docker_manager.py

print("Starting test.")

manager = DockerManager(config_path="configs/vllm_config.yaml")

print("Automated container launch will be done shortly.")

manager.start_vllm_server()
