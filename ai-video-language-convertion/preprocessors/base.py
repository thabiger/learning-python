import os
import re

def audio_preprocessor(func):
    def wrapper(input_path, skip_if_exists=False, checksum=None, **kwargs):

        base, ext = os.path.splitext(input_path)
        # Remove trailing _<16hex> if present (checksum pattern)
        base = re.sub(r'_[0-9a-f]{16}$', '', base)
        
        if checksum:
            output_path = f"{base}_{func.__name__}_{checksum}{ext}"
        else:
            output_path = f"{base}_{func.__name__}{ext}"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if output_format:=kwargs.pop('output_format', None):
            output_path = os.path.splitext(output_path)[0] + f".{output_format}"

        if os.path.exists(output_path) and skip_if_exists:
            print(f"[Preprocessor] Output file '{output_path}' already exists. Skipping {func.__name__}.")
            return output_path

        # Print/log which preprocessor is running and with what arguments
        print(f"[Preprocessor] Running {func.__name__}(")
        print(f"    input_path='{input_path}',")
        print(f"    output_path='{output_path}',")
        if kwargs:
            print(f"    kwargs={kwargs}")
        print(")")

        return func(input_path, output_path, output_format, **kwargs)
    wrapper._is_audio_preprocessor = True
    return wrapper

