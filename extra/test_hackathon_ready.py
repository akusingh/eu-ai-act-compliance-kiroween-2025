#!/usr/bin/env python3
"""
Quick test to verify hackathon submission is ready
Checks all critical components without running full evaluation
"""

import sys
import os
from pathlib import Path

def print_status(check_name, passed, message=""):
    """Print colored status."""
    status = "✅" if passed else "❌"
    print(f"{status} {check_name}")
    if message:
        print(f"   {message}")
    return passed

def main():
    """Run all checks."""
    print("\n" + "="*70)
    print("🏆 KIROWEEN HACKATHON READINESS CHECK")
    print("="*70 + "\n")
    
    all_passed = True
    
    # Check 1: Python version
    print("📋 Checking Python version...")
    python_version = sys.version_info
    passed = python_version >= (3, 9)
    all_passed &= print_status(
        "Python 3.9+",
        passed,
        f"Found: {python_version.major}.{python_version.minor}"
    )
    
    # Check 2: Required files exist
    print("\n📁 Checking required files...")
    required_files = [
        "README.md",
        "LICENSE",
        "requirements.txt",
        "demo_hackathon.py",
        "web_demo.py",
        "evaluate.py",
        "quickstart.sh",
        "VIDEO_SCRIPT.md",
        "DEVPOST_SUBMISSION.md",
        "SUBMISSION_CHECKLIST.md",
        "KIRO_SHOWCASE.md",
        "PROJECT_STRUCTURE.md",
        "COMPETITION_READY.md"
    ]
    
    for file in required_files:
        exists = Path(file).exists()
        all_passed &= print_status(file, exists)
    
    # Check 3: Source code structure
    print("\n🔧 Checking source code...")
    src_files = [
        "src/config.py",
        "src/models.py",
        "src/sequential_orchestrator.py",
        "src/parallel_research_agents.py",
        "src/vector_index_tool.py",
        "src/tools_adk.py"
    ]
    
    for file in src_files:
        exists = Path(file).exists()
        all_passed &= print_status(file, exists)
    
    # Check 4: Environment setup
    print("\n🔐 Checking environment...")
    env_exists = Path(".env").exists()
    print_status(".env file", env_exists)
    
    if env_exists:
        with open(".env") as f:
            env_content = f.read()
            has_key = "GOOGLE_GENAI_API_KEY=" in env_content and len(env_content.split("GOOGLE_GENAI_API_KEY=")[1].split()[0]) > 10
            all_passed &= print_status("API key configured", has_key)
    else:
        print("   ⚠️  Create .env from .env.example and add your API key")
        all_passed = False
    
    # Check 5: Dependencies
    print("\n📦 Checking dependencies...")
    try:
        import google.adk
        print_status("google-adk", True)
    except ImportError:
        print_status("google-adk", False, "Run: pip install -r requirements.txt")
        all_passed = False
    
    try:
        import google.generativeai
        print_status("google-generativeai", True)
    except ImportError:
        print_status("google-generativeai", False, "Run: pip install -r requirements.txt")
        all_passed = False
    
    try:
        from flask import Flask
        print_status("flask", True)
    except ImportError:
        print_status("flask", False, "Run: pip install -r requirements.txt")
        all_passed = False
    
    # Check 6: Data files
    print("\n📚 Checking data files...")
    data_files = [
        "data/eu_act_recitals.txt",
        "data/eu_act_articles.txt",
        "data/eu_act_annexes.txt"
    ]
    
    data_ready = True
    for file in data_files:
        exists = Path(file).exists()
        data_ready &= exists
        print_status(file, exists)
    
    if not data_ready:
        print("   ⚠️  Run: bash scripts/download_eu_ai_act.sh")
    
    # Check 7: Vector indexes
    print("\n🔍 Checking vector indexes...")
    cache_dirs = [
        "data/embeddings_cache/recitals",
        "data/embeddings_cache/articles",
        "data/embeddings_cache/annexes"
    ]
    
    indexes_ready = True
    for dir_path in cache_dirs:
        exists = Path(dir_path).exists()
        indexes_ready &= exists
        print_status(dir_path, exists)
    
    if not indexes_ready:
        print("   ⚠️  Run: python scripts/build_vector_indexes.py")
    
    # Check 8: Test suite
    print("\n🧪 Checking test suite...")
    test_files = [
        "tests/test_models.py",
        "tests/test_tools.py",
        "tests/test_vector_index.py"
    ]
    
    for file in test_files:
        exists = Path(file).exists()
        print_status(file, exists)
    
    # Check 9: Kiro Integration
    print("\n🤖 Checking Kiro integration...")
    kiro_files = [
        ".kiro/steering/eu-ai-act-compliance.md",
        ".kiro/hooks/compliance-check-on-save.json",
        ".kiro/hooks/test-on-code-change.json",
        ".kiro/hooks/update-docs-on-structure-change.json",
        ".kiro/specs/add-new-regulation-support.md",
        ".kiro/README.md"
    ]
    
    kiro_ready = True
    for file in kiro_files:
        exists = Path(file).exists()
        kiro_ready &= exists
        print_status(file, exists)
    
    if not kiro_ready:
        print("   ⚠️  Kiro integration incomplete - required for competition!")
    
    # Check 10: Documentation
    print("\n📖 Checking documentation...")
    
    # Check README has hackathon badge
    with open("README.md") as f:
        readme = f.read()
        has_badge = "Kiroween" in readme
        print_status("README has Kiroween badge", has_badge)
        
        has_quickstart = "quickstart.sh" in readme
        print_status("README has quickstart", has_quickstart)
        
        has_kiro_section = "Kiro Integration" in readme
        print_status("README mentions Kiro integration", has_kiro_section)
    
    # Check LICENSE exists
    license_exists = Path("LICENSE").exists()
    print_status("LICENSE file (open source requirement)", license_exists)
    if not license_exists:
        print("   ⚠️  Add LICENSE file (MIT, Apache 2.0, etc.)")
    
    # Summary
    print("\n" + "="*70)
    if all_passed and data_ready and indexes_ready and kiro_ready:
        print("🎉 ALL CHECKS PASSED - READY FOR SUBMISSION!")
        print("="*70)
        print("\n✅ Competition Requirements Met:")
        print("   ✓ Kiro integration (.kiro/ directory)")
        print("   ✓ Open source license (LICENSE file)")
        print("   ✓ Working demos (terminal + web)")
        print("   ✓ Comprehensive documentation")
        print("\n📋 Next Steps:")
        print("1. Record video demo <3 minutes (use VIDEO_SCRIPT.md)")
        print("2. Upload video to YouTube/Vimeo")
        print("3. Take screenshots (terminal, web UI, architecture)")
        print("4. Make GitHub repo public")
        print("5. Fill out Devpost submission (use DEVPOST_SUBMISSION.md)")
        print("6. Test demos one more time:")
        print("   - python demo_hackathon.py")
        print("   - python web_demo.py")
        print("7. Submit before deadline!")
        print("\n🏆 Good luck!")
        return 0
    else:
        print("⚠️  SOME CHECKS FAILED - FIX BEFORE SUBMISSION")
        print("="*70)
        print("\n📋 To Fix:")
        if not all_passed:
            print("- Install missing dependencies: pip install -r requirements.txt")
        if not data_ready:
            print("- Download EU AI Act data: bash scripts/download_eu_ai_act.sh")
        if not indexes_ready:
            print("- Build vector indexes: python scripts/build_vector_indexes.py")
        if not kiro_ready:
            print("- Kiro integration incomplete (CRITICAL for competition!)")
            print("  Check .kiro/ directory has all required files")
        print("\nThen run this script again: python test_hackathon_ready.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
