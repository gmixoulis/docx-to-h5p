#!/usr/bin/env python3
"""
🎓 H5P Content Pipeline Orchestrator
Complete automation for DOCX → JSON → H5P workflow with optional translations
Manages: Batch DOCX Processing, JSON Combining, H5P Generation, and Translations
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Optional, List
import json

class H5PPipeline:
    """Orchestrate the entire H5P content generation pipeline."""

    def __init__(self):
        self.project_root = Path(".")
        self.english_docs = self.project_root / "english_docs"
        self.greek_docs = self.project_root / "greek_docs"
        self.translations_enabled = False
        self.verbose = False

    def setup_environment(self) -> bool:
        """Check and validate the project environment."""
        print("\n" + "=" * 70)
        print("🔍 Checking Environment Setup...")
        print("=" * 70)

        required_scripts = [
            "batch_h5p_converter_final.py",
            "combine_h5p_auto.py"
        ]

        missing = []
        for script in required_scripts:
            script_path = self.project_root / script
            if script_path.exists():
                print(f"  ✅ Found: {script}")
            else:
                print(f"  ❌ Missing: {script}")
                missing.append(script)

        if missing:
            print(f"\n❌ ERROR: Missing required scripts: {', '.join(missing)}")
            print("Please ensure all scripts are in the project root directory.")
            return False

        # Check for optional translation script
        if (self.project_root / "translations.py").exists():
            print(f"  ✅ Found: translations.py (optional)")
            self.translations_enabled = True
        else:
            print(f"  ℹ️  translations.py not found (translations disabled)")

        print("\n✅ Environment validation complete!")
        return True

    def stage_1_convert_docx_to_json(self) -> bool:
        """
        Stage 1: Convert DOCX files to JSON question files.
        Processes english_docs folder.
        """
        print("\n" + "=" * 70)
        print("📄 Stage 1: Converting DOCX to JSON")
        print("=" * 70)

        if not self.english_docs.exists():
            print(f"⚠️  Folder not found: {self.english_docs}")
            print("Creating folder structure...")
            self.english_docs.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created: {self.english_docs}")
            print("\n⚠️  Please add your DOCX files to the 'english_docs' folder and run again.")
            return False

        # Find DOCX files
        docx_files = list(self.english_docs.glob("*.docx"))
        if not docx_files:
            print(f"❌ No DOCX files found in: {self.english_docs}")
            return False

        print(f"\n📚 Found {len(docx_files)} DOCX file(s):")
        for docx in docx_files:
            print(f"  • {docx.name}")

        print("\n🔄 Running batch converter...")
        try:
            result = subprocess.run(
                [sys.executable, "batch_h5p_converter_final.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if self.verbose or result.returncode != 0:
                print(result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)

            if result.returncode == 0:
                print("\n✅ Stage 1 Complete: JSON files generated!")
                return True
            else:
                print(f"\n❌ Stage 1 Failed with return code: {result.returncode}")
                return False

        except Exception as e:
            print(f"❌ Error running batch converter: {e}")
            return False

    def stage_2_combine_json_to_h5p(self) -> bool:
        """
        Stage 2: Combine JSON files into H5P packages.
        Auto-detects Activity/Module folders.
        """
        print("\n" + "=" * 70)
        print("🧩 Stage 2: Combining JSON to H5P")
        print("=" * 70)

        # Check for Activity/Module folders
        activity_folders = self._find_activity_folders()
        if not activity_folders:
            print("❌ No Activity/Module folders found")
            print("The batch converter should have created these folders.")
            return False

        print(f"\n📁 Found {len(activity_folders)} Activity/Module folder(s):")
        for folder in activity_folders:
            print(f"  • {folder.name}")

        print("\n🔄 Running H5P combiner...")
        try:
            result = subprocess.run(
                [sys.executable, "combine_h5p_auto.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if self.verbose or result.returncode != 0:
                print(result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)

            if result.returncode == 0:
                print("\n✅ Stage 2 Complete: H5P files generated!")
                self._list_generated_h5p_files()
                return True
            else:
                print(f"\n❌ Stage 2 Failed with return code: {result.returncode}")
                return False

        except Exception as e:
            print(f"❌ Error running H5P combiner: {e}")
            return False

    def stage_3_translate_content(self) -> bool:
        """
        Stage 3 (Optional): Translate content to other languages.
        Requires translations.py script.
        """
        print("\n" + "=" * 70)
        print("🌍 Stage 3: Translating Content (Optional)")
        print("=" * 70)

        if not self.translations_enabled:
            print("⏭️  Skipping translations (translations.py not found)")
            return True

        if not (self.project_root / "translations.py").exists():
            print("❌ translations.py not found")
            return False

        print("🔄 Running translation script...")
        try:
            result = subprocess.run(
                [sys.executable, "translations.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if self.verbose or result.returncode != 0:
                print(result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)

            if result.returncode == 0:
                print("\n✅ Stage 3 Complete: Translations generated!")
                return True
            else:
                print(f"\n⚠️  Stage 3 Warning: return code {result.returncode}")
                # Don't fail the pipeline for translations
                return True

        except Exception as e:
            print(f"⚠️  Warning: Could not run translations: {e}")
            return True  # Don't fail the entire pipeline

    def stage_4_create_manual_h5p(self) -> None:
        """
        Stage 4 (Bonus): Instructions for manual H5P creation from existing files.
        """
        print("\n" + "=" * 70)
        print("📦 Stage 4: Manual H5P Creation (Alternative Method)")
        print("=" * 70)

        print("""
