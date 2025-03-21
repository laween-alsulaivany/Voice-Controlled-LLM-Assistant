from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, BitsAndBytesConfig
import torch

# Determine the device (GPU if available, otherwise CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Point to the local directory where the model was downloaded
model_name_or_path = "C:/Users/Laween/.cache/huggingface/hub/models--mistralai--Mistral-7B-Instruct-v0.3/snapshots/e0bc86c23ce5aae1db576c8cca6f06f1f73af2db"

# Configure 4-bit quantization
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    llm_int8_enable_fp32_cpu_offload=True,  # Enable FP32 offloading for CPU
    bnb_4bit_compute_dtype=torch.float16  # Use float16 for faster inference


)


# Load the tokenizer and model from the local directory
print(device)
tokenizer = AutoTokenizer.from_pretrained(
    model_name_or_path, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name_or_path,
    torch_dtype=torch.bfloat16,
    quantization_config=quantization_config,  # Use the quantization config
    device_map="auto",                        # Automatically place weights on GPU/CPU
    trust_remote_code=True
)
model = torch.compile(model)


def generate_response(prompt):
    # Ensure inputs are on the same device as the model
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    generation_config = GenerationConfig(
        max_new_tokens=64,
        min_length=5,  # Ensure at least 5 tokens are generated
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
    )
    with torch.no_grad():
        output_tokens = model.generate(
            **inputs,
            generation_config=generation_config
            # eos_token_id=tokenizer.eos_token_id  # Stop at the end-of-sentence token

        )
    return tokenizer.decode(output_tokens[0], skip_special_tokens=True)


# Test
# response = generate_response("Hello there! How are you doing today?")
response = generate_response("tell me a joke")
print("Model response:", response)
