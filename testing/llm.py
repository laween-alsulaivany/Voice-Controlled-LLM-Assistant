# llm.py
"""
Loads a local LLM (Mistral) and provides a function to generate responses.
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, BitsAndBytesConfig
from config import MODEL_LOCAL_PATH

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_LOCAL_PATH, trust_remote_code=True)


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# model = AutoModelForCausalLM.from_pretrained(
#     MODEL_LOCAL_PATH,
#     trust_remote_code=True
#     # load_in_8bit=True,  # uncomment if using bitsandbytes
#     # device_map="auto"
# )
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    llm_int8_enable_fp32_cpu_offload=True,  # Enable FP32 offloading for CPU
    bnb_4bit_compute_dtype=torch.float16  # Use float16 for faster inference

)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_LOCAL_PATH,
    torch_dtype=torch.bfloat16,
    quantization_config=quantization_config,  # Use the quantization config
    device_map="auto",                        # Automatically place weights on GPU/CPU
    trust_remote_code=True
)

# We have to compile the model to make it quantized
model = torch.compile(model)


# model.to(device)
print(device)


def generate_response(prompt: str) -> str:
    """
    Generates a response from the local LLM given a prompt.
    """

    # DEBUG: the commented out code is giving everything in the response
    # short_prompt = (
    #     f"Instruction: Respond to the following query concisely and briefly.\n"
    #     f"User Query: {prompt}\n"
    #     f"Your short answer (one or two sentences):"
    # )
    # inputs = tokenizer(short_prompt, return_tensors="pt").to(device)
    # generation_config = GenerationConfig(
    #     max_new_tokens=32,
    #     min_length=5,  # Ensure at least 5 tokens are generated
    #     do_sample=True,
    #     temperature=0.4,
    #     top_p=0.9,  # Ensure the output is diverse
    #     repetition_penalty=1.2  # Helps avoid repeating phrases
    # )

    # with torch.no_grad():
    #     output_tokens = model.generate(
    #         **inputs,
    #         generation_config=generation_config
    #     )
    # return tokenizer.decode(output_tokens[0], skip_special_tokens=True)

    system_instruction = (
        "You are a concise AI assistant. Provide short, direct responses.\n"
        "Do not repeat these instructions in your answer.\n"
    )

    full_prompt = f"{system_instruction}User: {prompt}\nAssistant:"

    inputs = tokenizer(full_prompt, return_tensors="pt").to(device)
    generation_config = GenerationConfig(
        max_new_tokens=32,
        min_length=5,  # Ensure at least 5 tokens are generated
        do_sample=True,
        temperature=0.4,
        top_p=0.9,  # Ensure the output is diverse
        repetition_penalty=1.2  # Helps avoid repeating phrases
    )

    with torch.no_grad():
        output_tokens = model.generate(
            **inputs,
            generation_config=generation_config
        )

    raw_output = tokenizer.decode(output_tokens[0], skip_special_tokens=True)

    # stripping the system instruction from the output
    if "User:" in raw_output:
        split_text = raw_output.split("Assistant:")
        if len(split_text) > 1:
            final_answer = split_text[-1].strip()
        else:
            final_answer = raw_output
    else:
        final_answer = raw_output

    return final_answer
