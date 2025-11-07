#!/usr/bin/env python3
"""
H5P Quiz Combiner with Auto-Detection, True/False, Crossword, Multiple Choice, and Library Support
Automatically detects folders containing 'Activity' or 'Module' in their names and combines JSONs by type.
"""

import json
import zipfile
import os
import shutil
import uuid
from typing import List, Dict, Tuple, Optional
from enum import Enum
import re

class QuestionType(Enum):
    """Enumeration for different question types."""
    MULTIPLE_CHOICE = "multiple_choice"
    CROSSWORD = "crossword"
    TRUE_FALSE = "true_false"
    UNKNOWN = "unknown"


class H5PQuizCombiner:
    """Combine multiple question JSONs into separate H5P files by type."""

    def __init__(self, language_files_folder: str = None, library_json_path: str = None):
        """
        Initialize H5P Quiz Combiner.

        Args:
            language_files_folder: Path to folder containing el.json and es.json
            library_json_path: Path to library.json file (optional)
        """
        self.language_files_folder = language_files_folder
        self.library_json_path = library_json_path

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

        self.truefalse_metadata = {
            "title": "True/False Questions",
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
                    "machineName": "H5P.TrueFalse",
                    "majorVersion": "1",
                    "minorVersion": "8"
                }
            ]
        }

    def detect_question_type(self, json_data: Dict) -> QuestionType:
        """
        Detect whether a JSON file is a multiple choice, true/false, or crossword question.

        Args:
            json_data: Parsed JSON data

        Returns:
            QuestionType enum value
        """
        # Check for crossword indicators
        if "words" in json_data:
            if isinstance(json_data["words"], list) and len(json_data["words"]) > 0:
                if "clue" in json_data["words"][0] and "answer" in json_data["words"][0]:
                    return QuestionType.CROSSWORD

        # Check for true/false indicators
        if "question" in json_data and "correct" in json_data:
            # True/False has a "correct" field at the root level (boolean)
            if isinstance(json_data["correct"], bool) or json_data["correct"] in ["true", "false"]:
                return QuestionType.TRUE_FALSE

        # Check if it's a True/False with different structure
        if "answers" in json_data and isinstance(json_data["answers"], list):
            # Count how many answers have "correct" field
            answers = json_data["answers"]
            if len(answers) == 2:  # True/False typically has 2 options
                # Check if answers look like True/False pattern
                answer_texts = [str(a.get("text", "")).lower() for a in answers]
                if any(keyword in text for text in answer_texts for keyword in ["true", "false", "yes", "no"]):
                    # Could be True/False, but let's check further
                    pass
            
            # It's likely multiple choice if it has more than 2 answers or doesn't match T/F pattern
            if "question" in json_data:
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
            QuestionType.TRUE_FALSE: [],
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

    def create_truefalse_h5p(
        self,
        questions: List[Dict],
        output_filename: str,
        title: str,
        images_folder: str = None,
        pass_percentage: int = 50
    ) -> Tuple[str, int]:
        """
        Create H5P file for true/false questions.

        Args:
            questions: List of true/false question dictionaries
            output_filename: Output file name
            title: Quiz title
            images_folder: Folder containing images
            pass_percentage: Pass percentage

        Returns:
            Tuple of (filename, question_count)
        """
        # Update metadata
        self.truefalse_metadata["title"] = title

        all_questions = []
        all_images = set()

        for q_item in questions:
            question_data = q_item['data']

            # Extract question text for metadata
            question_text = question_data.get('question', 'Question')
            question_text = question_text.replace('<p>', '').replace('</p>', '').replace('\\n', '').strip()

            # Wrap question in H5P.TrueFalse structure
            question_obj = {
                "params": question_data,
                "library": "H5P.TrueFalse 1.8",
                "subContentId": str(uuid.uuid4()),
                "metadata": {
                    "title": question_text[:100] if len(question_text) > 100 else question_text,
                    "license": "U",
                    "contentType": "True/False Question"
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

        # Create Question Set structure (same as multiple choice)
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
            self.truefalse_metadata,
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
        Create an H5P file with language and library support.

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

        # Copy library.json if provided
        if self.library_json_path and os.path.exists(self.library_json_path):
            dest_path = os.path.join(temp_dir, "library.json")
            shutil.copy2(self.library_json_path, dest_path)
            print(f"  📚 Added library.json")

        # Copy language files if available
        language_files_added = []
        if self.language_files_folder and os.path.exists(self.language_files_folder):
            for lang_file in ['el.json', 'es.json']:
                src_path = os.path.join(self.language_files_folder, lang_file)
                if os.path.exists(src_path):
                    dest_path = os.path.join(language_dir, lang_file)
                    shutil.copy2(src_path, dest_path)
                    language_files_added.append(lang_file)
                    print(f"  🌍 Added language file: {lang_file}")

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

            # Add library.json if it exists
            library_path = os.path.join(temp_dir, "library.json")
            if os.path.exists(library_path):
                zipf.write(library_path, 'library.json')

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

    def process_folder_questions(
        self,
        folder_path: str,
        folder_name: str,
        pass_percentage: int = 50
    ) -> Dict[str, Tuple[str, int]]:
        """
        Process all questions in a specific folder and create H5P files by type.

        Args:
            folder_path: Path to the folder containing JSON files
            folder_name: Name of the folder (used for output naming)
            pass_percentage: Pass percentage for quizzes

        Returns:
            Dictionary mapping question type to (filename, count) tuples
        """
        # Find all JSON files in this folder
        json_files = []
        images_folder = None
        
        for root, dirs, files in os.walk(folder_path):
            # Check for images folder
            if 'images' in dirs:
                images_folder = os.path.join(root, 'images')
            
            # Collect JSON files (exclude language files and library.json)
            for file in files:
                if file.endswith('.json') and file not in ['el.json', 'es.json', 'library.json']:
                    json_files.append(os.path.join(root, file))

        if not json_files:
            print(f"  ⚠️  No JSON files found in {folder_name}")
            return {}

        print(f"\n📂 Processing folder: {folder_name}")
        print(f"  📄 Found {len(json_files)} JSON files")
        if images_folder:
            print(f"  🖼️  Found images folder")

        # Categorize questions
        print(f"\n🔍 Categorizing questions in {folder_name}...")
        categorized = self.categorize_questions(json_files)

        results = {}
        output_prefix = folder_name.replace(' ', '_').replace('-', '_')

        # Create multiple choice H5P if there are any MC questions
        if categorized[QuestionType.MULTIPLE_CHOICE]:
            print(f"\n🎯 Creating Multiple Choice quiz for {folder_name}...")
            mc_filename, mc_count = self.create_multiple_choice_h5p(
                categorized[QuestionType.MULTIPLE_CHOICE],
                f"{output_prefix}_multiple_choice",
                f"{folder_name} - Multiple Choice Quiz",
                images_folder,
                pass_percentage
            )
            results['multiple_choice'] = (mc_filename, mc_count)
            print(f"  ✅ Created: {mc_filename} with {mc_count} questions")

        # Create true/false H5P if there are any T/F questions
        if categorized[QuestionType.TRUE_FALSE]:
            print(f"\n✓✗ Creating True/False quiz for {folder_name}...")
            tf_filename, tf_count = self.create_truefalse_h5p(
                categorized[QuestionType.TRUE_FALSE],
                f"{output_prefix}_truefalse",
                f"{folder_name} - True/False Quiz",
                images_folder,
                pass_percentage
            )
            results['true_false'] = (tf_filename, tf_count)
            print(f"  ✅ Created: {tf_filename} with {tf_count} questions")

        # Create crossword H5P if there are any crosswords
        if categorized[QuestionType.CROSSWORD]:
            print(f"\n🧩 Creating Crossword puzzle for {folder_name}...")
            cw_filename, cw_count = self.create_crossword_h5p(
                categorized[QuestionType.CROSSWORD],
                f"{output_prefix}_crossword",
                f"{folder_name} - Crossword Puzzle",
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


def find_activity_module_folders(base_path: str = ".") -> List[Tuple[str, str]]:
    """
    Find all folders containing 'Activity' or 'Module' in their names.

    Args:
        base_path: Base path to search from

    Returns:
        List of tuples (folder_path, folder_name)
    """
    activity_folders = []
    
    # Patterns to match (case-insensitive)
    patterns = [
        re.compile(r'.*activity.*', re.IGNORECASE),
        re.compile(r'.*module.*', re.IGNORECASE)
    ]
    
    # Search for matching folders
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        
        # Check if it's a directory
        if os.path.isdir(item_path):
            # Check if folder name matches any pattern
            for pattern in patterns:
                if pattern.match(item):
                    activity_folders.append((item_path, item))
                    break
    
    return sorted(activity_folders)


def main():
    """Main function with auto-detection of Activity/Module folders."""
    print("=" * 70)
    print("📚 H5P Quiz Auto-Combiner")
    print("=" * 70)
    print("\nAuto-detecting Activity/Module folders...\n")

    # Find all Activity/Module folders in current directory
    activity_folders = find_activity_module_folders(".")
    
    if not activity_folders:
        print("❌ No folders containing 'Activity' or 'Module' found in current directory")
        print("\nPlease ensure your folder structure is:")
        print("  ./")
        print("  ├── Activities_Module_1/")
        print("  │   ├── question1.json")
        print("  │   ├── question2.json")
        print("  │   └── images/")
        print("  ├── Activities_Module_2/")
        print("  │   └── ...")
        print("  └── ...")
        return

    print(f"✅ Found {len(activity_folders)} Activity/Module folder(s):\n")
    for folder_path, folder_name in activity_folders:
        print(f"  📁 {folder_name}")
    print()

    # Look for language files and library.json in current directory
    lang_folder = None
    library_json = None
    
    if os.path.exists("./el.json") or os.path.exists("./es.json"):
        lang_folder = "."
        print("🌍 Found language files in current directory")
    
    if os.path.exists("./library.json"):
        library_json = "./library.json"
        print("📚 Found library.json in current directory")
    
    print("\n" + "=" * 70)

    # Create combiner
    combiner = H5PQuizCombiner(
        language_files_folder=lang_folder,
        library_json_path=library_json
    )

    # Process each folder
    all_results = {}
    for folder_path, folder_name in activity_folders:
        results = combiner.process_folder_questions(
            folder_path=folder_path,
            folder_name=folder_name,
            pass_percentage=50
        )
        
        if results:
            all_results[folder_name] = results

    # Final summary
    print("\n" + "=" * 70)
    print("✅ Processing Complete!")
    print("=" * 70)

    if all_results:
        print(f"\n📦 Created H5P files for {len(all_results)} folder(s):\n")

        total_files = 0
        for folder_name, results in all_results.items():
            print(f"📁 {folder_name}:")
            
            if 'multiple_choice' in results:
                filename, count = results['multiple_choice']
                size = os.path.getsize(filename)
                print(f"  🎯 Multiple Choice: {filename}")
                print(f"     • Questions: {count}")
                print(f"     • Size: {size:,} bytes")
                total_files += 1
            
            if 'true_false' in results:
                filename, count = results['true_false']
                size = os.path.getsize(filename)
                print(f"  ✓✗ True/False: {filename}")
                print(f"     • Questions: {count}")
                print(f"     • Size: {size:,} bytes")
                total_files += 1
            
            if 'crossword' in results:
                filename, count = results['crossword']
                size = os.path.getsize(filename)
                print(f"  🧩 Crossword: {filename}")
                print(f"     • Words: {count}")
                print(f"     • Size: {size:,} bytes")
                total_files += 1
            
            print()

        print(f"🎉 Total H5P files created: {total_files}")
        print("\n🎓 Ready to upload to your LMS (Moodle, WordPress, Canvas, etc.)!")
        
        features = []
        if lang_folder:
            features.append("🌍 Multilingual support (Greek, Spanish)")
        if library_json:
            features.append("📚 Library metadata included")
        
        if features:
            print("\nIncluded features:")
            for feature in features:
                print(f"  {feature}")
    else:
        print("\n⚠️  No H5P files were created. Please check your JSON files.")


if __name__ == "__main__":
    main()
