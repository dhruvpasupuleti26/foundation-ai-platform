# Here we create an instance of IModelServer defined in llm_platform/interfaces/model_server.py

from __future__ import annotations # Py evaluates type hints during runtime (Solve forward/circular ref)
import httpx
from llm_platform.interfaces.model_server import IModelServer # Rules for model server instances to follow
from llm_platform.schemas.gateway import ChatCompletionRequest # Pydantic structure for the payload

class VllmModelServer(IModelServer):
	"""Concrete inplementation of model server followig guidelines laid out by abstract base class IModelServer that communicates with vLLM"""

	def __init__(self, base_url: str = "http://localhost:8001"):
		
		self.base_url = base_url # default points to port 8001


	async def generate(self, deployment:object, request: ChatCompletionRequest) -> str:
		"""Sends the request payload over the interna loopback network to live vllm container"""
		
		url = f"{self.base_url}/v1/chat/completions" # following openapi formatting
		
		# Extract info from Pydantic request payload
		payload = {
			"model": request.model,
			"message": [{"role": m.role, "content": m.content} for m in request.messages],
			"temperature": request.temperature or 0.7
		}

		# Open up a network pipe, convert dict payload to json and sent POST request to url
		async with httpx.AsyncClient as client:
			response = await client.post(url, json=payload, timeout=60.0)

		if response.status_code == 200:
			json_data = response.json()
			return json_data["choices"][0]["message"]["content"] # Extract LLM's Natural Lang. response from the comlpex json it return
		else:
			raise RuntimeError(f"vLLM server error: {response.text}")

