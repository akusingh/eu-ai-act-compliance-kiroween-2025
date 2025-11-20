#!/usr/bin/env python3
"""
Build 3 separate vector indexes for parallel EU AI Act search:
1. Recitals index (context and intent)
2. Articles index (legal requirements)
3. Annexes index (specific lists and details)

Each index uses Gemini embeddings + BM25 with caching.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.vector_index_tool import VectorIndexTool
from src.config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def build_all_indexes():
    """Build vector indexes for all 3 EU AI Act sources."""
    
    print("=" * 70)
    print("EU AI ACT - VECTOR INDEX BUILDER")
    print("Building 3 separate indexes for parallel search")
    print("=" * 70)
    
    # Check API key
    if not Config.GOOGLE_GENAI_API_KEY:
        print("\n❌ ERROR: GOOGLE_GENAI_API_KEY not set")
        print("Please configure your Gemini API key in .env file")
        print("Example: GOOGLE_GENAI_API_KEY=your_key_here")
        return False
    
    print(f"\n✓ Gemini API key configured")
    
    # Define sources
    sources = [
        {
            "name": "Recitals",
            "description": "Context, intent, and definitions (1-180)",
            "path": str(project_root / "data" / "eu_act_recitals.txt"),
            "cache_dir": str(project_root / "data" / "embeddings_cache" / "recitals")
        },
        {
            "name": "Articles",
            "description": "Legal requirements and obligations (1-113)",
            "path": str(project_root / "data" / "eu_act_articles.txt"),
            "cache_dir": str(project_root / "data" / "embeddings_cache" / "articles")
        },
        {
            "name": "Annexes",
            "description": "Specific lists and technical details (I-XIII)",
            "path": str(project_root / "data" / "eu_act_annexes.txt"),
            "cache_dir": str(project_root / "data" / "embeddings_cache" / "annexes")
        }
    ]
    
    # Build each index
    results = []
    for i, source in enumerate(sources, 1):
        print(f"\n{'='*70}")
        print(f"[{i}/3] Building index: {source['name']}")
        print(f"Description: {source['description']}")
        print(f"Source: {source['path']}")
        print(f"Cache: {source['cache_dir']}")
        print(f"{'='*70}\n")
        
        try:
            # Check if source file exists
            if not Path(source['path']).exists():
                print(f"❌ ERROR: Source file not found: {source['path']}")
                print("Run: python3 scripts/split_eu_ai_act.py")
                results.append({"name": source['name'], "success": False})
                continue
            
            # Build index
            logger.info(f"Initializing VectorIndexTool for {source['name']}...")
            tool = VectorIndexTool(
                eu_act_text_path=source['path'],
                cache_dir=source['cache_dir']
            )
            
            # Check if index was built
            if tool.chunks and tool.embeddings:
                print(f"\n✓ {source['name']} index built successfully!")
                print(f"  - Chunks: {len(tool.chunks)}")
                print(f"  - Embeddings: {len(tool.embeddings)}")
                print(f"  - BM25: {'✓' if tool.bm25 else '✗'}")
                results.append({"name": source['name'], "success": True, "chunks": len(tool.chunks)})
            else:
                print(f"\n❌ {source['name']} index build failed")
                results.append({"name": source['name'], "success": False})
        
        except Exception as e:
            logger.error(f"Failed to build {source['name']} index: {e}", exc_info=True)
            print(f"\n❌ {source['name']} index build failed: {e}")
            results.append({"name": source['name'], "success": False})
    
    # Summary
    print("\n" + "=" * 70)
    print("BUILD SUMMARY")
    print("=" * 70)
    
    success_count = sum(1 for r in results if r.get("success"))
    
    for result in results:
        status = "✓" if result.get("success") else "✗"
        chunks = f"({result.get('chunks', 0)} chunks)" if result.get("success") else ""
        print(f"  {status} {result['name']} {chunks}")
    
    print(f"\nTotal: {success_count}/3 indexes built successfully")
    
    if success_count == 3:
        print("\n🎉 All indexes ready for parallel search!")
        print("\nNext steps:")
        print("  1. Test parallel search: python3 -c \"from src.vector_index_tool import VectorIndexTool; ...\"")
        print("  2. Run demo: python3 demo.py")
        return True
    else:
        print("\n⚠ Some indexes failed to build. Check errors above.")
        return False


if __name__ == "__main__":
    success = build_all_indexes()
    exit(0 if success else 1)