If you already have a 'content' folder with 'content.json' and 'h5p.json' files,
you can manually create an H5P file by zipping the contents:

🖥️  macOS/Linux:
  1. Remove macOS metadata:
     find . -name '.DS_Store' -delete

  2. Create H5P file:
     zip -r -D -X project_el.h5p content h5p.json language/

📁 Expected structure:
  project_el.h5p
  ├── content/
  │   ├── content.json
  │   └── images/
  ├── h5p.json
  └── language/
      ├── el.json
      └── es.json

For more information, see the README.md file.
        """)

    def _find_activity_folders(self) -> List[Path]:
        """Find all folders containing 'Activity' or 'Module' in their names."""
        activity_folders = []
        for item in self.project_root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                name_lower = item.name.lower()
                if 'activity' in name_lower or 'module' in name_lower:
                    activity_folders.append(item)

        return sorted(activity_folders)

    def _list_generated_h5p_files(self) -> None:
        """List all generated H5P files."""
        h5p_files = list(self.project_root.glob("*.h5p"))
        if h5p_files:
            print("\n📦 Generated H5P files:")
            for h5p in h5p_files:
                size_mb = h5p.stat().st_size / (1024 * 1024)
                print(f"  • {h5p.name} ({size_mb:.2f} MB)")

    def run_full_pipeline(self, skip_translations: bool = False) -> bool:
        """
        Execute the complete pipeline.

        Args:
            skip_translations: Skip the translation stage

        Returns:
            True if all stages succeeded, False otherwise
        """
        print("\n")
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 15 + "🎓 H5P Content Pipeline Orchestrator" + " " * 17 + "║")
        print("╚" + "=" * 68 + "╝")

        # Environment setup
        if not self.setup_environment():
            return False

        # Stage 1: DOCX to JSON
        if not self.stage_1_convert_docx_to_json():
            return False

        # Stage 2: JSON to H5P
        if not self.stage_2_combine_json_to_h5p():
            return False

        # Stage 3: Translation (optional)
        if not skip_translations:
            self.stage_3_translate_content()

        # Stage 4: Manual H5P creation info
        self.stage_4_create_manual_h5p()

        # Final summary
        print("\n" + "=" * 70)
        print("✅ Pipeline Execution Complete!")
        print("=" * 70)
        print("""
📊 Pipeline Summary:
  ✓ Stage 1: DOCX → JSON conversion
  ✓ Stage 2: JSON → H5P combination
  ✓ Stage 3: Content translation (optional)
  ✓ Stage 4: Manual H5P creation guide

🎉 Your H5P files are ready for upload to:
  • Moodle
  • WordPress (with H5P plugin)
  • Canvas
  • Any other LMS with H5P support

📖 For more information, see README.md
        """)
        return True

    def run_stage(self, stage_num: int) -> bool:
        """Run a specific stage of the pipeline."""
        if stage_num == 1:
            return self.stage_1_convert_docx_to_json()
        elif stage_num == 2:
            if not self.stage_1_convert_docx_to_json():
                return False
            return self.stage_2_combine_json_to_h5p()
        elif stage_num == 3:
            return self.stage_3_translate_content()
        else:
            print(f"❌ Unknown stage: {stage_num}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="🎓 H5P Content Pipeline Orchestrator - Automate DOCX → JSON → H5P workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline
  python run_pipeline.py

  # Run only stage 1 (DOCX to JSON)
  python run_pipeline.py --stage 1

  # Run stages 1-2 (full conversion without translations)
  python run_pipeline.py --skip-translations

  # Verbose output
  python run_pipeline.py --verbose

For more information, see README.md
        """
    )

    parser.add_argument(
        "--stage",
        type=int,
        choices=[1, 2, 3],
        help="Run a specific stage (1=DOCX→JSON, 2=JSON→H5P, 3=Translate)"
    )

    parser.add_argument(
        "--skip-translations",
        action="store_true",
        help="Skip the translation stage"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show verbose output from subprocess commands"
    )

    args = parser.parse_args()

    # Create pipeline
    pipeline = H5PPipeline()
    pipeline.verbose = args.verbose

    # Run appropriate mode
    if args.stage:
        success = pipeline.run_stage(args.stage)
    else:
        success = pipeline.run_full_pipeline(skip_translations=args.skip_translations)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
