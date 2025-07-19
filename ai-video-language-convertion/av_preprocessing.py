import json
import importlib
import hashlib

def preprocess_w_pipeline(input_path, pipeline, skip_if_exists=None, kwargs=None):

    stage_result_path = input_path
    prev_cksum = ""
    for i, (preprocessor, params) in enumerate(pipeline):
        processor_name = getattr(preprocessor, '__name__', str(preprocessor))

        # Count the checksume of the stage and add it to the params
        hash_dict = {
            'processor': processor_name,
            'params': params,
            'prev_cksum': prev_cksum
        }
        hash_str = json.dumps(hash_dict, sort_keys=True)
        cksum = hashlib.sha256(hash_str.encode('utf-8')).hexdigest()[:16]

        # Optionally, print or log the checksum for this stage
        print(f"[Pipeline] Stage {i}: {processor_name}, checksum: {cksum}")

        if '.' in processor_name:
            module_name, func_name = processor_name.split('.')
        else:
            module_name, func_name = processor_name, processor_name
        module = importlib.import_module(f"preprocessors.{module_name}")
        func = getattr(module, func_name)
        stage_result_path = func(stage_result_path, skip_if_exists, cksum, **params)

        prev_cksum = cksum
    return stage_result_path