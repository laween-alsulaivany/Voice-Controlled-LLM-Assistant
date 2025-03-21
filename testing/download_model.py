from transformers import AutoModelForCausalLM, AutoTokenizer

# model_name = "mistralai/Mistral-7B-v0.1"
# model_name = "mistralai/Mistral-Nemo-Instruct-2407"
model_name = "mistralai/Mistral-7B-Instruct-v0.3"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name, trust_remote_code=True)
