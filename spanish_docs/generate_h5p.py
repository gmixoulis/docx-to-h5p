#!/usr/bin/env python3
"""
H5P File Generator
Creates .h5p files (ZIP archives) from JSON content and images.
H5P files contain: h5p.json (metadata) and content/ folder with content.json and optional images.
"""

import json
import zipfile
import os
import shutil
from typing import Dict, List, Optional
from pathlib import Path

class H5PGenerator:
    """Generate H5P packages from content JSON and images."""

    def __init__(self):
        self.h5p_metadata = {
            "title": "Multiple Choice Question",
            "language": "en",
            "mainLibrary": "H5P.MultiChoice",
            "embedTypes": ["iframe"],
            "license": "U",
            "preloadedDependencies": [
                {
                    "machineName": "H5P.MultiChoice",
                    "majorVersion": "1",
                    "minorVersion": "16"
                }
            ]
        }

    def create_h5p_file(
        self, 
        content_json: Dict,
        output_filename: str,
        images: Optional[List[str]] = None,
        title: Optional[str] = None
    ) -> str:
        """
        Create an H5P file from content JSON and optional images.

        Args:
            content_json: Dictionary containing the question content
            output_filename: Name for the output .h5p file (without extension)
            images: List of image file paths to include
            title: Optional title for the H5P package

        Returns:
            Path to the created .h5p file
        """

        # Update title if provided
        if title:
            self.h5p_metadata["title"] = title

        # Create temporary directory structure
        temp_dir = f"temp_{output_filename}"
        content_dir = os.path.join(temp_dir, "content")
        images_dir = os.path.join(content_dir, "images")

        # Clean up if temp directory exists
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

        # Create directories
        os.makedirs(images_dir, exist_ok=True)

        # Write h5p.json
        h5p_json_path = os.path.join(temp_dir, "h5p.json")
        with open(h5p_json_path, 'w', encoding='utf-8') as f:
            json.dump(self.h5p_metadata, f, ensure_ascii=False)

        # Write content.json
        content_json_path = os.path.join(content_dir, "content.json")
        with open(content_json_path, 'w', encoding='utf-8') as f:
            json.dump(content_json, f, indent=2, ensure_ascii=False)

        # Copy images if provided
        if images:
            for img_path in images:
                if os.path.exists(img_path):
                    img_filename = os.path.basename(img_path)
                    dest_path = os.path.join(images_dir, img_filename)
                    shutil.copy2(img_path, dest_path)
                    print(f"  Added image: {img_filename}")

        # Create H5P file (ZIP archive)
        h5p_filename = f"{output_filename}.h5p"

        with zipfile.ZipFile(h5p_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add h5p.json
            zipf.write(h5p_json_path, 'h5p.json')

            # Add content/content.json
            zipf.write(content_json_path, 'content/content.json')

            # Add images
            if images and os.path.exists(images_dir):
                for img_file in os.listdir(images_dir):
                    img_path = os.path.join(images_dir, img_file)
                    zipf.write(img_path, f'content/images/{img_file}')

        # Clean up temporary directory
        shutil.rmtree(temp_dir)

        print(f"âœ“ Created H5P file: {h5p_filename}")
        return h5p_filename

    def create_crossword_h5p(
        self,
        content_json: Dict,
        output_filename: str,
        title: Optional[str] = None
    ) -> str:
        """
        Create an H5P file for crossword content.

        Args:
            content_json: Dictionary containing the crossword content
            output_filename: Name for the output .h5p file (without extension)
            title: Optional title for the H5P package

        Returns:
            Path to the created .h5p file
        """

        # Update metadata for crossword
        self.h5p_metadata = {
            "title": title or "Crossword Puzzle",
            "language": "en",
            "mainLibrary": "H5P.Crossword",
            "embedTypes": ["iframe"],
            "license": "U",
            "preloadedDependencies": [
                {
                    "machineName": "H5P.Crossword",
                    "majorVersion": "0",
                    "minorVersion": "4"
                }
            ]
        }

        return self.create_h5p_file(content_json, output_filename, title=title)

    def batch_create_h5p_files(
        self,
        json_files: List[str],
        images_folder: Optional[str] = None
    ) -> List[str]:
        """
        Create multiple H5P files from a list of JSON files.

        Args:
            json_files: List of paths to JSON files
            images_folder: Optional folder containing images to include

        Returns:
            List of created H5P file paths
        """
        created_files = []

        for json_file in json_files:
            try:
                # Load JSON content
                with open(json_file, 'r', encoding='utf-8') as f:
                    content = json.load(f)

                # Extract filename without extension
                base_name = os.path.splitext(os.path.basename(json_file))[0]

                # Extract title from question if available
                title = "Multiple Choice Question"
                if "question" in content:
                    # Clean HTML tags from question for title
                    import re
                    question_text = re.sub(r'<[^>]+>', '', content.get("question", ""))
                    title = question_text[:50] + "..." if len(question_text) > 50 else question_text

                # Find images in the images folder if provided
                images = []
                if images_folder and os.path.exists(images_folder):
                    for img_file in os.listdir(images_folder):
                        if img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                            images.append(os.path.join(images_folder, img_file))

                # Create H5P file
                h5p_file = self.create_h5p_file(
                    content_json=content,
                    output_filename=base_name,
                    images=images if images else None,
                    title=title
                )

                created_files.append(h5p_file)

            except Exception as e:
                print(f"âœ— Error processing {json_file}: {e}")

        return created_files


def main():
    """Example usage of H5PGenerator."""
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python generate_h5p.py <json_file> [images_folder]")
        print("  python generate_h5p.py --batch <json_folder> [images_folder]")
        print()
        print("Examples:")
        print("  python generate_h5p.py question_1.json images/")
        print("  python generate_h5p.py --batch output/ images/")
        return

    generator = H5PGenerator()

    # Batch mode
    if sys.argv[1] == "--batch":
        if len(sys.argv) < 3:
            print("Error: Please provide a folder containing JSON files")
            return

        json_folder = sys.argv[2]
        images_folder = sys.argv[3] if len(sys.argv) > 3 else None

        # Find all JSON files
        json_files = []
        for file in os.listdir(json_folder):
            if file.endswith('.json'):
                json_files.append(os.path.join(json_folder, file))

        if not json_files:
            print(f"No JSON files found in {json_folder}")
            return

        print(f"Processing {len(json_files)} JSON files...")
        created_files = generator.batch_create_h5p_files(json_files, images_folder)

        print(f"\nâœ“ Successfully created {len(created_files)} H5P files:")
        for f in created_files:
            print(f"  - {f}")

    # Single file mode
    else:
        json_file = sys.argv[1]
        images_folder = sys.argv[2] if len(sys.argv) > 2 else None

        if not os.path.exists(json_file):
            print(f"Error: File {json_file} not found")
            return

        # Load JSON content
        with open(json_file, 'r', encoding='utf-8') as f:
            content = json.load(f)

        # Get base name for output
        base_name = os.path.splitext(os.path.basename(json_file))[0]

        # Find images
        images = []
        if images_folder and os.path.exists(images_folder):
            for img_file in os.listdir(images_folder):
                if img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    images.append(os.path.join(images_folder, img_file))

        # Create H5P file
        h5p_file = generator.create_h5p_file(
            content_json=content,
            output_filename=base_name,
            images=images if images else None
        )

        print(f"\nâœ“ H5P file created successfully: {h5p_file}")


if __name__ == "__main__":
    main()
