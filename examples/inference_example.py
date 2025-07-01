from llama_gpu import LlamaGPU

if __name__ == "__main__":
    model_path = "./models/<model_name>"  # Replace with your model path
    input_text = "Hello, world!"
    llama = LlamaGPU(model_path=model_path, prefer_gpu=True)
    result = llama.infer(input_text)
    print("Result:", result)
