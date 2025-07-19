import os
import textwrap
import ollama
from transformers import MarianMTModel, MarianTokenizer

from srt_processing import parse_srt, merge_srt_segments, get_context_segments, seconds_to_srt_time, get_broad_context

def marian_translate(texts, src_lang="pl", tgt_lang="en", batch_size=8):
    import torch
    model_name = f"Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}"
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    results = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch = tokenizer(batch_texts, return_tensors="pt", padding=True, truncation=True).to(device)
        gen = model.generate(**batch)
        results.extend([tokenizer.decode(t, skip_special_tokens=True) for t in gen])
    return results

def translate_srt(
    input_srt: str,
    output_srt: str | None = None,
    window: float = 7.0,
    source_language: str = "polish",
    target_language: str = "english",
    method: str = "llm"  # or "marian"
) -> str:
    """
    Translate SRT subtitles from source_language to target_language using LLM or MarianMT with broad and local context.
    """

    # If output_srt is None, use input file name with 'translated' prefix
    if output_srt is None:
        base = os.path.basename(input_srt)
        dir_ = os.path.dirname(input_srt)
        output_srt = os.path.join(dir_, f"{base}_translated")

    segments = merge_srt_segments(parse_srt(input_srt))
    translated_segments = []

    if method == "marian":
        # Use MarianMT for direct translation (no context)
        src_lang = "pl" if source_language.lower().startswith("pol") else "en"
        tgt_lang = "en" if target_language.lower().startswith("eng") else "pl"
        texts = [seg.text for seg in segments]
        translations = marian_translate(texts, src_lang, tgt_lang)
        for seg, translated_line in zip(segments, translations):
            translated_segments.append((seg.idx, seg.start, seg.end, translated_line))
    else:
        # Use LLM with context
        broad_context = get_broad_context(segments)

        system_prompt = textwrap.dedent(f"""
            You are a professional subtitle translator. 
            Translate the provided subtitle line from {source_language} to natural, idiomatic {target_language}, preserving the meaning and style.
            Use the provided movie summary and local context to resolve ambiguities.
            Return only the translated line, with no explanations or extra output.
        """)
        summary_prompt = f"Movie summary: {broad_context}"

        for idx, seg in enumerate(segments):
            before, target, after = get_context_segments(segments, idx, window)
            before_text = ' '.join([s.text for s in before])
            after_text = ' '.join([s.text for s in after])

            prompt = textwrap.dedent(f"""
                {system_prompt}
                {summary_prompt}

                Context before: {before_text}
                Line to translate: {target.text}
                Context after: {after_text}
            """)

            translated_line = ollama.call_api(prompt)

            print(f"[TRANSLATED] #{target.idx} {seconds_to_srt_time(target.start)} --> {seconds_to_srt_time(target.end)}")
            print(f"  Original: {target.text}")
            print(f"  Translated:  {translated_line}\n")

            translated_segments.append((target.idx, target.start, target.end, translated_line))

    # Write translated SRT
    with open(output_srt, 'w', encoding='utf-8') as f:
        for idx, start, end, text in translated_segments:
            f.write(f"{idx}\n{seconds_to_srt_time(start)} --> {seconds_to_srt_time(end)}\n{text}\n\n")

    return output_srt