# audio_to_image.py

# Install dependencies using pip if not already installed:
# pip install mutagen wikipedia-api diffusers torch transformers accelerate

import os
import mutagen
import requests
import wikipediaapi
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
from diffusers import StableDiffusionPipeline
import torch

def extract_metadata(filename):
    try:
        if filename.endswith(".mp3"):
            audio = MP3(filename, ID3=EasyID3)
        elif filename.endswith(".flac"):
            audio = FLAC(filename)
        else:
            return "❌ Unsupported file format."

        metadata = {
            "title": audio.get("title", ["Unknown"])[0],
            "artist": audio.get("artist", ["Unknown"])[0],
            "album": audio.get("album", ["Unknown"])[0],
            "year": audio.get("date", ["Unknown"])[0],
            "genre": audio.get("genre", ["Unknown"])[0],
        }
        return metadata
    except Exception as e:
        return f"⚠ Error extracting metadata: {str(e)}"

def get_wikipedia_info(year):
    wiki_wiki = wikipediaapi.Wikipedia(
        language='en',
        user_agent="MyColabScript/1.0 (contact: him62065sr@gmail.com)"
    )

    page = wiki_wiki.page(str(year))

    if page.exists():
        return page.summary[:500]
    else:
        return f"No historical information found for the year {year}."

def generate_image(era_info, year):
    model_id = "CompVis/stable-diffusion-v1-4"
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    pipe.to("cpu")

    prompt = f"Visual representation of actress dancing {year}. {era_info}"
    image = pipe(prompt).images[0]

    image_path = "generated_image.png"
    image.save(image_path)
    return image_path

def main():
    print("📂 Enter the path to an audio file (MP3 or FLAC):")
    filepath = input("> ").strip()

    if not os.path.exists(filepath):
        print("❌ File not found.")
        return

    print("\n🎵 Extracting Metadata...")
    metadata = extract_metadata(filepath)
    print(metadata)

    year = metadata.get("year", "Unknown")
    if year == "Unknown":
        print("⚠ No year found in metadata. Skipping Wikipedia info and image generation.")
        return

    print("\n📜 Fetching Historical Info from Wikipedia...")
    era_info = get_wikipedia_info(year)
    print(era_info)

    print("\n🖼 Generating Image...")
    image_path = generate_image(era_info, year)
    print("✅ Image saved as:", image_path)

if __name__ == "__main__":
    main()
