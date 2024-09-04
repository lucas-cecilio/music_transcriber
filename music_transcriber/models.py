from InferenceModel import InferenceModel

MODEL = "ismir2021" #@param["ismir2021", "mt3"]

# Get the checkpoint
checkpoint_path = f'../checkpoints/{MODEL}/'

# Load the model
inference_model = InferenceModel(checkpoint_path, MODEL)