#!/usr/bin/env python3
"""
H5P Quiz Combiner with Crossword and Language Support
Combines multiple JSON files and creates separate H5P files for:
1. Multiple Choice questions (using H5P.QuestionSet)
2. Crossword puzzles (using H5P.Crossword)
Includes language files (el.json, es.json) for multilingual support
"""

import json
import zipfile
import os
import shutil
import uuid
from typing import List, Dict, Tuple
from enum import Enum

class QuestionType(Enum):
    """Enumeration for different question types."""
    MULTIPLE_CHOICE = "multiple_choice"
    CROSSWORD = "crossword"
    UNKNOWN = "unknown"


class H5PQuizCombiner:
    """Combine multiple question JSONs into separate H5P files by type."""

    def __init__(self, language_files_folder: str = None):
        """
        Initialize H5P Quiz Combiner.

        Args:
            language_files_folder: Path to folder containing el.json and es.json
        """
        self.language_files_folder = language_files_folder
        self.mc_metadata = {
            "title": "Multiple Choice Quiz",
            "language": "en",
            "mainLibrary": "H5P.QuestionSet",
            "embedTypes": ["iframe"],
            "license": "U",
            "preloadedDependencies": [
                {
                    "machineName": "H5P.QuestionSet",
                    "majorVersion": "1",
                    "minorVersion": "20"
                },
                {
                    "machineName": "H5P.MultiChoice",
                    "majorVersion": "1",
                    "minorVersion": "16"
                }
            ]
        }

        self.crossword_metadata = {
            "title": "Crossword Puzzle",
            "language": "en",
            "mainLibrary": "H5P.Crossword",
            "embedTypes": ["iframe"],
            "license": "U",
            "preloadedDependencies": [
                {
                    "machineName": "H5P.Crossword",
                    "majorVersion": "0",
                    "minorVersion": "5"
                }
            ]
        }

    def detect_question_type(self, json_data: Dict) -> QuestionType:
        """
        Detect whether a JSON file is a multiple choice question or crossword.

        Args:
            json_data: Parsed JSON data

        Returns:
            QuestionType enum value
        """
        # Check for crossword indicators
        if "words" in json_data:
            # Verify it has the crossword structure
            if isinstance(json_data["words"], list) and len(json_data["words"]) > 0:
                if "clue" in json_data["words"][0] and "answer" in json_data["words"][0]:
                    return QuestionType.CROSSWORD

        # Check for multiple choice indicators
        if "answers" in json_data and "question" in json_data:
            return QuestionType.MULTIPLE_CHOICE

        return QuestionType.UNKNOWN

    def categorize_questions(self, question_files: List[str]) -> Dict[QuestionType, List[Dict]]:
        """
        Categorize JSON files by type.

        Args:
            question_files: List of JSON file paths

        Returns:
            Dictionary mapping QuestionType to list of (filename, data) tuples
        """
        categorized = {
            QuestionType.MULTIPLE_CHOICE: [],
            QuestionType.CROSSWORD: [],
            QuestionType.UNKNOWN: []
        }

        for json_file in question_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                q_type = self.detect_question_type(data)
                categorized[q_type].append({
                    'filename': json_file,
                    'data': data
                })

                type_name = q_type.value.replace('_', ' ').title()
                print(f"  📋 {os.path.basename(json_file)}: {type_name}")

            except Exception as e:
                print(f"  ❌ Error loading {json_file}: {e}")
                categorized[QuestionType.UNKNOWN].append({
                    'filename': json_file,
                    'data': None,
                    'error': str(e)
                })

        return categorized

    def create_multiple_choice_h5p(
        self,
        questions: List[Dict],
        output_filename: str,
        title: str,
        images_folder: str = None,
        pass_percentage: int = 50
    ) -> Tuple[str, int]:
        """
        Create H5P file for multiple choice questions.

        Args:
            questions: List of question dictionaries
            output_filename: Output file name
            title: Quiz title
            images_folder: Folder containing images
            pass_percentage: Pass percentage

        Returns:
            Tuple of (filename, question_count)
        """
        # Update metadata
        self.mc_metadata["title"] = title

        all_questions = []
        all_images = set()

        for q_item in questions:
            question_data = q_item['data']

            # Extract question text for metadata
            question_text = question_data.get('question', 'Question')
            question_text = question_text.replace('<p>', '').replace('</p>', '').replace('\\n', '').strip()

            # Wrap question in H5P.MultiChoice structure
            question_obj = {
                "params": question_data,
                "library": "H5P.MultiChoice 1.16",
                "subContentId": str(uuid.uuid4()),
                "metadata": {
                    "title": question_text[:100] if len(question_text) > 100 else question_text,
                    "license": "U",
                    "contentType": "Multiple Choice"
                }
            }

            all_questions.append(question_obj)

            # Track images
            if 'media' in question_data and 'type' in question_data['media']:
                media = question_data['media']['type']
                if 'params' in media and 'file' in media['params']:
                    image_path = media['params']['file'].get('path', '')
                    if image_path:
                        all_images.add(image_path)

        # Create Question Set structure
        quiz_content = {
            "progressType": "dots",
            "passPercentage": pass_percentage,
            "questions": all_questions,
            "introPage": {
                "showIntroPage": False,
                "startButtonText": "Start Quiz",
                "introduction": ""
            },
            "texts": {
                "prevButton": "Previous",
                "nextButton": "Next",
                "finishButton": "Finish",
                "textualProgress": "Question: @current of @total questions",
                "questionLabel": "Question",
                "jumpToQuestion": "Jump to question %d",
                "readSpeakerProgress": "Question @current of @total",
                "unansweredText": "Unanswered",
                "answeredText": "Answered",
                "currentQuestionText": "Current question",
                "submitButton": "Submit",
                "navigationLabel": "Questions"
            },
            "endGame": {
                "showResultPage": True,
                "solutionButtonText": "Show solution",
                "finishButtonText": "Finish",
                "showAnimations": False,
                "skippable": False,
                "skipButtonText": "Skip video",
                "message": "Your result:",
                "retryButtonText": "Retry",
                "noResultMessage": "Finished",
                "overallFeedback": [
                    {"from": 0, "to": 100, "feedback": "You got @score points of @total possible."}
                ],
                "showSolutionButton": True,
                "showRetryButton": True,
                "scoreBarLabel": "You got @finals out of @totals points",
                "submitButtonText": "Submit"
            },
            "override": {
                "showSolutionButton": "off",
                "retryButton": "off",
                "checkButton": True
            },
            "disableBackwardsNavigation": False,
            "randomQuestions": False
        }

        return self._create_h5p_file(
            output_filename,
            self.mc_metadata,
            quiz_content,
            images_folder
        )

    def create_crossword_h5p(
        self,
        crosswords: List[Dict],
        output_filename: str,
        title: str,
        images_folder: str = None
    ) -> Tuple[str, int]:
        """
        Create H5P file for crossword puzzles.

        Note: Each crossword is a standalone activity, so we combine all words
        from all crosswords into a single large crossword.

        Args:
            crosswords: List of crossword dictionaries
            output_filename: Output file name
            title: Crossword title
            images_folder: Folder containing images

        Returns:
            Tuple of (filename, crossword_count)
        """
        # Update metadata
        self.crossword_metadata["title"] = title

        # Combine all words from all crosswords
        all_words = []
        base_crossword = crosswords[0]['data']

        for cw_item in crosswords:
            cw_data = cw_item['data']
            if 'words' in cw_data:
                all_words.extend(cw_data['words'])

        # Use the structure from the first crossword and add all words
        crossword_content = {
            "words": all_words,
            "overallFeedback": base_crossword.get("overallFeedback", [{"from": 0, "to": 100}]),
            "theme": base_crossword.get("theme", {
                "backgroundColor": "#222b46",
                "gridColor": "#031928",
                "cellBackgroundColor": "#ffffff",
                "cellColor": "#000000",
                "clueIdColor": "#606060",
                "cellBackgroundColorHighlight": "#5c9ba9",
                "cellColorHighlight": "#031928",
                "clueIdColorHighlight": "#e0e0e0"
            }),
            "behaviour": base_crossword.get("behaviour", {
                "enableInstantFeedback": False,
                "scoreWords": True,
                "applyPenalties": False,
                "enableRetry": True,
                "enableSolutionsButton": True
            }),
            "l10n": base_crossword.get("l10n", {
                "across": "Across",
                "down": "Down",
                "checkAnswer": "Check",
                "tryAgain": "Retry",
                "showSolution": "Show solution",
                "couldNotGenerateCrossword": "Could not generate a crossword with the given words.",
                "couldNotGenerateCrosswordTooFewWords": "Could not generate a crossword. You need at least two words.",
                "probematicWords": "Problematic word(s): @words",
                "extraClue": "Extra clue",
                "closeWindow": "Close window",
                "submitAnswer": "Submit"
            }),
            "a11y": base_crossword.get("a11y", {
                "crosswordGrid": "Crossword grid. Use arrow keys to navigate and keyboard to enter characters.",
                "column": "Column",
                "row": "Row",
                "across": "Across",
                "down": "Down",
                "empty": "Empty",
                "resultFor": "Result for: @clue",
                "correct": "Correct",
                "wrong": "Wrong",
                "point": "point",
                "solutionFor": "For @clue the solution is: @solution",
                "check": "Check the characters.",
                "showSolution": "Show the solution.",
                "retry": "Retry the task.",
                "yourResult": "You got @score out of @total points"
            }),
            "taskDescription": base_crossword.get("taskDescription", "")
        }

        return self._create_h5p_file(
            output_filename,
            self.crossword_metadata,
            crossword_content,
            images_folder
        )

    def _create_h5p_file(
        self,
        output_filename: str,
        metadata: Dict,
        content: Dict,
        images_folder: str = None
    ) -> Tuple[str, int]:
        """
        Create an H5P file with language support.

        Args:
            output_filename: Name for output file
            metadata: H5P metadata (h5p.json)
            content: Content data (content.json)
            images_folder: Optional images folder

        Returns:
            Tuple of (h5p_filename, item_count)
        """
        # Create temporary directory structure
        temp_dir = f"temp_{output_filename}"
        content_dir = os.path.join(temp_dir, "content")
        images_dir = os.path.join(content_dir, "images")
        language_dir = os.path.join(temp_dir, "language")

        # Clean up if exists
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(language_dir, exist_ok=True)

        # Write h5p.json
        with open(os.path.join(temp_dir, "h5p.json"), 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False)

        # Write content.json
        with open(os.path.join(content_dir, "content.json"), 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)

        # Copy language files if available
        language_files_added = []
        if self.language_files_folder and os.path.exists(self.language_files_folder):
            for lang_file in ['el.json', 'es.json']:
                src_path = os.path.join(self.language_files_folder, lang_file)
                if os.path.exists(src_path):
                    dest_path = os.path.join(language_dir, lang_file)
                    shutil.copy2(src_path, dest_path)
                    language_files_added.append(lang_file)
                    print(f"  🌐 Added language file: {lang_file}")

        # Copy images if provided
        if images_folder and os.path.exists(images_folder):
            for img_file in os.listdir(images_folder):
                if img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    src_path = os.path.join(images_folder, img_file)
                    dest_path = os.path.join(images_dir, img_file)
                    shutil.copy2(src_path, dest_path)

        # Create H5P file (ZIP archive)
        h5p_filename = f"{output_filename}.h5p"

        with zipfile.ZipFile(h5p_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add h5p.json
            zipf.write(os.path.join(temp_dir, "h5p.json"), 'h5p.json')

            # Add content/content.json
            zipf.write(os.path.join(content_dir, "content.json"), 'content/content.json')

            # Add images if they exist
            if os.path.exists(images_dir) and os.listdir(images_dir):
                for img_file in os.listdir(images_dir):
                    img_path = os.path.join(images_dir, img_file)
                    zipf.write(img_path, f'content/images/{img_file}')

            # Add language files if they exist
            if os.path.exists(language_dir) and os.listdir(language_dir):
                for lang_file in os.listdir(language_dir):
                    lang_path = os.path.join(language_dir, lang_file)
                    zipf.write(lang_path, f'language/{lang_file}')

        # Clean up temp directory
        shutil.rmtree(temp_dir)

        # Count items
        item_count = 0
        if "questions" in content:
            item_count = len(content["questions"])
        elif "words" in content:
            item_count = len(content["words"])

        return h5p_filename, item_count

    def process_all_questions(
        self,
        question_files: List[str],
        output_prefix: str = "quiz",
        mc_title: str = "Multiple Choice Quiz",
        crossword_title: str = "Crossword Puzzle",
        images_folder: str = None,
        pass_percentage: int = 50
    ) -> Dict[str, Tuple[str, int]]:
        """
        Process all questions and create separate H5P files for each type.

        Args:
            question_files: List of JSON file paths
            output_prefix: Prefix for output files
            mc_title: Title for multiple choice quiz
            crossword_title: Title for crossword
            images_folder: Optional images folder
            pass_percentage: Pass percentage for multiple choice

        Returns:
            Dictionary mapping question type to (filename, count) tuples
        """
        # Categorize questions
        print("\n📂 Categorizing questions...")
        categorized = self.categorize_questions(question_files)

        results = {}

        # Create multiple choice H5P if there are any MC questions
        if categorized[QuestionType.MULTIPLE_CHOICE]:
            print(f"\n🎯 Creating Multiple Choice quiz...")
            mc_filename, mc_count = self.create_multiple_choice_h5p(
                categorized[QuestionType.MULTIPLE_CHOICE],
                f"{output_prefix}_multiple_choice",
                mc_title,
                images_folder,
                pass_percentage
            )
            results['multiple_choice'] = (mc_filename, mc_count)
            print(f"  ✅ Created: {mc_filename} with {mc_count} questions")

        # Create crossword H5P if there are any crosswords
        if categorized[QuestionType.CROSSWORD]:
            print(f"\n🧩 Creating Crossword puzzle...")
            cw_filename, cw_count = self.create_crossword_h5p(
                categorized[QuestionType.CROSSWORD],
                f"{output_prefix}_crossword",
                crossword_title,
                images_folder
            )
            results['crossword'] = (cw_filename, cw_count)
            print(f"  ✅ Created: {cw_filename} with {cw_count} words")

        # Report unknown files
        if categorized[QuestionType.UNKNOWN]:
            print(f"\n⚠️  Warning: {len(categorized[QuestionType.UNKNOWN])} files could not be categorized:")
            for item in categorized[QuestionType.UNKNOWN]:
                print(f"  • {os.path.basename(item['filename'])}")

        return results


def main():
    """Main function with command-line interface."""
    import sys
    import glob

    if len(sys.argv) < 2:
        print("H5P Quiz Combiner with Crossword and Language Support")
        print("=" * 60)
        print("\nUsage:")
        print("  python combine_to_h5p.py <json_folder> [images_folder] [lang_folder] [output_prefix] [mc_title] [crossword_title]")
        print()
        print("Arguments:")
        print("  json_folder     : Folder containing JSON files (required)")
        print("  images_folder   : Folder containing images (optional)")
        print("  lang_folder     : Folder containing el.json and es.json (optional)")
        print("  output_prefix   : Prefix for output files (default: 'quiz')")
        print("  mc_title        : Title for multiple choice quiz (default: 'Multiple Choice Quiz')")
        print("  crossword_title : Title for crossword (default: 'Crossword Puzzle')")
        print()
        print("Example:")
        print("  python combine_to_h5p.py questions/ images/ languages/ my_quiz \"My Quiz\" \"My Crossword\"")
        print()
        print("Language folder structure:")
        print("  languages/")
        print("    ├── el.json  (Greek translations)")
        print("    └── es.json  (Spanish translations)")
        print()
        print("This will:")
        print("  • Scan all JSON files in questions/")
        print("  • Detect whether each is a multiple choice question or crossword")
        print("  • Include language files for multilingual support")
        print("  • Create separate H5P files:")
        print("    - my_quiz_multiple_choice.h5p (if there are MC questions)")
        print("    - my_quiz_crossword.h5p (if there are crosswords)")
        return

    # Parse arguments
    json_folder = sys.argv[1]
    images_folder = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '' else None
    lang_folder = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != '' else None
    output_prefix = sys.argv[4] if len(sys.argv) > 4 else "quiz"
    mc_title = sys.argv[5] if len(sys.argv) > 5 else "Multiple Choice Quiz"
    crossword_title = sys.argv[6] if len(sys.argv) > 6 else "Crossword Puzzle"

    # Find all JSON files
    if os.path.isdir(json_folder):
        json_pattern = os.path.join(json_folder, "*.json")
        json_files = glob.glob(json_pattern)
    else:
        # Single file or pattern provided
        json_files = glob.glob(json_folder)

    if not json_files:
        print(f"❌ No JSON files found in {json_folder}")
        return

    print("=" * 60)
    print("📚 H5P Quiz Combiner with Language Support")
    print("=" * 60)
    print(f"\n📁 Found {len(json_files)} JSON files")
    print(f"🎯 Output prefix: {output_prefix}")

    if lang_folder:
        print(f"🌐 Language folder: {lang_folder}")

    # Create combiner with language files folder
    combiner = H5PQuizCombiner(language_files_folder=lang_folder)

    # Process all questions
    results = combiner.process_all_questions(
        question_files=json_files,
        output_prefix=output_prefix,
        mc_title=mc_title,
        crossword_title=crossword_title,
        images_folder=images_folder
    )

    # Summary
    print("\n" + "=" * 60)
    print("✅ Processing Complete!")
    print("=" * 60)

    if results:
        print(f"\n📦 Created {len(results)} H5P file(s):\n")

        if 'multiple_choice' in results:
            filename, count = results['multiple_choice']
            size = os.path.getsize(filename)
            print(f"  🎯 Multiple Choice Quiz:")
            print(f"     • File: {filename}")
            print(f"     • Questions: {count}")
            print(f"     • Size: {size:,} bytes")
            print()

        if 'crossword' in results:
            filename, count = results['crossword']
            size = os.path.getsize(filename)
            print(f"  🧩 Crossword Puzzle:")
            print(f"     • File: {filename}")
            print(f"     • Words: {count}")
            print(f"     • Size: {size:,} bytes")
            print()

        print("🎓 Ready to upload to your LMS (Moodle, WordPress, Canvas, etc.)!")
        if lang_folder:
            print("🌐 Language files included for multilingual support!")
    else:
        print("\n⚠️  No H5P files were created. Please check your JSON files.")


if __name__ == "__main__":
    main()
