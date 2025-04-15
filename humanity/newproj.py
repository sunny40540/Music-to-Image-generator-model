import os
import re
import traceback
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
import wikipediaapi
from diffusers import StableDiffusionPipeline
import torch

def extract_metadata(filepath):
    try:
        if filepath.endswith(".mp3"):
            audio = MP3(filepath, ID3=EasyID3)
        elif filepath.endswith(".flac"):
            audio = FLAC(filepath)
        else:
            return None, "❌ Unsupported file format."

        metadata = {
            "title": audio.get("title", ["Unknown"])[0],
            "artist": audio.get("artist", ["Unknown"])[0],
            "album": audio.get("album", ["Unknown"])[0],
            "year": audio.get("date", ["Unknown"])[0],
            "genre": audio.get("genre", ["Unknown"])[0],
        }
        return metadata, None
    except Exception as e:
        return None, f"⚠ Error extracting metadata: {str(e)}"

def get_wikipedia_info(year):
    try:
        wiki = wikipediaapi.Wikipedia(language='en')
        page = wiki.page(str(year))
        if page.exists():
            return page.summary[:500]
        return f"No Wikipedia summary found for year {year}."
    except Exception as e:
        return f"⚠ Error fetching Wikipedia info: {str(e)}"

def generate_image(metadata, era_info):
    try:
        prompt = (
            f" traditional dress of that era and having concert  {metadata['year']}, "
            f"genre: {metadata['genre']}, artist: {metadata['artist']}. "
            f"{era_info}"
        )

        print("\n🧠 Generating image from prompt...\n", prompt)

        model_id = "CompVis/stable-diffusion-v1-4"
        pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32)
        pipe.to("cpu")

        image = pipe(prompt).images[0]
        title_safe = re.sub(r'[\\/*?:"<>|]', "_", metadata['title'] or "output")
        image_path = f"image_{title_safe}.png"
        image.save(image_path)
        return image_path
    except Exception as e:
        print("❌ Error during image generation:")
        traceback.print_exc()
        return None

def main():
    try:
        filepath = input("🎵 Enter path to MP3 or FLAC file: ").strip()

        if not os.path.isfile(filepath):
            print("❌ File not found.")
            return

        print("\n🔍 Extracting metadata...")
        metadata, error = extract_metadata(filepath)
        if error:
            print(error)
            return

        print("✅ Metadata found:", metadata)

        if metadata["year"] == "Unknown":
            print("⚠ Year not found in metadata. Cannot generate image.")
            return

        print("\n🌍 Fetching historical info...")
        era_info = get_wikipedia_info(metadata["year"])
        print("📝 Wikipedia info (shortened):", era_info[:200], "...")

        print("\n🎨 Creating image...")
        image_path = generate_image(metadata, era_info)

        if image_path:
            print("✅ Image saved as:", image_path)
        else:
            print("⚠ Image generation failed.")

    except Exception as e:
        print("❌ An unexpected error occurred:")
        traceback.print_exc()

if __name__ == "__main__":
    main()
