from .base import Backend
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class ROCMBackend(Backend):
    def __init__(self):
        self.model = None
        self.tokenizer = None

    def load_model(self, model_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16)
        self.model.to('cuda')  # ROCm uses 'cuda' device string for AMD GPUs

    def infer(self, input_data):
        inputs = self.tokenizer(input_data, return_tensors="pt").to('cuda')
        with torch.no_grad():
            outputs = self.model.generate(**inputs)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def is_available(self) -> bool:
        try:
            return torch.version.hip is not None and torch.cuda.is_available()
        except AttributeError:
            return False
